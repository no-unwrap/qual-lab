from __future__ import annotations

from dataclasses import asdict, dataclass
from pathlib import Path

from qual_lab.policies import RepositoryPolicy, default_policy


@dataclass(frozen=True)
class DoctorCheck:
    name: str
    path: str
    present: bool


@dataclass(frozen=True)
class DoctorReport:
    repo_root: str
    git_repo_present: bool
    expected_paths: list[DoctorCheck]
    policy: RepositoryPolicy
    warnings: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "repo_root": self.repo_root,
            "git_repo_present": self.git_repo_present,
            "expected_paths": [asdict(check) for check in self.expected_paths],
            "policy": self.policy.to_dict(),
            "warnings": self.warnings,
        }


EXPECTED_PATHS = (
    "src/qual_lab",
    "tests",
    "docs",
    "contracts",
    "examples",
    "artifacts",
    "tools",
)


def run_doctor(repo_root: str | Path | None = None) -> DoctorReport:
    root = Path(repo_root or Path.cwd()).resolve()
    checks = [
        DoctorCheck(
            name=relative_path,
            path=str(root / relative_path),
            present=(root / relative_path).exists(),
        )
        for relative_path in EXPECTED_PATHS
    ]
    warnings: list[str] = []
    if not (root / ".git").exists():
        warnings.append("The expected git repository marker `.git` is missing.")
    missing = [check.name for check in checks if not check.present]
    if missing:
        warnings.append(f"Missing expected paths: {', '.join(missing)}.")
    return DoctorReport(
        repo_root=str(root),
        git_repo_present=(root / ".git").exists(),
        expected_paths=checks,
        policy=default_policy(),
        warnings=warnings,
    )
