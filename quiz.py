import requests
import json
import itertools
import get_cookies

SLIDE_DATA = {}

def submit_quiz(email, password):
    SESSION_ID = get_cookies.main(email, password, headless=False)
    url = "https://lms.ptit.edu.vn/slides/slide/quiz/submit"
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Cookie": f"session_id={SESSION_ID}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36"
    }

    for slide_id, data in SLIDE_DATA.items():
        start_ans_id = data["start_ans_id"]
        num_submits = data["num_submits"]

        print(f"🔎 Đang thử câu {slide_id} với {num_submits} đáp án, bắt đầu từ {start_ans_id}")

        # Thay vì lưu tất cả tổ hợp, ta tạo từng cái một
        ranges = [[start_ans_id + i * 4 + delta for delta in range(5)] for i in range(num_submits)]

        for answer_list in itertools.product(*ranges):  # Lặp trực tiếp
            print(f"Thử {list(answer_list)}")

            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "slide_id": slide_id,
                    "answer_ids": list(answer_list)
                }
            }

            response = requests.post(url, json=payload, headers=headers)
            response_text = response.text
            print(f"-> Status: {response.status_code}, Response: {response_text}")

            try:
                response_json = json.loads(response_text)
                if response_json.get("result", {}).get("error") == "slide_quiz_done":
                    print(f"⏩ Bỏ qua {slide_id} vì đã hoàn thành!")
                    break
            except json.JSONDecodeError:
                pass
        
        print(f"🔄 Hoàn thành kiểm tra {slide_id}")

if __name__ == "__main__":
    EMAIL = input("Nhập Email: ").strip()
    PASSWORD = input("Nhập Password: ").strip()
    submit_quiz(EMAIL, PASSWORD)
    print("🏁 Hoàn thành kiểm tra tất cả slide!")
