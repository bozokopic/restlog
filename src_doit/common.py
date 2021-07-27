from pathlib import Path
import shutil


def rm_rf(*paths: Path):
    for path in paths:
        if not path.exists():
            continue
        if path.is_dir():
            shutil.rmtree(str(path), ignore_errors=True)
        else:
            path.unlink()


def cp_r(src: Path, dest: Path):
    if src.is_dir():
        shutil.copytree(str(src), str(dest), dirs_exist_ok=True)
    else:
        shutil.copy2(str(src), str(dest))
