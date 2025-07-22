import requests
import re
import json


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


def run_file(filename):
    with open(filename, "r", encoding="utf-8") as f:
        exec(f.read(), {})


def main():
    url = "https://github.com/vectorra/SE_task_1/blob/main/week1/py_file.py"
    html = fetch_github_html(url)
    lines = extract_raw_lines(html)
    print("Extracted lines:\n", lines)
    filename = save_code_to_file(lines)
    print(f"Saved to: {filename}")
    run_file(filename)


if __name__ == "__main__":
    main()
