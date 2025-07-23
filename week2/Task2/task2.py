import requests
import importlib.abc
import importlib.util
import os
import types
import sys

class GitHubLoader(importlib.abc.SourceLoader):
    def get_data(self, path):
        response = requests.get(self.raw_url)
        response.raise_for_status()
        return response.text.encode("utf-8")  # must return bytes

    def get_filename(self, fullname):
        return f"{fullname}.py"
    def __init__(self, fullname, raw_url):
        self.fullname = fullname
        self.raw_url = raw_url

    def create_module(self, spec):
        return types.ModuleType(spec.name)

    def exec_module(self, module):
        response = requests.get(self.raw_url)
        response.raise_for_status()
        source_code = response.text
        exec(source_code, module.__dict__)

class GitHubFinder:
    def find_spec(self, fullname, path=None, target=None):
        
        if not fullname.startswith("github"):
            return None
        path = "vectorra.SE_task_1.week2.Task1.Task1_week2"
        if path:
            fullname += '.' + path
        parts = fullname.split(".")
        if len(parts) < 4:
            return None

        _, username, repo, *path_parts = parts

        file_name = path_parts[-1] + ".py"
        file_path = "/".join(path_parts[:-1] + [file_name])

        raw_url = f"https://raw.github.com/{username}/{repo}/main/{file_path}"
        print(raw_url)
        loader = GitHubLoader(fullname, raw_url)
        return importlib.util.spec_from_loader(fullname, loader)




# Register the finder
if not any(isinstance(f, GitHubFinder) for f in sys.meta_path):
    sys.meta_path.insert(0, GitHubFinder())

import github as g
def main():
    g.test_singleton()
    pass

if __name__ == "__main__":
    main()