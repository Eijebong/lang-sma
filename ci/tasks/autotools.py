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
            cd %s && ../configure %s
            make
        """ % (self.build_dir, self.build_dir, " ".join(self.flags))

        if self.cwd:
            script += "cd -"

        return script

    def add_flag(self, flag):
        self.flags.append(flag)

    def build_config_to_flags(self, config):
        config = yaml.load(config)
        print(config)
