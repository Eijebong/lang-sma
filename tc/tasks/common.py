import decisionlib

build_artifacts_expire_in = "1 week"

build_env = {
    "RUSTFLAGS": "-Dwarnings",
}

linux_build_env = {
    "RUST_BACKTRACE": "1",  # https://github.com/servo/servo/issues/26192
}


def linux_task(name):
    return decisionlib.DockerWorkerTask(name).with_worker_type("linux")


def linux_build_task(name, bundle_dest="repo"):
    task = (
        linux_task(name)
        # https://docs.taskcluster.net/docs/reference/workers/docker-worker/docs/caches
        .with_scopes("docker-worker:cache:divvun-*")
        .with_features("taskclusterProxy")
        .with_caches(
            **{
                "divvun-cargo-registry": "/root/.cargo/registry",
                "divvun-cargo-git": "/root/.cargo/git",
                "divvun-rustup": "/root/.rustup",
            }
        )
        .with_index_and_artifacts_expire_in(build_artifacts_expire_in)
        .with_max_run_time_minutes(60)
        .with_scopes("queue:get-artifact:private/*")
        .with_script("mkdir -p $HOME/$TASK_ID")
        .with_docker_image("ubuntu:hirsute")
        .with_apt_update()
        .with_apt_install("curl", "git", "wget", "nodejs")
        .with_env(**build_env, **linux_build_env)
        .with_repo_bundle("repo", bundle_dest)
        .with_repo_bundle("ci", "ci")
        .with_script(f"cd $HOME/$TASK_ID/{bundle_dest}")
    )
    return task


def macos_task(name):
    return (
        decisionlib.MacOsGenericWorkerTask(name)
        .with_worker_type("macos")
        .with_provisioner_id("divvun")
        .with_index_and_artifacts_expire_in(build_artifacts_expire_in)
        .with_max_run_time_minutes(60)
    )


def windows_task(name):
    return (
        decisionlib.WindowsGenericWorkerTask(name)
        .with_worker_type("windows")
        .with_provisioner_id("divvun")
        .with_scopes("queue:get-artifact:private/*")
        .with_script("mkdir %HOMEDRIVE%%HOMEPATH%\\%TASK_ID%")
        .with_features("taskclusterProxy")
        .with_repo_bundle("ci", "ci")
        .with_index_and_artifacts_expire_in(build_artifacts_expire_in)
        .with_max_run_time_minutes(60)
    )
