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

def linux_build_task(name):
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
        .with_apt_install("curl", "git", "wget")
        .with_env(**build_env, **linux_build_env)
        .with_repo_bundle()
    )
    return task



