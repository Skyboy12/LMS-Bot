import sys
import argparse
from pathlib import Path

try:
    from bs4 import BeautifulSoup
except ImportError:
    print("Missing dependency: bs4. Install with 'pip install beautifulsoup4'.")
    sys.exit(1)


ICON_YOUTUBE = "fa fa-youtube-play py-2 mx-2"
ICON_QUESTION = "fa fa-question-circle-o py-2 mx-2"


def parse_html(html_text: str):
    soup = BeautifulSoup(html_text, "html.parser")

    # Find the course title from class="tieu-de"
    course_title_elem = soup.find(class_="tieu-de")
    course_title = course_title_elem.get_text(strip=True) if course_title_elem else "Unknown Course"

    # Order-preserving traversal: find list items containing slide entries
    # Track ALL occurrences in order to maintain proper sequencing
    slides_in_order = []  # List of (slide_id, icon_type) tuples

    # Strategy: for each element that has data-slide-id, look for the direct child icon
    for li in soup.find_all("li", attrs={"data-slide-id": True}):
        slide_id = li.get("data-slide-id")
        if not slide_id:
            continue

        # Skip if slide-id equals category-id (category title slide)
        category_id = li.get("data-category-id")
        if category_id and slide_id == category_id:
            continue

        # Look for DIRECT child <i> tag (the icon next to the slide name)
        # This is the icon that appears in the structure: <li><i class="fa ...">
        icon_i = li.find("i", recursive=False)
        if not icon_i:
            # If not a direct child, look for first <i> within the li
            icon_i = li.find("i")
        
        if not icon_i:
            continue

        # Get the full class string
        classes = icon_i.get("class", [])
        if isinstance(classes, list):
            class_str = " ".join(classes)
        else:
            class_str = classes

        # Determine icon type
        icon_type = None
        if "fa-youtube-play" in class_str:
            icon_type = "youtube"
        elif "fa-question-circle-o" in class_str:
            icon_type = "question"
        else:
            continue

        slides_in_order.append((int(slide_id), icon_type))

    # Split into youtube and question lists while preserving order
    youtube_ids = [sid for sid, itype in slides_in_order if itype == "youtube"]
    question_ids = [sid for sid, itype in slides_in_order if itype == "question"]

    return youtube_ids, question_ids, slides_in_order, course_title


def build_id_type_mapping_ordered(slides_in_order):
    """Build ordered mapping of id -> type preserving exact HTML appearance order.
    
    Args:
        slides_in_order: List of (slide_id, icon_type) tuples in appearance order
    
    Returns:
        OrderedDict with slide_id -> type_name mapping
    """
    from collections import OrderedDict
    mapping = OrderedDict()
    for slide_id, icon_type in slides_in_order:
        # Map icon_type to type name
        type_name = "slide" if icon_type == "youtube" else "quiz"
        # First seen wins
        if slide_id not in mapping:
            mapping[slide_id] = type_name
    return mapping


def main():
    parser = argparse.ArgumentParser(description="List and categorize data-slide-id by icon.")
    parser.add_argument("html_path", help="Path to HTML file or directory containing HTML files")
    parser.add_argument("--format", choices=["text", "json", "mapping"], default="text", help="Output format")
    parser.add_argument("--out", help="Optional path to write JSON output (for --format json or mapping)")
    parser.add_argument("--pattern", default="*.html", help="File pattern to match (default: *.html)")
    args = parser.parse_args()

    path = Path(args.html_path)
    
    # Collect HTML files
    html_files = []
    if path.is_file():
        html_files = [path]
    elif path.is_dir():
        html_files = sorted(path.glob(args.pattern))
        if not html_files:
            print(f"❌ No HTML files found in: {path}")
            sys.exit(1)
    else:
        print(f"❌ Path not found: {path}")
        sys.exit(1)

    # Process all HTML files
    all_courses = {}
    for idx, html_file in enumerate(html_files, start=1):
        print(f"📄 Processing ({idx}/{len(html_files)}): {html_file.name}")
        html_text = html_file.read_text(encoding="utf-8", errors="ignore")
        youtube_ids, question_ids, slides_in_order, course_title = parse_html(html_text)
        
        if args.format == "text":
            print(f"📚 Course: {course_title}")
            print("🎬 YouTube slides (order of appearance):")
            print(", ".join(map(str, youtube_ids)) or "<none>")
            print()
            print("❓ Question slides (order of appearance):")
            print(", ".join(map(str, question_ids)) or "<none>")
            print("\n" + "="*60 + "\n")
        else:
            # Store for JSON output
            mapping = build_id_type_mapping_ordered(slides_in_order)
            slides_dict = {str(k): v for k, v in mapping.items()}
            all_courses[str(idx)] = {
                "name": course_title,
                "slides": slides_dict
            }
    
    # Output JSON formats
    if args.format in ("json", "mapping"):
        import json
        if args.format == "json":
            # Legacy format for single file
            if len(html_files) == 1:
                youtube_ids, question_ids, slides_in_order, _ = parse_html(html_files[0].read_text(encoding="utf-8", errors="ignore"))
                payload = {"youtube": youtube_ids, "question": question_ids}
            else:
                payload = all_courses
        else:
            payload = all_courses

        if args.out:
            out_path = Path(args.out)
            out_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
            print(f"✅ Wrote JSON to: {out_path}")
            print(f"📊 Total courses: {len(all_courses)}")
        else:
            print(json.dumps(payload, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
