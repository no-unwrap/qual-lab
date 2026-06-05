from __future__ import annotations

from pathlib import Path

from qual_lab.models import StorageLocator, StorageScheme

REPO_ROOT = Path(__file__).resolve().parents[2]


def storage_locator_outside_repo(
    source: StorageLocator,
    repo_root: Path,
) -> tuple[bool, str | None]:
    if source.storage_scheme in {
        StorageScheme.SECURE_URI,
        StorageScheme.EXTERNAL_OBJECT_STORE,
        StorageScheme.SYNTHETIC,
    }:
        if "://" not in source.locator:
            return False, "non-local storage locators must use an explicit URI-like scheme"
        return True, None

    raw_locator = source.locator.removeprefix("file://")
    locator_path = Path(raw_locator)
    if not locator_path.is_absolute():
        return False, "local storage locators must use an absolute path outside the repository"

    resolved_repo_root = repo_root.resolve()
    resolved_locator = locator_path.resolve(strict=False)
    if resolved_locator == resolved_repo_root or resolved_repo_root in resolved_locator.parents:
        return (
            False,
            "storage locators for staged or deidentified artifacts must stay "
            "outside the repository root",
        )

    return True, None
