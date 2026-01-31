import sys
import os
import requests
from pathlib import Path
from bs4 import BeautifulSoup
import time
import json

try:
    from dotenv import load_dotenv
except ImportError:
    print("Missing dependency: python-dotenv. Install with 'pip install python-dotenv'.")
    sys.exit(1)

load_dotenv()

# Configuration
BASE_URL = "https://lms.ptit.edu.vn"
SLIDES_URL = f"{BASE_URL}/slides"
OUTPUT_DIR = Path(__file__).parent.parent / "downloaded_courses"
USER_AGENT = os.getenv("USER_AGENT", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
SESSION_ID = os.getenv("SESSION_ID", "")

def get_session():
    """Create requests session with cookies and headers"""
    session = requests.Session()
    session.headers.update({
        "User-Agent": USER_AGENT,
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Connection": "keep-alive",
    })
    if SESSION_ID:
        session.cookies.set("session_id", SESSION_ID)
    return session

def fetch_courses_page(session):
    """Fetch main slides page and extract course links"""
    print(f"🌐 Fetching: {SLIDES_URL}")
    try:
        response = session.get(SLIDES_URL, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Error fetching courses page: {e}")
        return None

def extract_course_links(html_content):
    """Extract course links from class 'row mx-n2 mt8 mb-4'"""
    soup = BeautifulSoup(html_content, "html.parser")
    
    # Find the container with courses
    courses_container = soup.find(class_="row mx-n2 mt8 mb-4")
    if not courses_container:
        print("❌ Could not find courses container (class='row mx-n2 mt8 mb-4')")
        return []
    
    courses = []
    seen_hrefs = set()  # Track unique course links to avoid duplicates
    
    # Find all course cards
    for card in courses_container.find_all("div", class_="card"):
        # Look for the card-title link with course name
        title_link = card.find("a", class_="card-title")
        if not title_link:
            continue
        
        href = title_link.get("href")
        if not href or not href.startswith("/slides/"):
            continue
        
        # Skip if we've already seen this course
        if href in seen_hrefs:
            continue
        seen_hrefs.add(href)
        
        # Get course title from the link text
        title = title_link.get_text(strip=True)
        if not title or title == "":
            title = "Unknown Course"
        
        # Build full URL
        full_url = BASE_URL + href if href.startswith("/") else href
        
        courses.append({
            "title": title,
            "url": full_url,
            "path": href
        })
    
    return courses

def download_course_page(session, course_url, course_title):
    """Download a course page HTML"""
    print(f"📥 Downloading: {course_title}")
    try:
        response = session.get(course_url, timeout=30)
        response.raise_for_status()
        return response.text
    except Exception as e:
        print(f"❌ Error downloading {course_title}: {e}")
        return None

def save_html(html_content, filename):
    """Save HTML content to file"""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    filepath = OUTPUT_DIR / filename
    
    try:
        filepath.write_text(html_content, encoding="utf-8")
        print(f"✅ Saved: {filepath}")
        return filepath
    except Exception as e:
        print(f"❌ Error saving {filename}: {e}")
        return None

def sanitize_filename(name):
    """Convert course title to safe filename"""
    # Remove invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "_")
    # Limit length
    return name[:100] + ".html"

def main():
    print("🚀 LMS PTIT Course Crawler\n")
    
    # Check for session ID
    if not SESSION_ID:
        print("⚠️  Warning: SESSION_ID not found in .env file")
        print("   You may not be able to access course pages that require authentication")
        print()
    
    # Create session
    session = get_session()
    
    # Fetch main page
    main_page = fetch_courses_page(session)
    if not main_page:
        print("❌ Failed to fetch courses page")
        sys.exit(1)
    
    # Extract course links
    courses = extract_course_links(main_page)
    if not courses:
        print("❌ No courses found")
        sys.exit(1)
    
    print(f"\n📚 Found {len(courses)} courses:\n")
    for idx, course in enumerate(courses, 1):
        print(f"  {idx}. {course['title']}")
    print()
    
    # Download each course
    downloaded_files = []
    for idx, course in enumerate(courses, 1):
        print(f"\n[{idx}/{len(courses)}] Processing: {course['title']}")
        
        # Download HTML
        html_content = download_course_page(session, course['url'], course['title'])
        if not html_content:
            continue
        
        # Save to file
        filename = sanitize_filename(course['title'])
        filepath = save_html(html_content, filename)
        if filepath:
            downloaded_files.append({
                "id": idx,
                "title": course['title'],
                "url": course['url'],
                "file": str(filepath)
            })
        
        # Be polite - wait between requests
        if idx < len(courses):
            time.sleep(1)
    
    # Save metadata
    metadata_file = OUTPUT_DIR / "courses_metadata.json"
    metadata_file.write_text(
        json.dumps({"courses": downloaded_files}, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )
    print(f"\n✅ Saved metadata: {metadata_file}")
    
    # Summary
    print(f"\n{'='*60}")
    print(f"✅ Downloaded {len(downloaded_files)}/{len(courses)} courses")
    print(f"📁 Output directory: {OUTPUT_DIR}")
    print(f"\nNext step: Run list_slides.py on the downloaded files:")
    print(f'  python scripts/list_slides.py "{OUTPUT_DIR}" --format mapping --out "{OUTPUT_DIR}/all_courses.json"')
    print(f"{'='*60}\n")

if __name__ == "__main__":
    main()
