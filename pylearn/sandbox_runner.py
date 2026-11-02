"""Child-process side of the sandbox.  NEVER import this module in the app.

It is executed as a separate Python process by :mod:`pylearn.sandbox`:

    python -E pylearn/sandbox_runner.py   (request JSON on stdin)

Layers of protection applied here, in order:

1. OS resource limits (CPU seconds, memory, file size, open files).
2. Heavy libraries the learner is allowed to use (pandas, matplotlib, ...)
   are imported *before* the policy is switched on.
3. A PEP 578 audit hook (which cannot be removed once installed) blocks:
   process creation, networking, ctypes, importing dangerous modules,
   and any file write / delete / rename outside the private temp directory,
   and file reads outside the temp dir and the Python installation.
4. The parent process also runs the child with a wall-clock timeout, a
   scrubbed environment and an empty temporary working directory.

The result is written as a single JSON line prefixed with a per-run nonce to
the *original* stdout file descriptor, while the learner's prints go into a
buffer.
"""

import base64
import io
import json
import math
import os
import sys
import traceback

# Do not let the runner's own directory (the pylearn package) be importable.
if sys.path and os.path.abspath(sys.path[0]) == os.path.dirname(os.path.abspath(__file__)):
    sys.path.pop(0)

MAX_OUTPUT_CHARS = 20_000
MAX_FIGURES = 4

BLOCKED_MODULES = {
    "subprocess", "_posixsubprocess", "socket", "_socket", "ssl", "ctypes",
    "_ctypes", "multiprocessing", "_multiprocessing", "concurrent",
    "urllib.request", "http.client", "http.server", "ftplib", "smtplib",
    "telnetlib", "poplib", "imaplib", "xmlrpc", "socketserver", "asyncio",
    "pty", "webbrowser", "requests", "urllib3", "httpx", "aiohttp",
    "signal", "resource", "pickle", "_pickle", "marshal", "shelve",
    "importlib.util", "zipimport", "code", "codeop", "pdb", "faulthandler",
    "tkinter", "turtle", "winreg", "_winapi", "msvcrt", "mmap", "fcntl",
}

DENY_EVENTS_PREFIX = (
    "subprocess.", "os.system", "os.exec", "os.spawn", "os.posix_spawn",
    "os.fork", "os.forkpty", "os.kill", "os.killpg", "os.chdir", "os.chroot",
    "os.setuid", "os.setgid", "socket.", "ctypes.", "pty.", "webbrowser.",
    "urllib.Request", "ftplib.", "smtplib.", "telnetlib.", "imaplib.",
    "poplib.", "http.client.", "sqlite3.enable_load_extension",
    "sqlite3.load_extension", "os.symlink", "os.link", "os.chown",
    "os.chflags", "os.lchown", "os.lchflags", "os.lchmod", "os.startfile",
    "winreg.", "msvcrt.", "_winapi.", "mmap.", "fcntl.", "resource.",
    "sys.setrecursionlimit", "os.setxattr", "os.removexattr",
    "sys.remote_exec",
)

PRELOAD_MODULES = (
    "sqlite3", "csv", "json", "math", "statistics", "random", "datetime",
    "collections", "string", "re", "itertools", "functools", "pathlib", "decimal",
    "fractions", "textwrap", "pprint", "operator", "copy", "inspect", "gc",
)

PATH_WRITE_EVENTS = {
    "os.remove", "os.rmdir", "os.mkdir", "os.rename", "os.truncate",
    "os.chmod", "os.utime", "shutil.copyfile", "shutil.copymode",
    "shutil.copystat", "shutil.copytree", "shutil.move", "shutil.rmtree",
    "shutil.make_archive", "shutil.unpack_archive",
}
PATH_READ_EVENTS = {"os.listdir", "os.scandir", "glob.glob", "os.walk"}


