from __future__ import annotations
import json
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple


def ensure_len(lst: List[int], idx: int) -> None:
    while len(lst) <= idx:
        lst.append(0)


def load_all_answerA(base_root: Path, user_path: Path | None = None) -> Tuple[Path, List[Dict[str, Any]]]:
    # If user provided a direct path or folder, use it
    if user_path is not None:
        if user_path.is_dir():
            candidate = user_path / 'all_answerA.json'
            if candidate.exists():
                data = json.loads(candidate.read_text(encoding='utf-8'))
                if isinstance(data, list):
                    return candidate, data
        elif user_path.is_file():
            data = json.loads(user_path.read_text(encoding='utf-8'))
            if isinstance(data, list):
                return user_path, data

    # Prefer Triết Mác-LêNin/all_answerA.json; then any immediate subfolder's all_answerA.json; fallback to workspace root
    tri_folder = base_root / 'Triết Mác-LêNin'
    candidates = [tri_folder / 'all_answerA.json']
    # scan immediate subdirectories
    for sub in base_root.iterdir():
        if sub.is_dir():
            cand = sub / 'all_answerA.json'
            if cand.exists():
                candidates.append(cand)
    candidates.append(base_root / 'all_answerA.json')
    for p in candidates:
        if p.exists():
            data = json.loads(p.read_text(encoding='utf-8'))
            if not isinstance(data, list):
                raise ValueError(f"Unexpected format in {p}")
            return p, data
    raise FileNotFoundError("all_answerA.json not found in expected locations")


def main() -> None:
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

    base = Path(__file__).resolve().parents[1]
    # Optional path argument (folder or file)
    arg_path = Path(sys.argv[1]) if len(sys.argv) > 1 else None
    all_path, records = load_all_answerA(base, arg_path)

    quiz_path = base / 'quiz_list.json'
    if not quiz_path.exists():
        print(f"quiz_list.json not found at {quiz_path}")
        sys.exit(1)

    # Backup existing file
    backup_path = base / 'quiz_list.json.preupdate.bak'
    try:
        backup_path.write_text(quiz_path.read_text(encoding='utf-8'), encoding='utf-8')
    except Exception as e:
        print(f"Warning: failed to write backup: {e}")

    quiz = json.loads(quiz_path.read_text(encoding='utf-8'))
    quiz_data = quiz.setdefault('quiz_data', {})
    arr_amount: List[int] = quiz_data.setdefault('question_ammount', [])
    arr_start: List[int] = quiz_data.setdefault('question_answer_start', [])

    updated = 0
    for rec in records:
        try:
            qid = int(rec['data_question_id'])
            start = int(rec['first_answer_id'])
            count = int(rec['answer_count'])
        except Exception:
            continue
        ensure_len(arr_amount, qid)
        ensure_len(arr_start, qid)
        arr_amount[qid] = count
        arr_start[qid] = start
        updated += 1

    # Write back
    quiz_path.write_text(json.dumps(quiz, ensure_ascii=False, indent=4), encoding='utf-8')

    print(f"Updated {updated} records from {all_path.name} into {quiz_path.name}")


if __name__ == '__main__':
    main()
