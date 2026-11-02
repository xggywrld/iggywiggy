"""Safe(ish) execution of learner code.

Learner code is never executed inside the Streamlit process. Instead:

1. :func:`static_check` parses the code with :mod:`ast` and rejects obviously
   dangerous constructs (``__import__``, ``eval``, dunder escapes, blocked
   modules) with a friendly message *before* anything runs.
2. :func:`run_code` launches a fresh Python interpreter (``sandbox_runner.py``)
   in an empty temporary directory, with a scrubbed environment, a wall-clock
   timeout, CPU/memory/file-size limits and an audit-hook policy that blocks
   processes, networking and file access outside that directory.

See README "Sandbox security model" for the limitations of this approach.
"""

from __future__ import annotations

import ast
import base64
import json
import os
import secrets
import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, Optional

RUNNER = Path(__file__).with_name("sandbox_runner.py")
DEFAULT_TIMEOUT = 10.0
MAX_CODE_CHARS = 20_000

BLOCKED_IMPORTS = {
    "subprocess", "socket", "ctypes", "multiprocessing", "asyncio", "ssl",
    "urllib", "http", "ftplib", "smtplib", "telnetlib", "requests", "pty",
    "webbrowser", "signal", "resource", "pickle", "marshal", "shelve",
    "importlib", "code", "codeop", "pdb", "concurrent", "socketserver",
    "xmlrpc", "tkinter", "turtle", "mmap", "fcntl", "shutil", "sys",
    "builtins", "gc", "inspect", "faulthandler", "threading", "_thread",
}
BLOCKED_CALLS = {"eval", "exec", "compile", "__import__", "breakpoint",
                 "globals", "vars", "getattr", "setattr", "delattr"}
BLOCKED_ATTRS_PREFIX = "__"
ALLOWED_DUNDERS = {"__init__", "__name__", "__str__", "__repr__", "__len__",
                   "__main__", "__doc__", "__eq__", "__lt__", "__add__",
                   "__dict__", "__class__"}

FRIENDLY_SANDBOX_NOTE = (
    "The learning sandbox switches off a few features that could harm your "
    "computer (running other programs, the internet, reading system files). "
    "Everything you need for this course still works."
)


@dataclass
class CheckResult:
    description: str
    passed: bool
    actual: Optional[str] = None
    expected: Optional[str] = None
    error: Optional[str] = None
    printed: str = ""
    actual_is_none: bool = False


@dataclass
class RunResult:
    ok: bool
    stdout: str = ""
    error: Optional[dict] = None  # {"type","message","line","traceback"}
    checks: list[CheckResult] = field(default_factory=list)
    figures: list[bytes] = field(default_factory=list)  # PNG bytes
    timed_out: bool = False
    blocked: Optional[str] = None  # static-policy rejection message
    truncated: bool = False
    setup_error: Optional[str] = None

    @property
    def all_checks_passed(self) -> bool:
        return self.ok and bool(self.checks) and all(c.passed for c in self.checks)


def _mpl_cache_dir() -> str:
    base = Path(os.environ.get("PYLEARN_DATA_DIR", Path.home() / ".pylearn"))
    path = base / "mplcache"
    try:
        path.mkdir(parents=True, exist_ok=True)
    except OSError:
        path = Path(tempfile.gettempdir()) / "pylearn-mplcache"
        path.mkdir(parents=True, exist_ok=True)
    return str(path)


def static_check(code: str) -> Optional[str]:
    """Return a friendly rejection message, or ``None`` if the code may run.

    Syntax errors are *not* rejected here: they are reported by the real
    interpreter so learners see authentic error messages.
    """
    if len(code) > MAX_CODE_CHARS:
        return f"Your code is very long (over {MAX_CODE_CHARS} characters). Please shorten it."
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return None
    except (ValueError, MemoryError, RecursionError):
        return "This code could not be read safely (it may be too deeply nested)."
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                top = alias.name.split(".")[0]
                if top in BLOCKED_IMPORTS:
                    return (f"`import {alias.name}` is disabled in the sandbox. "
                            + FRIENDLY_SANDBOX_NOTE)
        elif isinstance(node, ast.ImportFrom):
            top = (node.module or "").split(".")[0]
            if top in BLOCKED_IMPORTS:
                return (f"`from {node.module} import ...` is disabled in the sandbox. "
                        + FRIENDLY_SANDBOX_NOTE)
            if top == "os" and any(a.name in {"system", "popen", "fork", "execv",
                                              "execl", "spawnl", "kill"}
                                   for a in node.names):
                return "Running other programs is disabled in the sandbox."
        elif isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            if node.func.id in BLOCKED_CALLS:
                return (f"`{node.func.id}()` is disabled in the sandbox because it "
                        "can be used to escape its safety rules.")
        elif isinstance(node, ast.Attribute):
            if node.attr.startswith(BLOCKED_ATTRS_PREFIX) and node.attr not in ALLOWED_DUNDERS:
                return (f"Accessing `{node.attr}` is disabled in the sandbox. "
                        "You won't need it for this course.")
            if node.attr in {"system", "popen", "fork", "execv", "execve", "spawnv",
                             "kill", "_getframe", "f_globals", "f_back", "gi_frame",
                             "tb_frame", "cr_frame"}:
                return f"Using `.{node.attr}` is disabled in the sandbox."
        elif isinstance(node, ast.Name) and node.id in {"__builtins__", "__loader__",
                                                        "__spec__"}:
            return f"Accessing `{node.id}` is disabled in the sandbox."
    return None


