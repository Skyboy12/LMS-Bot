import requests
import os
from dotenv import load_dotenv
from extract_slide_id import get_slide_ids_from_file

load_dotenv()
SESSION_ID = os.getenv('SESSION_ID')

SLIDE_IDs = [2]
ID = 0

def use_existing_session():
    url = "https://lms.ptit.edu.vn/slides/slide/set_completed"
    
    headers = {
        "Content-Type": "application/json",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/129.0.6668.71 Safari/537.36",
    }

    cookies = {
        "session_id": SESSION_ID
    }
    
    for SLIDE_ID in SLIDE_IDs:
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "slide_id": SLIDE_ID
            },
            "id": ID
        }

        response = requests.post(url, json=payload, headers=headers, cookies=cookies)

        if response.status_code == 200:
            print("Yêu cầu thành công!")
            print(response.json()) 
        else:
            print(f"Yêu cầu thất bại. Mã trạng thái: {response.status_code}")

if __name__ == "__main__":
    use_existing_session()
