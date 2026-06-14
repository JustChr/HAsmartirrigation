"""Regression: the ``datetime`` platform submodule must not shadow the stdlib.

The integration ships ``custom_components/smart_irrigation/datetime.py`` (the
rain-delay ``DateTimeEntity`` platform). A package submodule named ``datetime``
is bound as the ``datetime`` attribute of the *parent package* when imported —
and the parent package's attribute namespace IS ``__init__.py``'s globals. So a
global in ``__init__.py`` literally named ``datetime`` got clobbered by the
submodule the moment Home Assistant set up the ``datetime`` platform, turning
every ``datetime.now()`` in ``_async_update_all`` into
``AttributeError: module '...smart_irrigation.datetime' has no attribute 'now'``
— a hard 500 on every weather update (and silent failure of the auto-update
timer). Fixed by importing the stdlib class under the alias ``dt_datetime``.

Importing the full package ``__init__`` pulls the whole Home Assistant chain
(these lightweight tests import submodules only), so this guards the fix at the
source level: ``__init__.py`` must not bind a global named ``datetime``, and
must not call ``datetime.now()``.
"""

import ast
import re
from pathlib import Path

INIT = (
    Path(__file__).resolve().parent.parent
    / "custom_components"
    / "smart_irrigation"
    / "__init__.py"
)


def _init_source() -> str:
    return INIT.read_text(encoding="utf-8")


def test_init_does_not_bind_a_global_named_datetime():
    """``from datetime import datetime`` / ``import datetime`` would create a
    global the platform submodule import clobbers — require an alias instead."""
    tree = ast.parse(_init_source())
    bound = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            for alias in node.names:
                bound.add(alias.asname or alias.name)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                # ``import datetime`` binds ``datetime``; ``import datetime as x`` binds ``x``
                bound.add(alias.asname or alias.name.split(".")[0])
    assert "datetime" not in bound, (
        "__init__.py binds a global named 'datetime' — the datetime.py platform "
        "submodule will shadow it on platform load (500 on every weather update). "
        "Import the stdlib class under an alias (e.g. 'dt_datetime')."
    )


def test_init_makes_no_bare_datetime_now_call():
    """The aliased class must actually be used at the call sites."""
    assert not re.search(r"\bdatetime\.now\s*\(", _init_source()), (
        "__init__.py calls datetime.now() — that name resolves to the platform "
        "submodule after platform load. Use the aliased stdlib class."
    )
