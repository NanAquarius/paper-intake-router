#!/usr/bin/env python3
import json
import shutil
from pathlib import Path

WORKSPACE = Path(__file__).resolve().parents[2]
SKILL_DIR_CANDIDATES = [
    WORKSPACE / "skills",
    WORKSPACE / ".claude" / "skills",
    Path.home() / ".openclaw" / "skills",
]


def _collect_existing_skills() -> set[str]:
    existing = set()
    for d in SKILL_DIR_CANDIDATES:
        if d.exists():
            existing.update({p.name for p in d.iterdir() if p.is_dir()})
    return existing


def skill_exists(existing: set[str], names: list[str]) -> bool:
    return any(name in existing for name in names)


def main():
    existing = _collect_existing_skills()
    # Local user-space fallback binaries (no root needed)
    local_bin = WORKSPACE / ".paper-tools" / "bin"
    local_quarto = local_bin / "quarto"
    local_pandoc = local_bin / "pandoc"

    caps = {
        "skills": {
            "paper_write": skill_exists(existing, ["paper-write"]),
            "academic_paper_search": skill_exists(existing, ["academic-paper-search"]),
            "latex_thesis_zh": skill_exists(existing, ["latex-thesis-zh"]),
            "latex_document_writer": skill_exists(existing, ["latex-document-writer"]),
            "mineru": skill_exists(existing, ["mineru", "pdf-process-mineru", "mineru-pdf"]),
            "zotero_scholar": skill_exists(existing, ["zotero-scholar", "zotero"]),
        },
        "toolchains": {
            "quarto": (shutil.which("quarto") is not None) or local_quarto.exists(),
            "pandoc": (shutil.which("pandoc") is not None) or local_pandoc.exists(),
            "manubot": (shutil.which("manubot") is not None) or ((Path.home() / ".local" / "bin" / "manubot").exists()),
            "xelatex": (shutil.which("xelatex") is not None) or ((WORKSPACE / ".paper-tools" / "bin" / "tectonic").exists()),
        },
        "paths": {
            "localQuarto": str(local_quarto) if local_quarto.exists() else None,
            "localPandoc": str(local_pandoc) if local_pandoc.exists() else None,
            "localManubot": str(Path.home() / ".local" / "bin" / "manubot") if (Path.home() / ".local" / "bin" / "manubot").exists() else None,
            "localTectonic": str(WORKSPACE / ".paper-tools" / "bin" / "tectonic") if (WORKSPACE / ".paper-tools" / "bin" / "tectonic").exists() else None,
        }
    }

    caps["summary"] = {
        "render_pdf_best": (
            "quarto+pandoc"
            if caps["toolchains"]["quarto"] and caps["toolchains"]["pandoc"]
            else ("pandoc" if caps["toolchains"]["pandoc"] else ("xelatex" if caps["toolchains"]["xelatex"] else "manual"))
        )
    }

    print(json.dumps(caps, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
