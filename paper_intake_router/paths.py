from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def repo_root_from_file(file_path: str | Path, levels: int = 1) -> Path:
    path = Path(file_path).resolve()
    root = path.parents[levels - 1]
    if (root / "scripts").exists() or (root / "SKILL.md").exists():
        return root
    for candidate in path.parents:
        if (candidate / "scripts").exists() or (candidate / "SKILL.md").exists():
            return candidate
    return root


def workspace_root(repo_root: str | Path) -> Path:
    repo_root = Path(repo_root).resolve()
    if repo_root.name == "paper-intake-router" and repo_root.parent.name == "open-source":
        return repo_root.parent.parent
    if repo_root.name == "paper-intake-router" and repo_root.parent.name == "skills":
        return repo_root.parent.parent
    return repo_root.parent


def skill_script(repo_root: str | Path, name: str) -> Path:
    return Path(repo_root).resolve() / "scripts" / name


def run_python_script(script: str | Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(script), *args]
    return subprocess.run(cmd, text=True, capture_output=False, check=check)


def run_python_script_capture(script: str | Path, *args: str, check: bool = True) -> subprocess.CompletedProcess[str]:
    cmd = [sys.executable, str(script), *args]
    return subprocess.run(cmd, text=True, capture_output=True, check=check)


def load_json(path: str | Path) -> Any:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def write_json(path: str | Path, data: Any) -> None:
    Path(path).write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def import_module_from_path(module_name: str, path: str | Path):
    spec = importlib.util.spec_from_file_location(module_name, Path(path))
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot import module from {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module
