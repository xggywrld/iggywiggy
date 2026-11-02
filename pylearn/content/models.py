"""Data model for all learning content.

Every piece of content is plain, immutable data. This keeps lessons easy to
write, easy to test (the test-suite runs every example and verifies every
answer key against the real Python interpreter) and easy to render in the UI.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Optional, Union


@dataclass(frozen=True)
class Check:
    """One automatic test applied to a learner's code.

    Exactly one of ``expr``, ``stdout_equals``, ``stdout_contains`` or
    ``figure`` should be set.

    * ``expr``: a Python expression evaluated *after* the learner's code, in the
      same namespace. Its value is compared with ``expected``.
    * ``stdout_equals`` / ``stdout_contains``: compare what the code printed.
    * ``figure``: require that at least one matplotlib figure was created.
    """

    description: str
    expr: Optional[str] = None
    expected: Any = None
    tolerance: float = 1e-6
    stdout_equals: Optional[str] = None
    stdout_contains: Optional[str] = None
    figure: bool = False

    def to_payload(self) -> dict:
        return {
            "description": self.description,
            "expr": self.expr,
            "expected": self.expected,
            "tolerance": self.tolerance,
            "stdout_equals": self.stdout_equals,
            "stdout_contains": self.stdout_contains,
            "figure": self.figure,
        }


@dataclass(frozen=True)
class Example:
    """A runnable, editable code example shown inside a lesson."""

    title: str
    code: str
    explanation: str = ""
    stdin: str = ""


@dataclass(frozen=True)
class Lesson:
    id: str
    title: str
    body: str  # Markdown
    examples: tuple[Example, ...] = ()
    key_points: tuple[str, ...] = ()


@dataclass(frozen=True)
class Option:
    text: str
    correct: bool = False
    why: str = ""  # Why this option is right or (more importantly) wrong.


@dataclass(frozen=True)
class MCQ:
    id: str
    prompt: str
    options: tuple[Option, ...]
    explanation: str
    code: str = ""
    tags: tuple[str, ...] = ()
    kind: str = field(default="mcq", init=False)

    @property
    def correct_index(self) -> int:
        return next(i for i, o in enumerate(self.options) if o.correct)


@dataclass(frozen=True)
class PredictOutput:
    id: str
    prompt: str
    code: str
    expected_output: str
    explanation: str
    tags: tuple[str, ...] = ()
    # Map of a *specific* wrong answer (normalised) -> tailored explanation.
    common_wrong: tuple[tuple[str, str], ...] = ()
    kind: str = field(default="predict", init=False)


@dataclass(frozen=True)
class DebugExercise:
    id: str
    prompt: str
    buggy_code: str
    solution: str
    checks: tuple[Check, ...]
    explanation: str
    hints: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    stdin: str = ""
    kind: str = field(default="debug", init=False)


@dataclass(frozen=True)
class CodingExercise:
    id: str
    prompt: str
    starter: str
    solution: str
    checks: tuple[Check, ...]
    explanation: str
    hints: tuple[str, ...] = ()
    tags: tuple[str, ...] = ()
    stdin: str = ""
    kind: str = field(default="code", init=False)


Item = Union[MCQ, PredictOutput, DebugExercise, CodingExercise]


@dataclass(frozen=True)
class Topic:
    id: str
    number: int
    title: str
    summary: str
    lessons: tuple[Lesson, ...]
    items: tuple[Item, ...]
    prerequisites: tuple[str, ...] = ()
    icon: str = "📘"

    def items_of(self, kind: str) -> list[Item]:
        return [i for i in self.items if i.kind == kind]


@dataclass(frozen=True)
class ProjectStep:
    title: str
    instructions: str  # Markdown
    starter: str
    solution: str
    checks: tuple[Check, ...]
    hints: tuple[str, ...] = ()


@dataclass(frozen=True)
class Project:
    id: str
    title: str
    story: str  # Markdown
    skills: tuple[str, ...]
    setup_code: str  # Trusted code that creates the project's data files.
    steps: tuple[ProjectStep, ...]
    topics: tuple[str, ...] = ()
