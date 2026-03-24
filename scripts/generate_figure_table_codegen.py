#!/usr/bin/env python3
import argparse
import csv
import json
from pathlib import Path

PY_TEMPLATE = '''#!/usr/bin/env python3
import csv
from pathlib import Path

try:
    import matplotlib.pyplot as plt
except Exception as e:
    raise SystemExit(f"matplotlib not available: {{e}}")


def read_rows(path: Path):
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def main():
    data_path = Path(__file__).resolve().parents[2] / "data" / "{data_name}"
    output_path = Path(__file__).resolve().parents[2] / "figures" / "{output_name}"
    output_path.parent.mkdir(parents=True, exist_ok=True)
    rows = read_rows(data_path)
    if not rows:
        raise SystemExit("empty csv")

    x = [row.get("label", "") for row in rows]
    y = [float(row.get("value", 0)) for row in rows]

    plt.figure(figsize=(8, 4.8))
    plt.bar(x, y)
    plt.title("{title}")
    plt.xlabel("Category")
    plt.ylabel("Value")
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    print(output_path)


if __name__ == "__main__":
    main()
'''

CSV_ROWS = [
    ["label", "value"],
    ["baseline", "0.72"],
    ["method-a", "0.79"],
    ["method-b", "0.83"],
]


def load_json(path: str) -> dict:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def ensure_text(path: Path, content: str):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


def ensure_csv(path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerows(CSV_ROWS)


def scaffold_for_item(base_dir: Path, item: dict):
    codegen = item.get("codegen") or {}
    if not codegen.get("enabled"):
        return

    script_path = base_dir / codegen["scriptPath"]
    data_path = base_dir / codegen["dataPath"]
    output_path = base_dir / codegen["outputPath"]
    output_path.parent.mkdir(parents=True, exist_ok=True)

    if item.get("kind") == "figure":
        ensure_csv(data_path)
        ensure_text(
            script_path,
            PY_TEMPLATE.format(
                data_name=data_path.name,
                output_name=output_path.name,
                title=item.get("title") or item.get("label")
            )
        )
    else:
        ensure_csv(output_path)
        ensure_csv(data_path)
        ensure_text(
            script_path,
            "#!/usr/bin/env python3\nfrom pathlib import Path\nprint('table artifact already stored as CSV placeholder')\n"
        )


def main():
    parser = argparse.ArgumentParser(description="Generate code/data scaffolding from figure-table plan")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--base-dir", required=True)
    args = parser.parse_args()

    plan = load_json(args.plan)
    base_dir = Path(args.base_dir)

    created = []
    for chapter in plan.get("chapters", []):
        for item in chapter.get("items", []):
            scaffold_for_item(base_dir, item)
            codegen = item.get("codegen") or {}
            created.append({
                "label": item.get("label"),
                "scriptPath": str(base_dir / codegen.get("scriptPath", "")),
                "dataPath": str(base_dir / codegen.get("dataPath", "")),
                "outputPath": str(base_dir / codegen.get("outputPath", "")),
            })

    print(json.dumps({"created": created}, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
