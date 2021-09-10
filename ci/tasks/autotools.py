import yaml

class Autotools:
    def __init__(self, cwd=None):
        self.flags = []
        self.build_dir = None
        self.configure_path = "./configure"
        self.cwd = cwd

    def with_build_dir(self):
        self.configure_path = "../configure"
        self.build_dir = "build"
        return self

    def as_script(self):
        script = ""
        if self.cwd:
            script += "pushd %s" % self.cwd

        script += """
            autoreconf -fi
            ./autogen.sh
        """

        if self.build_dir:
            script += "mkdir -p %s && pushd %s" % (self.build_dir, self.build_dir)

        # TODO: nproc ?
        script += """
            %s `[[ -f ../.ci-configure-flags ]] && cat ../.ci-configure-flags`
            make -j16
        """ % self.configure_path

        if self.build_dir:
            script += "popd"

        if self.cwd:
            script += "popd"

        return script

