import subprocess
import sys
import tomllib
from pathlib import Path


def run_cmd(command: str):
    result = subprocess.run(command, shell=True, text=True)
    if result.returncode != 0:
        print(f"Error: '{command}' terminated with code {result.returncode}")
        sys.exit(1)


def get_project_version() -> str:
    toml_path = Path("pyproject.toml")
    if not toml_path.exists():
        print("Error: pyproject.toml not found")
        sys.exit(1)

    with open(toml_path, "rb") as f:
        data = tomllib.load(f)
        return data["project"]["version"]

def main():
    print("Release script")
    commit_message = input("Input commit message: ").strip()

    if not commit_message:
        print("Error: commit message cannot be empty")
        sys.exit(1)

    version = get_project_version()
    tag_name = f"v{version}"
    print(f"Detected release version: {tag_name}")

    confirm = input(f"Start release version {tag_name} with message: '{commit_message}'? (y/n): ")
    if confirm.lower() != 'y':
        print("Canceled")
        sys.exit(0)

    run_cmd("git checkout develop")
    run_cmd("git pull origin develop")
    run_cmd("git add .")
    run_cmd(f'git commit -m "{commit_message}"')
    run_cmd("git push origin develop")

    run_cmd("git checkout main")
    run_cmd("git pull origin main")
    run_cmd(f'git merge --no-ff develop -m "Merge develop into main for release {tag_name}"')
    run_cmd("git push origin main")

    run_cmd(f'git tag -a {tag_name} -m "Release version {version}"')
    run_cmd("git push origin --tags")

    run_cmd("git checkout develop")

    print(f"\nRelease {tag_name} successfully completed and pushed to repository")


if __name__ == "__main__":
    main()