def _set_limits(req):
    try:
        import resource
    except ImportError:  # Windows: no rlimits available (documented limitation)
        return
    cpu = int(req.get("cpu_seconds", 5))
    mem = int(req.get("memory_mb", 1536)) * 1024 * 1024
    limits = [
        (resource.RLIMIT_CPU, (cpu, cpu + 1)),
        (resource.RLIMIT_FSIZE, (5 * 1024 * 1024, 5 * 1024 * 1024)),
        (resource.RLIMIT_NOFILE, (256, 256)),
        (resource.RLIMIT_CORE, (0, 0)),
    ]
    if hasattr(resource, "RLIMIT_AS"):
        limits.append((resource.RLIMIT_AS, (mem, mem)))
    for which, value in limits:
        try:
            resource.setrlimit(which, value)
        except (ValueError, OSError):
            pass


def _preload(req):
    """Import allowed heavy libraries before the policy is active."""
    import importlib
    import warnings
    # Standard-library modules learners may use. Importing them now means
    # their own internal file reads happen before the policy is switched on.
    for name in PRELOAD_MODULES:
        importlib.import_module(name)
    warnings.simplefilter("ignore")
    text = req.get("code", "") + req.get("prelude", "") + req.get("setup", "")
    text += " ".join(c.get("expr") or "" for c in req.get("checks", []))
    if "numpy" in text or "np." in text or "pandas" in text or "pd." in text \
            or "matplotlib" in text or "plt" in text:
        importlib.import_module("numpy")
        if "pandas" in text or "pd." in text:
            importlib.import_module("pandas")
        if "matplotlib" in text or "plt" in text:
            import matplotlib
            matplotlib.use("Agg")
            import matplotlib.pyplot as plt
            plt.show = lambda *a, **k: None  # figures are captured instead
            # Warm up the text renderer so fonts are loaded pre-policy.
            fig = plt.figure()
            fig.text(0.5, 0.5, "warm-up 0123")
            fig.canvas.draw()
            plt.close(fig)


def _install_policy(workdir, read_roots):
    workdir = os.path.realpath(workdir)
    read_roots = tuple(os.path.realpath(r) for r in read_roots if r)

    def inside(path, roots):
        try:
            if isinstance(path, int):
                return True  # already-open file descriptor
            if isinstance(path, bytes):
                path = path.decode(errors="replace")
            p = os.path.realpath(os.fspath(path))
        except Exception:
            return False
        return any(p == r or p.startswith(r + os.sep) for r in roots)

    def deny(msg):
        raise PermissionError(f"Sandbox: {msg} is not allowed in the learning sandbox.")

    def hook(event, args):
        if event == "import":
            name = args[0] or ""
            top = name.split(".")[0]
            if name in BLOCKED_MODULES or top in BLOCKED_MODULES:
                raise ImportError(
                    f"Sandbox: the module '{name}' is disabled in the learning sandbox."
                )
            return
        if event.startswith(DENY_EVENTS_PREFIX):
            deny(f"'{event}'")
        if event == "open":
            path, mode = args[0], args[1]
            flags = args[2] if len(args) > 2 else 0
            if path is None:
                return
            if isinstance(path, int):
                if path <= 2:
                    deny("opening the console streams directly")
                return
            writing = (isinstance(mode, str) and any(c in mode for c in "wax+")) or (
                isinstance(flags, int) and flags & (os.O_WRONLY | os.O_RDWR | os.O_CREAT)
            )
            if writing:
                if not inside(path, (workdir,)):
                    deny(f"writing to '{path}' (only files in the current folder can be written)")
            elif not inside(path, (workdir,) + read_roots):
                deny(f"reading '{path}' (only files in the current folder can be read)")
        elif event in PATH_WRITE_EVENTS:
            for a in args:
                if isinstance(a, (str, bytes, os.PathLike)) and not inside(a, (workdir,)):
                    deny(f"'{event}' outside the current folder")
        elif event in PATH_READ_EVENTS:
            if args and isinstance(args[0], (str, bytes, os.PathLike)):
                if not inside(args[0], (workdir,) + read_roots):
                    deny(f"listing '{args[0]}'")
        elif event == "sqlite3.connect":
            db = args[0] if args else ":memory:"
            if db not in (":memory:", b":memory:", "") and not inside(db, (workdir,)):
                deny(f"opening database '{db}' outside the current folder")

    sys.addaudithook(hook)


