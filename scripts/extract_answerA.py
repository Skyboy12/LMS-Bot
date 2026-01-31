from __future__ import annotations
import json
import sys
from pathlib import Path
from html.parser import HTMLParser
from typing import List, Dict, Optional


class QuizParser(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.current_qid: Optional[int] = None
        self.depth: int = 0
        self.first_answer_id: Optional[int] = None
        self.answer_count: int = 0
        self.results: List[Dict[str, int]] = []

    def handle_starttag(self, tag: str, attrs_list):
        attrs = {k: v for k, v in attrs_list}
        # Start of a question block
        if tag == 'div':
            classes = attrs.get('class', '') or ''
            if self.current_qid is None and 'o_wslides_js_lesson_quiz_question' in classes and 'data-question-id' in attrs:
                # Enter a question block
                try:
                    self.current_qid = int(attrs['data-question-id'])
                except Exception:
                    # If not numeric, skip this block
                    self.current_qid = None
                    self.depth = 0
                    self.first_answer_id = None
                    self.answer_count = 0
                    return
                self.depth = 1  # depth for this question's root div
                self.first_answer_id = None
                self.answer_count = 0
                return
            # Nested div inside an active question
            if self.current_qid is not None:
                self.depth += 1
                return

        # Inside a question: count answers and record the first one's id
        if self.current_qid is not None and tag == 'a':
            classes = (attrs.get('class', '') or '')
            if 'o_wslides_quiz_answer' in classes:
                self.answer_count += 1
                if self.first_answer_id is None:
                    aid = attrs.get('data-answer-id')
                    if aid is not None:
                        try:
                            self.first_answer_id = int(aid)
                        except Exception:
                            # ignore non-int ids
                            pass

    def handle_endtag(self, tag: str):
        if self.current_qid is not None and tag == 'div':
            self.depth -= 1
            if self.depth == 0:
                # Closing the question block
                if self.current_qid is not None and self.first_answer_id is not None:
                    self.results.append({
                        'data_question_id': int(self.current_qid),
                        'first_answer_id': int(self.first_answer_id),
                        'answer_count': int(self.answer_count),
                    })
                # Reset state
                self.current_qid = None
                self.first_answer_id = None
                self.answer_count = 0


def extract_from_html(html_text: str) -> List[Dict[str, int]]:
    parser = QuizParser()
    parser.feed(html_text)
    return parser.results


def process_file(file_path: Path) -> List[Dict[str, int]]:
    text = file_path.read_text(encoding='utf-8', errors='ignore')
    return extract_from_html(text)


def main(base_dir: Optional[str] = None) -> None:
    # Ensure stdout can handle UTF-8 characters when printing filenames
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass
    # Base directory containing the HTML files
    if base_dir is None:
        base = Path(__file__).resolve().parents[1] / 'Triết Mác-LêNin'
    else:
        base = Path(base_dir)

    if not base.exists():
        print(f"Base folder not found: {base}")
        return

    html_files = [p for p in base.iterdir() if p.is_file() and p.suffix.lower() == '.html']

    written = []
    for html_file in html_files:
        try:
            results = process_file(html_file)
        except Exception as e:
            print(f"Error processing {html_file.name}: {e}")
            continue

        out_path = html_file.with_suffix('.answerA.json')
        try:
            out_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
            written.append(out_path.name)
        except Exception as e:
            print(f"Error writing {out_path.name}: {e}")

    print("Written files:")
    for name in written:
        try:
            print(f" - {name}")
        except Exception:
            # Fallback to ascii-safe output
            try:
                print(" - " + name.encode('ascii', 'ignore').decode('ascii'))
            except Exception:
                pass


if __name__ == '__main__':
    arg = sys.argv[1] if len(sys.argv) > 1 else None
    main(arg)
