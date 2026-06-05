from __future__ import annotations

from pathlib import Path

from qual_lab.doctor import run_doctor


def test_doctor_reports_expected_layout(tmp_path: Path) -> None:
    (tmp_path / ".git").mkdir()
    for relative_path in (
        "src/qual_lab",
        "tests",
        "docs",
        "contracts",
        "examples",
        "artifacts",
        "tools",
    ):
        (tmp_path / relative_path).mkdir(parents=True, exist_ok=True)
    report = run_doctor(tmp_path)
    assert report.git_repo_present is True
    assert all(check.present for check in report.expected_paths)
    assert report.policy.team_coding_supported is True
    assert report.policy.adjudication_supported is True
    assert report.policy.synthesis_exports_supported is True
    assert report.policy.assistive_algorithm_policy_gates_required is True
    assert report.warnings == []


def test_doctor_warns_when_layout_is_missing(tmp_path: Path) -> None:
    report = run_doctor(tmp_path)
    assert report.git_repo_present is False
    assert report.warnings
