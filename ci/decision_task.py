# coding: utf8

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

import os.path
import decisionlib
from decisionlib import CONFIG, SHARED


def tasks(task_for):
    if CONFIG.git_ref.startswith("refs/heads/"):
        branch = CONFIG.git_ref[len("refs/heads/") :]

    # Work around a tc-github bug/limitation:
    # https://bugzilla.mozilla.org/show_bug.cgi?id=1548781#c4
    if task_for.startswith("github"):
        # https://github.com/taskcluster/taskcluster/blob/21f257dc8/services/github/config.yml#L14
        CONFIG.routes_for_all_subtasks.append("statuses")

    if task_for == "github-push":
        linux_build_core()
    elif task_for == "github-pull-request":
        CONFIG.index_read_only = True
        CONFIG.docker_image_build_worker_type = None
        # We want the merge commit that GitHub creates for the PR.
        # The event does contain a `pull_request.merge_commit_sha` key, but it is wrong:
        # https://github.com/servo/servo/pull/22597#issuecomment-451518810
        CONFIG.git_sha_is_current_head()

        linux_build_core()
    elif task_for == "daily":
        pass


build_artifacts_expire_in = "1 week"
build_dependencies_artifacts_expire_in = "1 month"
log_artifacts_expire_in = "1 year"

build_env = {
    "RUSTFLAGS": "-Dwarnings",
}

linux_build_env = {
    "RUST_BACKTRACE": "1",  # https://github.com/servo/servo/issues/26192
}


def linux_build_core():
    lang_deps = [
        "wget",
        "build-essential",
        "autotools-dev",
        "autoconf",
        "git",
        "pkg-config",
        "gawk",
        "python3-pip",
        "zip",
        "bc",
        "foma",
        "hfst",
        "libhfst-dev",
        "cg3-dev",
    ]  # TODO: , "divvun-gramcheck"]

    return (
        linux_build_task("Linux debug build")
        .with_script(
            """
            wget -q https://apertium.projectjj.com/apt/install-nightly.sh -O install-nightly.sh && bash install-nightly.sh
        """
        )
        .with_apt_update()
        .with_apt_install(*lang_deps)
        .with_pip_install("PyYAML")
        .with_additional_repo(
            "https://github.com/giellalt/giella-core.git", "../giella-core"
        )
        .with_additional_repo(
            "https://github.com/giellalt/giella-shared.git", "../giella-shared"
        )
        .with_script(
            """
            cd ../giella-shared && autoreconf -fi && ./configure && make && cd -
            cd ../giella-core && autoreconf -fi && ./configure && make && cd -
            autoreconf -fi && ./configure && make
        """
        )
        .find_or_create("build.linux_x64.%s" % CONFIG.tree_hash())
    )


def dockerfile_path(name):
    return os.path.join(os.path.dirname(__file__), "docker", name + ".dockerfile")


def linux_task(name):
    return decisionlib.DockerWorkerTask(name).with_worker_type("linux")


def linux_build_task(name, *, build_env=build_env):
    task = (
        linux_task(name)
        # https://docs.taskcluster.net/docs/reference/workers/docker-worker/docs/caches
        .with_scopes("docker-worker:cache:divvun-*")
        .with_caches(
            **{
                "divvun-cargo-registry": "/root/.cargo/registry",
                "divvun-cargo-git": "/root/.cargo/git",
                "divvun-rustup": "/root/.rustup",
            }
        )
        .with_index_and_artifacts_expire_in(build_artifacts_expire_in)
        .with_max_run_time_minutes(60)
        .with_docker_image("ubuntu:hirsute")
        .with_apt_update()
        .with_apt_install("curl git")
        .with_env(**build_env, **linux_build_env)
        .with_repo_bundle()
    )
    return task


CONFIG.task_name_template = "Divvun: %s"
CONFIG.docker_images_expire_in = build_dependencies_artifacts_expire_in
CONFIG.repacked_msi_files_expire_in = build_dependencies_artifacts_expire_in
CONFIG.index_prefix = "project.divvun"
CONFIG.default_provisioner_id = "test"
CONFIG.docker_image_build_worker_type = "docker"

task_for = os.environ["TASK_FOR"]
with decisionlib.make_repo_bundle():
    tasks(task_for)
