URL_MACOS = "https://pahkat.uit.no/artifacts/pahkat-prefix-cli_0.1.0_macos_amd64.txz"

class Pahkat:
    def __init__(self):
        self.should_bootstrap = False
        self.path = "/tmp/pahkat-tmp"
        self.repos = []
        self.script = ""

    def bootstrap(self):
        self.should_bootstrap = True
        return self

    def as_script(self):

        if self.should_bootstrap:
            # TODO: Differentiate based on OS
            self.script = """
                rm -R %s
                curl %s -o pahkat-prefix.txz
                tar xvf pahkat-prefix.txz
                export PATH=$PATH:`pwd`/bin
                pahkat-prefix-cli init -c %s
            """ % (self.path, URL_MACOS, self.path) + self.script

        return self.script

    def with_repository(self, url, *, channel=""):
        self.script += "pahkat-prefix-cli config repo add -c %s %s %s\n" % (self.path, url, channel)
        return self

    def with_packages(self, *pkgs):
        self.script += "pahkat-prefix-cli install %s -c %s\n" % (" ".join(pkgs), self.path)
        for pkg in pkgs:
            self.script += "export PATH=$PATH:%s/pkg/%s/bin\n" % (self.path, pkg)
        return self