def run_code(
    code: str,
    *,
    stdin: str = "",
    checks: Iterable = (),
    setup: str = "",
    prelude: str = "",
    timeout: float = DEFAULT_TIMEOUT,
    cpu_seconds: int = 8,
    memory_mb: int = 1536,
) -> RunResult:
    """Run learner ``code`` in an isolated child interpreter.

    ``setup`` and ``prelude`` are *trusted* course code (e.g. creating a
    dataset) that runs first, with its output hidden. ``checks`` is an
    iterable of :class:`~pylearn.content.models.Check` (or payload dicts).
    """
    blocked = static_check(code)
    if blocked:
        return RunResult(ok=False, blocked=blocked)

    payload_checks = [c.to_payload() if hasattr(c, "to_payload") else dict(c) for c in checks]
    nonce = "@@PYLEARN-" + secrets.token_hex(16) + "@@"
    request = {
        "nonce": nonce,
        "code": code,
        "stdin": stdin,
        "checks": payload_checks,
        "setup": setup,
        "prelude": prelude,
        "cpu_seconds": cpu_seconds,
        "memory_mb": memory_mb,
        "mpl_dir": _mpl_cache_dir(),
    }
    env = {
        "PATH": os.environ.get("PATH", "/usr/bin:/bin"),
        "PYTHONIOENCODING": "utf-8",
        "PYTHONDONTWRITEBYTECODE": "1",
        "MPLBACKEND": "Agg",
        "MPLCONFIGDIR": request["mpl_dir"],
        "OPENBLAS_NUM_THREADS": "1",
        "OMP_NUM_THREADS": "1",
        "MKL_NUM_THREADS": "1",
        "LANG": "C.UTF-8",
    }
    if os.name == "nt":  # Windows needs these to start Python at all.
        for key in ("SYSTEMROOT", "TEMP", "TMP"):
            if key in os.environ:
                env[key] = os.environ[key]

    with tempfile.TemporaryDirectory(prefix="pylearn-sbx-") as workdir:
        env["HOME"] = workdir
        try:
            proc = subprocess.run(
                [sys.executable, "-E", "-X", "utf8", str(RUNNER)],
                input=json.dumps(request),
                capture_output=True,
                text=True,
                cwd=workdir,
                env=env,
                timeout=timeout,
                encoding="utf-8",
                errors="replace",
            )
        except subprocess.TimeoutExpired:
            return RunResult(
                ok=False,
                timed_out=True,
                error={
                    "type": "TimeoutError",
                    "message": f"Your code took longer than {timeout:.0f} seconds.",
                    "line": None,
                    "traceback": "",
                },
            )

    return _parse_output(proc, nonce)


def _parse_output(proc: subprocess.CompletedProcess, nonce: str) -> RunResult:
    marker_line = None
    for line in reversed(proc.stdout.splitlines()):
        if line.startswith(nonce):
            marker_line = line[len(nonce):]
            break
    if marker_line is None:
        # The child died before reporting: CPU limit, memory limit, crash.
        stderr = proc.stderr.strip()
        if proc.returncode in (-24, 152) or "CPU" in stderr:  # SIGXCPU
            etype, msg = "TimeoutError", "Your code used too much processing time (is there an infinite loop?)."
        elif "MemoryError" in stderr or proc.returncode in (-9, 137):
            etype, msg = "MemoryError", "Your code used too much memory."
        else:
            etype, msg = "SandboxError", (
                "The sandbox stopped unexpectedly." + (f"\n{stderr[-800:]}" if stderr else "")
            )
        return RunResult(ok=False, timed_out=etype == "TimeoutError",
                         error={"type": etype, "message": msg, "line": None, "traceback": ""})

    data = json.loads(marker_line)
    return RunResult(
        ok=data["ok"],
        stdout=data.get("stdout", ""),
        error=data.get("error"),
        checks=[CheckResult(**c) for c in data.get("checks", [])],
        figures=[base64.b64decode(f) for f in data.get("figures", [])],
        truncated=data.get("truncated", False),
        setup_error=data.get("setup_error"),
    )
