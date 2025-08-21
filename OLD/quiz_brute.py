import requests
import json
import itertools

SESSION_ID = "988bb48080930d59c74693ab35258228b4ec69c0"

SLIDE_DATA = {
    166: {"start_ans_id": 1640, "num_submits": 10},
    167: {"start_ans_id": 1680, "num_submits": 10},
    168: {"start_ans_id": 1760, "num_submits": 10},
    169: {"start_ans_id": 1800, "num_submits": 10},
    170: {"start_ans_id": 1840, "num_submits": 15}, 
    171: {"start_ans_id": 1900, "num_submits": 10},
    172: {"start_ans_id": 1940, "num_submits": 10},
    173: {"start_ans_id": 1980, "num_submits": 10},
    174: {"start_ans_id": 2020, "num_submits": 10}
}

def submit_quiz():
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

        ranges = [[start_ans_id + i * 4 + delta for delta in range(5)] for i in range(num_submits)]

        for answer_list in itertools.product(*ranges): 
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
    submit_quiz()
    print("🏁 Hoàn thành kiểm tra tất cả slide!")
