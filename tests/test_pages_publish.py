"""scripts/pages_publish.sh against a local bare repository (no network, no GitHub)."""

from __future__ import annotations

import os
import subprocess
from pathlib import Path

import pytest

SCRIPT = Path(__file__).resolve().parent.parent / "scripts/pages_publish.sh"


@pytest.fixture
def remote(tmp_path):
    bare = tmp_path / "remote.git"
    subprocess.run(["git", "init", "--bare", "--quiet", str(bare)], check=True)
    return bare


def publish(remote, tmp_path, mode, pr=None, html="<html>site</html>"):
    site = tmp_path / "site"
    site.mkdir(exist_ok=True)
    (site / "index.html").write_text(html)
    env = {**os.environ, "REPO_URL": str(remote), "SITE_DIR": str(site)}
    args = ["bash", str(SCRIPT), mode] + ([str(pr)] if pr else [])
    return subprocess.run(args, env=env, capture_output=True, text=True)


def files(remote, tmp_path):
    checkout = tmp_path / "check"
    if checkout.exists():
        subprocess.run(["rm", "-rf", str(checkout)], check=True)
    subprocess.run(
        ["git", "clone", "--quiet", "--branch", "gh-pages", str(remote), str(checkout)], check=True
    )
    return {
        str(p.relative_to(checkout)): p.read_text()
        for p in checkout.rglob("*")
        if p.is_file() and ".git" not in p.parts
    }


def test_main_creates_the_branch_and_publishes_at_the_root(remote, tmp_path):
    result = publish(remote, tmp_path, "main", html="v1")
    assert result.returncode == 0, result.stderr
    assert files(remote, tmp_path)["index.html"] == "v1"


def test_previews_live_in_their_own_folders_and_leave_the_root_alone(remote, tmp_path):
    publish(remote, tmp_path, "main", html="root")
    assert publish(remote, tmp_path, "preview", 7, html="pr7").returncode == 0
    assert publish(remote, tmp_path, "preview", 8, html="pr8").returncode == 0
    got = files(remote, tmp_path)
    assert got["index.html"] == "root"
    assert got["pr-preview/pr-7/index.html"] == "pr7"
    assert got["pr-preview/pr-8/index.html"] == "pr8"


def test_a_new_main_deploy_keeps_open_previews(remote, tmp_path):
    publish(remote, tmp_path, "preview", 7, html="pr7")
    publish(remote, tmp_path, "main", html="root-v2")
    got = files(remote, tmp_path)
    assert got["index.html"] == "root-v2"
    assert got["pr-preview/pr-7/index.html"] == "pr7"


def test_pushing_a_preview_again_replaces_it(remote, tmp_path):
    publish(remote, tmp_path, "preview", 7, html="first")
    publish(remote, tmp_path, "preview", 7, html="second")
    assert files(remote, tmp_path)["pr-preview/pr-7/index.html"] == "second"


def test_remove_deletes_only_that_preview(remote, tmp_path):
    publish(remote, tmp_path, "main", html="root")
    publish(remote, tmp_path, "preview", 7, html="pr7")
    publish(remote, tmp_path, "preview", 8, html="pr8")
    assert publish(remote, tmp_path, "remove", 7).returncode == 0
    got = files(remote, tmp_path)
    assert "pr-preview/pr-7/index.html" not in got
    assert got["pr-preview/pr-8/index.html"] == "pr8" and got["index.html"] == "root"


def test_remove_before_any_deploy_is_a_clean_no_op(remote, tmp_path):
    result = publish(remote, tmp_path, "remove", 3)
    assert result.returncode == 0 and "nothing to remove" in result.stdout


def test_publishing_the_same_content_twice_does_not_fail(remote, tmp_path):
    publish(remote, tmp_path, "main", html="same")
    result = publish(remote, tmp_path, "main", html="same")
    assert result.returncode == 0 and "nothing to publish" in result.stdout


def test_bad_arguments_are_rejected(remote, tmp_path):
    assert publish(remote, tmp_path, "preview").returncode == 2  # PR number missing
    assert publish(remote, tmp_path, "preview", "x1").returncode == 2  # not numeric
    assert publish(remote, tmp_path, "bogus", 5).returncode == 2
