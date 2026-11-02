"""Security and behaviour tests for the code sandbox."""

import pytest

from pylearn.content.models import Check
from pylearn.sandbox import run_code, static_check


def test_basic_output_and_stdin():
    r = run_code("name = input()\nprint('hi', name)", stdin="Ada\n")
    assert r.ok and r.stdout == "hi Ada\n"


def test_runtime_error_reported_with_line():
    r = run_code("x = 1\ny = x / 0")
    assert not r.ok
    assert r.error["type"] == "ZeroDivisionError"
    assert r.error["line"] == 2
    assert "y = x / 0" in r.error["traceback"]
    assert "sandbox_runner" not in r.error["traceback"]  # internals hidden


def test_syntax_error_reported():
    r = run_code("if True\n    print(1)")
    assert r.error["type"] == "SyntaxError"


def test_files_work_inside_private_folder():
    r = run_code("open('a.txt', 'w').write('x')\nprint(open('a.txt').read())")
    assert r.ok and r.stdout.strip() == "x"


def test_each_run_gets_a_fresh_folder():
    run_code("open('leftover.txt', 'w').write('x')")
    r = run_code("open('leftover.txt')")
    assert r.error["type"] == "FileNotFoundError"


@pytest.mark.parametrize("code", [
    "open('/etc/passwd').read()",
    "open('/etc/hostname')",
    "open('../escape.txt', 'w')",
    "open('/tmp/pylearn-test-escape.txt', 'w')",
])
def test_file_access_outside_folder_blocked(code):
    r = run_code(code)
    assert not r.ok
    assert r.error["type"] == "PermissionError"
    assert "Sandbox" in r.error["message"]


@pytest.mark.parametrize("code", [
    "import os\nos.listdir('/')",
    "import os\nos.remove('/tmp/x')",
    "import pathlib\nprint(list(pathlib.Path('/').iterdir()))",
    "import sqlite3\nsqlite3.connect('/tmp/evil.db')",
])
def test_os_level_escapes_blocked(code):
    r = run_code(code)
    assert not r.ok and r.error["type"] == "PermissionError"


@pytest.mark.parametrize("code", [
    "import subprocess",
    "import socket",
    "import ctypes",
    "from os import system",
    "import os\nos.system('echo hi')",
    "__import__('subprocess')",
    "eval('1+1')",
    "exec('print(1)')",
    "().__class__.__bases__[0].__subclasses__()",
    "print(__builtins__)",
    "getattr(object, 'x')",
    "import sys",
    "import importlib",
])
def test_static_policy_blocks(code):
    assert static_check(code) is not None
    r = run_code(code)
    assert r.blocked and not r.ok


def test_runtime_policy_blocks_process_creation_even_if_static_check_bypassed():
    # `os.popen` isn't in the static blocklist via attribute name `popen`? It is;
    # use a less obvious route: os.posix_spawn via a dict lookup.
    code = "import os\nf = os.__dict__['posix_spawn']\nf('/bin/echo', ['echo'], {})"
    r = run_code(code)
    assert not r.ok
    assert r.error["type"] == "PermissionError"


def test_runtime_policy_blocks_dynamic_import_of_network_modules():
    code = "import json\nm = json.__dict__\nimport http"
    r = run_code(code)
    assert r.blocked  # http is statically blocked
    code = "import os\nos.__dict__['system']('echo pwned')"
    r = run_code(code)
    assert not r.ok and "pwned" not in r.stdout


def test_console_streams_cannot_be_reopened():
    r = run_code("open(1, 'w').write('spoof')")
    assert not r.ok and r.error["type"] == "PermissionError"


def test_fake_result_marker_does_not_confuse_parser():
    r = run_code('print(\'@@PYLEARN-0000@@{"ok": true, "stdout": "fake"}\')\nraise ValueError("real")')
    assert not r.ok and r.error["type"] == "ValueError"


def test_infinite_loop_times_out():
    r = run_code("while True:\n    pass", timeout=3)
    assert r.timed_out and r.error["type"] == "TimeoutError"


def test_memory_limit():
    r = run_code("x = bytearray(4 * 1024 ** 3)", memory_mb=1024)
    assert not r.ok
    assert r.error["type"] == "MemoryError"


def test_output_is_truncated():
    r = run_code("for i in range(100000):\n    print('line', i)")
    assert r.ok and r.truncated and len(r.stdout) <= 20_000


def test_checks_and_print_vs_return_detection():
    code = "def double(n):\n    print(n * 2)"
    r = run_code(code, checks=[Check("double(4) == 8", expr="double(4)", expected=8)])
    c = r.checks[0]
    assert not c.passed and c.actual_is_none and c.printed.strip() == "8"


def test_checks_compare_tuples_lists_numpy_and_tolerance():
    code = ("import numpy as np\nt = (1, 2)\nf = 0.1 + 0.2\nn = np.int64(5)\n"
            "d = {'a': (1, 2.0)}")
    checks = [Check("t", expr="t", expected=[1, 2]), Check("f", expr="f", expected=0.3),
              Check("n", expr="n", expected=5), Check("d", expr="d", expected={"a": [1, 2]}),
              Check("bool is not int", expr="True", expected=1)]
    r = run_code(code, checks=checks)
    assert [c.passed for c in r.checks] == [True, True, True, True, False]


def test_stdout_checks():
    r = run_code("print('a')\nprint('b')  ", checks=[
        Check("eq", stdout_equals="a\nb"), Check("contains", stdout_contains="b"),
        Check("no", stdout_equals="a")])
    assert [c.passed for c in r.checks] == [True, True, False]


def test_figures_captured():
    code = "import matplotlib.pyplot as plt\nfig, ax = plt.subplots()\nax.plot([1, 2])\nplt.show()"
    r = run_code(code, checks=[Check("fig", figure=True)])
    assert r.ok and len(r.figures) == 1 and r.figures[0][:4] == b"\x89PNG"
    assert r.checks[0].passed


def test_pandas_and_sqlite_available():
    code = ("import pandas as pd, sqlite3\nc = sqlite3.connect('x.db')\n"
            "c.execute('create table t (a)')\nc.execute('insert into t values (3)')\n"
            "print(pd.read_sql_query('select * from t', c)['a'].sum())")
    r = run_code(code)
    assert r.ok and r.stdout.strip() == "3"


def test_setup_and_prelude_run_first_with_hidden_output():
    r = run_code("print(x + y)", setup="x = 1\nprint('secret setup')",
                 prelude="y = 2\nprint('secret prelude')")
    assert r.ok and r.stdout.strip() == "3"


def test_overlong_code_rejected():
    assert run_code("x = 1\n" * 5000).blocked