def _to_jsonable(value, depth=0):
    """Convert results to JSON-compatible values for comparison."""
    if depth > 20:
        return repr(value)
    if value is None or isinstance(value, (bool, int, str)):
        return value
    if isinstance(value, float):
        if math.isnan(value):
            return "NaN"
        return value
    if isinstance(value, (list, tuple)):
        return [_to_jsonable(v, depth + 1) for v in value]
    if isinstance(value, (set, frozenset)):
        try:
            return sorted(_to_jsonable(v, depth + 1) for v in value)
        except TypeError:
            return [_to_jsonable(v, depth + 1) for v in value]
    if isinstance(value, dict):
        return {str(k): _to_jsonable(v, depth + 1) for k, v in value.items()}
    item = getattr(value, "item", None)  # numpy scalars
    if callable(item) and type(value).__module__ == "numpy":
        try:
            return _to_jsonable(value.item(), depth + 1)
        except Exception:
            pass
    tolist = getattr(value, "tolist", None)  # numpy arrays / pandas Series
    if callable(tolist):
        try:
            return _to_jsonable(tolist(), depth + 1)
        except Exception:
            pass
    return repr(value)


def _equal(actual, expected, tol):
    if isinstance(expected, bool) or isinstance(actual, bool):
        return actual is expected or actual == expected and type(actual) is type(expected)
    if isinstance(expected, (int, float)) and isinstance(actual, (int, float)):
        return math.isclose(actual, expected, rel_tol=tol, abs_tol=tol)
    if isinstance(expected, list) and isinstance(actual, list):
        return len(actual) == len(expected) and all(
            _equal(a, e, tol) for a, e in zip(actual, expected)
        )
    if isinstance(expected, dict) and isinstance(actual, dict):
        return actual.keys() == expected.keys() and all(
            _equal(actual[k], expected[k], tol) for k in expected
        )
    return actual == expected


def _short_repr(value, limit=300):
    try:
        text = repr(value)
    except Exception:
        text = "<unprintable value>"
    return text if len(text) <= limit else text[:limit] + " ..."


def _error_info(exc, filename="<your code>"):
    tb = traceback.extract_tb(exc.__traceback__)
    line = None
    for frame in tb:
        if frame.filename == filename:
            line = frame.lineno
    if isinstance(exc, SyntaxError) and exc.filename == filename:
        line = exc.lineno
    lines = traceback.format_exception_only(type(exc), exc)
    # Keep only the frames from the learner's code: they do not need to see
    # the sandbox's internals.
    user_frames = [f for f in tb if f.filename == filename]
    pretty = "Traceback (most recent call last):\n" if user_frames else ""
    for f in user_frames:
        pretty += f'  File "{filename}", line {f.lineno}\n'
        if f.line:
            pretty += f"    {f.line}\n"
    pretty += "".join(lines)
    return {
        "type": type(exc).__name__,
        "message": str(exc),
        "line": line,
        "traceback": pretty,
    }


class _LimitedWriter(io.StringIO):
    def write(self, s):
        if self.tell() > MAX_OUTPUT_CHARS:
            return len(s)
        return super().write(s)


