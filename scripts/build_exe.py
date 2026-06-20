import os
import shutil
import subprocess
import platform
from pathlib import Path
import tomllib

def get_version() -> str:
    try:
        with open("pyproject.toml", "rb") as f:
            data = tomllib.load(f)
            return data.get("project", {}).get("version", "0.1.0")
    except Exception:
        return "0.1.0"

def get_platform_suffix() -> str:
    sys_name = platform.system().lower()
    if sys_name == "windows":
        return "Windows"
    elif sys_name == "darwin":
        return "macOS"
    elif sys_name == "linux":
        return "Linux"
    return sys_name

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
    suffix = get_platform_suffix()
    release_dir = Path(f"Release_v{version}")
    
    if release_dir.exists():
        shutil.rmtree(release_dir)
    release_dir.mkdir()

    zip_base = f"NekoBuddy_v{version}_{suffix}"

    if suffix == "macOS":
        app_dir = Path("dist/NekoBuddy.app")
        macos_dir = app_dir / "Contents" / "MacOS"
        
        shutil.copytree("assets", macos_dir / "assets", dirs_exist_ok=True)
        if Path(".env.example").exists():
            shutil.copy(".env.example", macos_dir / ".env")
            
        shutil.copytree(app_dir, release_dir / "NekoBuddy.app")
        
        print("Packaging macOS app bundle...")
        shutil.make_archive(zip_base, "zip", root_dir=release_dir, base_dir="NekoBuddy.app")
    else:
        dist_dir = Path("dist/NekoBuddy")
        shutil.copytree(dist_dir, release_dir / "NekoBuddy")

        shutil.copytree("assets", release_dir / "NekoBuddy" / "assets", dirs_exist_ok=True)
        if Path(".env.example").exists():
            shutil.copy(".env.example", release_dir / "NekoBuddy" / ".env")

        print(f"Packaging {suffix} release directory...")
        shutil.make_archive(zip_base, "zip", root_dir=release_dir, base_dir="NekoBuddy")
        
    print(f"Build complete! Output is in the {release_dir.absolute()} folder.")
    print(f"Zip archive is ready at: {Path(zip_base + '.zip').absolute()}")

if __name__ == "__main__":
    build()


