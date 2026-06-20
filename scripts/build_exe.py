import os
import shutil
import subprocess
from pathlib import Path
import tomllib

def get_version() -> str:
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.1.1")
    except Exception:
        return "0.1.1"

def build():
    print("Building NekoBuddy executable using PyInstaller...")

    subprocess.run([
        "uv", "run", "pyinstaller",
        "--noconfirm",
        "--noconsole",
        "--collect-all", "litellm",
        "--collect-all", "tiktoken",
        "--hidden-import", "tiktoken_ext.openai_public",
        "--hidden-import", "tiktoken_ext.anthropic",
        "--name", "NekoBuddy",
        "src/main.py"
    ], check=True)

    version = get_version()
    release_dir = Path(f"Release_v{version}")
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()

    dist_dir = Path("dist/NekoBuddy")
    shutil.copytree(dist_dir, release_dir / "NekoBuddy")

    shutil.copytree("assets", release_dir / "NekoBuddy" / "assets")
    if Path(".env.example").exists():
        shutil.copy(".env.example", release_dir / "NekoBuddy" / ".env")
        
    print(f"Build complete! The final output is ready in the {release_dir.absolute()} folder.")

if __name__ == "__main__":
    build()