def main():
    real_stdout = sys.stdout
    req = json.loads(sys.stdin.read())
    nonce = req["nonce"]
    workdir = os.getcwd()

    _set_limits(req)
    result = {"ok": True, "stdout": "", "error": None, "checks": [], "figures": [],
              "truncated": False, "setup_error": None}
    try:
        _preload(req)
    except Exception as exc:  # pragma: no cover - only on broken installs
        result["setup_error"] = f"Could not load libraries: {exc!r}"

    read_roots = [sys.prefix, sys.base_prefix, sys.exec_prefix,
                  os.path.dirname(os.__file__)]
    read_roots += [p for p in sys.path if p and os.path.isdir(p)]
    read_roots += [req.get("mpl_dir") or ""]
    _install_policy(workdir, read_roots)

    namespace = {"__name__": "__main__", "__builtins__": __builtins__}
    out = _LimitedWriter()
    sys.stdin = io.StringIO(req.get("stdin", ""))

    def run_trusted(src, label):
        """Run setup/prelude code with output discarded."""
        sink = io.StringIO()
        sys.stdout = sink
        sys.stderr = sink
        try:
            exec(compile(src, label, "exec"), namespace)
        finally:
            sys.stdout = out
            sys.stderr = out

    sys.stdout = out
    sys.stderr = out
    try:
        if req.get("setup"):
            run_trusted(req["setup"], "<setup>")
        if req.get("prelude"):
            run_trusted(req["prelude"], "<prelude>")
    except BaseException as exc:  # noqa: BLE001
        result["setup_error"] = _error_info(exc, "<prelude>")["traceback"]

    import linecache
    user_code = req.get("code", "")
    linecache.cache["<your code>"] = (len(user_code), None,
                                      user_code.splitlines(True), "<your code>")
    try:
        code_obj = compile(user_code, "<your code>", "exec")
        exec(code_obj, namespace)
    except SystemExit:
        pass
    except BaseException as exc:  # noqa: BLE001 - we report every failure
        result["ok"] = False
        result["error"] = _error_info(exc)

    main_stdout = out.getvalue()

    for check in req.get("checks", []):
        rec = {"description": check.get("description", ""), "passed": False,
               "actual": None, "expected": None, "error": None,
               "printed": "", "actual_is_none": False}
        try:
            if check.get("expr"):
                buf = io.StringIO()
                sys.stdout = buf
                try:
                    value = eval(compile(check["expr"], "<check>", "eval"), namespace)
                finally:
                    sys.stdout = out
                rec["printed"] = buf.getvalue()[:500]
                rec["actual_is_none"] = value is None
                actual = _to_jsonable(value)
                expected = check.get("expected")
                rec["passed"] = _equal(actual, expected, float(check.get("tolerance") or 1e-6))
                rec["actual"] = _short_repr(value)
                rec["expected"] = _short_repr(expected)
            elif check.get("stdout_equals") is not None:
                want = check["stdout_equals"].strip()
                got = "\n".join(l.rstrip() for l in main_stdout.strip().splitlines())
                rec["passed"] = got == want
                rec["actual"] = got[:500]
                rec["expected"] = want
            elif check.get("stdout_contains") is not None:
                rec["passed"] = check["stdout_contains"] in main_stdout
                rec["expected"] = check["stdout_contains"]
                rec["actual"] = main_stdout[:500]
            elif check.get("figure"):
                import matplotlib.pyplot as plt
                rec["passed"] = len(plt.get_fignums()) > 0
                rec["expected"] = "at least one chart"
                rec["actual"] = f"{len(plt.get_fignums())} chart(s)"
        except BaseException as exc:  # noqa: BLE001
            sys.stdout = out
            info = _error_info(exc, "<check>")
            rec["error"] = f"{info['type']}: {info['message']}"
        result["checks"].append(rec)

    sys.stdout = real_stdout
    sys.stderr = sys.__stderr__

    if "matplotlib.pyplot" in sys.modules:
        plt = sys.modules["matplotlib.pyplot"]
        for num in plt.get_fignums()[:MAX_FIGURES]:
            try:
                buf = io.BytesIO()
                plt.figure(num).savefig(buf, format="png", dpi=90, bbox_inches="tight")
                result["figures"].append(base64.b64encode(buf.getvalue()).decode())
            except Exception:
                pass

    result["stdout"] = main_stdout[:MAX_OUTPUT_CHARS]
    result["truncated"] = len(main_stdout) >= MAX_OUTPUT_CHARS
    real_stdout.write("\n" + nonce + json.dumps(result, default=repr) + "\n")
    real_stdout.flush()


if __name__ == "__main__":
    main()
