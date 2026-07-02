"""Install the bundled valve script blueprints into the user's config.

Home Assistant has no first-class "an integration ships blueprints" API, so we
copy the bundled YAMLs into ``config/blueprints/script/<domain>/`` on setup.

Copy-if-missing only: a blueprint the user has already imported or edited is
never overwritten (so their changes survive an integration update). The
trade-off is that an updated bundled blueprint will not replace an existing
copy — a version-aware update is left for later.
"""

from __future__ import annotations

import logging
import shutil
from pathlib import Path

_LOGGER = logging.getLogger(__name__)


def install_bundled_blueprints(src_dir, dst_dir) -> list:
    """Copy ``*.yaml`` from ``src_dir`` into ``dst_dir`` if not already present.

    Returns the list of newly installed filenames. Never overwrites an existing
    destination file. All filesystem errors are swallowed (logged) so a copy
    failure can never break integration setup.
    """
    installed: list = []
    try:
        src = Path(src_dir)
        dst = Path(dst_dir)
        if not src.is_dir():
            return installed
        dst.mkdir(parents=True, exist_ok=True)
        for yaml_file in sorted(src.glob("*.yaml")):
            target = dst / yaml_file.name
            if target.exists():
                continue
            try:
                shutil.copyfile(yaml_file, target)
                installed.append(yaml_file.name)
            except OSError as err:
                _LOGGER.warning(
                    "Could not install blueprint %s: %s", yaml_file.name, err
                )
        if installed:
            _LOGGER.info(
                "Installed %d valve blueprint(s): %s",
                len(installed),
                ", ".join(installed),
            )
    except Exception as err:  # noqa: BLE001 - must never break integration setup
        _LOGGER.warning("Blueprint install skipped: %s", err)
    return installed
