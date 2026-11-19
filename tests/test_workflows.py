"""Workflow policy: only GitHub's own actions, and no secrets passed around."""

from __future__ import annotations

import re
from pathlib import Path

WORKFLOWS = sorted((Path(__file__).resolve().parent.parent / ".github/workflows").glob("*.yml"))


def test_there_are_workflows():
    assert {w.name for w in WORKFLOWS} >= {"ci.yml", "release.yml"}


def test_only_githubs_own_actions_are_used():
    for workflow in WORKFLOWS:
        for line in workflow.read_text(encoding="utf-8").splitlines():
            match = re.match(r"\s*-?\s*uses:\s*(\S+)", line)
            if match:
                assert match.group(1).startswith("actions/"), (
                    f"{workflow.name}: third-party action {match.group(1)}"
                )


def test_no_repository_secrets_are_referenced():
    for workflow in WORKFLOWS:
        assert "secrets." not in workflow.read_text(encoding="utf-8"), workflow.name


def test_the_site_is_published_with_githubs_official_pages_actions():
    ci = (WORKFLOWS[0].parent / "ci.yml").read_text(encoding="utf-8")
    assert "actions/upload-pages-artifact@" in ci and "actions/deploy-pages@" in ci
    assert "pages: write" in ci and "id-token: write" in ci
    assert "github.ref == 'refs/heads/main'" in ci  # only merges to main deploy


def test_the_pages_artifact_is_uploaded_in_a_job_before_the_one_that_deploys_it():
    """Uploading and deploying in the same job raced ("No artifacts named github-pages")."""
    ci = (WORKFLOWS[0].parent / "ci.yml").read_text(encoding="utf-8")
    upload_job = ci.index("pages-artifact:")
    deploy_job = ci.index("\n  deploy:")
    assert ci.index("actions/upload-pages-artifact@") < deploy_job
    assert upload_job < ci.index("actions/deploy-pages@")
    assert "needs: pages-artifact" in ci[deploy_job:]
