import requests
import yaml


class GithubAction:
    def __init__(self, path, args):
        """
        Path here is the github path to an actions which is {org}/{repo}/{action_path_in_repo}
        Args will all be put in the env as INPUT_{key} = {value}
        """
        self.path = path
        self.args = {}
        self.parse_config()
        self.args.update(args)

    def env_variables(self):
        out = ""
        for k, v in self.args.items():
            k = k.upper()
            escaped_v = str(v).replace('"','\\"')
            out += f"export INPUT_{k}=\"{escaped_v}\"\n"

        # TODO: Move this to cwd/_temp
        out += "export RUNNER_TEMP=\"$HOME/$TASK_ID/_temp\"\n"
        # TODO: Move this to cwd/_work
        out += "export GITHUB_WORKSPACE=\"$HOME/$TASK_ID\"\n"

        return out

    def parse_config(self):
        url = 'https://raw.githubusercontent.com/' + self.repo_name + '/master/' + self.action_path + '/action.yml'
        config = requests.get(url).text
        config = yaml.load(config)
        for name, content in config.get('inputs', {}).items():
            if "default" in content:
                self.args[name] = content["default"]

    @property
    def repo_name(self):
        parts = self.path.split('/')
        assert len(parts) > 1

        if parts[0] == "actions":
            raise NotImplementedError
        else:
            return '/'.join(parts[:2])

    @property
    def action_path(self):
        parts = self.path.split('/')
        if parts[0] == "actions":
            raise NotImplementedError
        else:
            return '/'.join(parts[2:])

    @property
    def git_fetch_url(self):
        return f"https://github.com/{self.repo_name}"

    @property
    def script_path(self):
        return self.action_path + "/index.js"
