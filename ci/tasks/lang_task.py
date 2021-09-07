from .common import linux_build_task
from .autotools import Autotools
from decisionlib import CONFIG
import os.path

def get_lang_task(with_apertium):
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
        "divvun-gramcheck"
    ]

    if with_apertium:
        lang_deps.extend(["apertium", "apertium-dev", "apertium-lex-tools"])

    if os.path.isfile('.build-config.yml'):
        print("Found config file, do something with it now")


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
        .with_script(Autotools("../giella-shared").as_script())
        .with_script(Autotools("../giella-core").as_script())
        .with_script(Autotools().with_build_dir().as_script())
        .with_script("ls build/tools/spellcheckers/weights")
        .with_artifacts("repo/build/tools/spellcheckers/", type="directory")
        .find_or_create("build.linux_x64.%s" % CONFIG.tree_hash())
    )



