import subprocess
import os
import pytest


def get_local_version():
    """Get the local version of the project"""
    with open("app/VERSION", "r") as version_file:
        app_version = version_file.read().strip()

    with open("launcher/VERSION", "r") as version_file:
        launcher_version = version_file.read().strip()

    return app_version, launcher_version


def get_tag_version():
    """Get the version of the project from the tag of the commit"""
    tag = (
        subprocess.check_output(["git", "describe", "--tags", "--abbrev=0"])
        .decode("utf-8")
        .strip()
    )
    tag_app_version, tag_launcher_version = tag.split("+")

    return tag_app_version.strip("v"), tag_launcher_version.split("--")[1]


@pytest.mark.skipif(
    os.environ.get("TEST_ENV") == "dev", reason="Running in dev environment"
)
def test_version_eq():
    """Check the local version of the project to match with the tag of the commit"""
    app_version, launcher_version = get_local_version()
    tag_app_version, tag_launcher_version = get_tag_version()

    assert app_version == tag_app_version
    assert launcher_version == tag_launcher_version


def test_version_gte():
    """Check the local version of the project to be >= the tag of the commit"""
    app_version, launcher_version = get_local_version()
    tag_app_version, tag_launcher_version = get_tag_version()

    assert app_version >= tag_app_version
    assert launcher_version >= tag_launcher_version
