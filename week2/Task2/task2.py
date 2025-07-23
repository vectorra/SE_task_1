import requests
import re
import json
import importlib.abc
import importlib.util
import os
import sys


def fetch_github_html(url):
    response = requests.get(url)
    response.raise_for_status()
    return response.text


def extract_raw_lines(html):
    match = re.search(
        r'<script type="application/json" data-target="react-app.embeddedData">(.+?)</script>',
        html, re.DOTALL
    )
    if not match:
        raise ValueError("No embedded JSON script found in HTML.")
    data = json.loads(match.group(1))
    raw_lines = data["payload"]["blob"]["rawLines"]
    return raw_lines


def save_code_to_file(lines, filename="output.py"):
    code = "\n".join(lines) + "\n"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(code)
    return filename


class GitLoader(importlib.abc.SourceLoader):
    def get_data(self, url):
        html = fetch_github_html(url)
        lines = extract_raw_lines(html)
        print("Extracted lines:\n", lines)
        return lines

    def get_filename(self):
        return f"{"repo"}.py"


class GitFinder:
    def find_spec(self, url, path, target):
        potential_name = f"{"repo"}.py"

        if os.path.exists(potential_name):
            # Note the use of spec_from_loader. This is a helper function that, when given a loader object, will construct a spec for you. Helps a
            # lot if you're lazy like me.
            return importlib.util.spec_from_loader(
                url, GitLoader(), origin=potential_name
            )

        return None

from github.vectorra.SE_task_1.week2.Task1.Task1_week2 import test_singleton

def main():
    test_singleton()


if __name__ == "__main__":
    main()
