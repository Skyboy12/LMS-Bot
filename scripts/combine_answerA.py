from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import List, Dict, Any


def main(base_dir: str | None = None) -> None:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    # Determine base folder containing the HTML and JSON files
    if base_dir is None:
        base = Path(__file__).resolve().parents[1] / 'Triết Mác-LêNin'
    else:
        base = Path(base_dir)

    if not base.exists():
        print(f"Base folder not found: {base}")
        sys.exit(1)

    json_files = sorted([p for p in base.iterdir() if p.is_file() and p.suffix.lower() == '.json' and p.name.endswith('.answerA.json')])

    combined: List[Dict[str, Any]] = []
    for jf in json_files:
        try:
            data = json.loads(jf.read_text(encoding='utf-8'))
            # Infer original HTML filename (strip the .answerA.json suffix)
            name = jf.name
            source_html = name[:-len('.answerA.json')] + '.html' if name.endswith('.answerA.json') else jf.with_suffix('.html').name
            if isinstance(data, list):
                for item in data:
                    if isinstance(item, dict):
                        combined.append({
                            'source_file': source_html,
                            **item,
                        })
            else:
                print(f"Warning: Skipping non-list JSON in {jf.name}")
        except Exception as e:
            print(f"Error reading {jf.name}: {e}")

    out_path = base / 'all_answerA.json'
    out_path.write_text(json.dumps(combined, ensure_ascii=False, indent=2), encoding='utf-8')

    print(f"Merged {len(json_files)} files into {out_path.name}")
    print(f"Total records: {len(combined)}")


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)
