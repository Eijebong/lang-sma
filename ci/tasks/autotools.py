import yaml

class Autotools:
    def __init__(self, cwd=None):
        self.flags = []
        self.build_dir = "build"
        self.cwd = cwd

    def as_script(self):
        script = ""
        if self.cwd:
            script += "cd %s" % self.cwd

        script += """
            autoreconf -fi
            ./autogen.sh
            mkdir -p %s
            cd %s && ../configure `[[ -f ../.ci-configure-flags ]] && cat ../.ci-configure-flags`
            make
        """ % (self.build_dir, self.build_dir)

        if self.cwd:
            script += "cd -"

        return script

