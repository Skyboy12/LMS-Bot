import requests
import json
import os
import sys
import itertools
from dotenv import load_dotenv
from extract_quiz_id import get_quiz_ids_from_file

load_dotenv()
SESSION_ID = os.getenv('SESSION_ID')

quiz_ids = get_quiz_ids_from_file('Lms.html')

with open('quiz_question', 'r') as file:
    lines = file.readlines()

SLIDE_DATA = {}
for i, quiz_id in enumerate(quiz_ids):
    if quiz_id and i < len(lines):
        parts = lines[i].strip().split()
        start_ans_id = int(parts[0])
        num_submits = int(parts[1])
        stats = int(parts[2])==0
        SLIDE_DATA[quiz_id] = {"start_ans_id": start_ans_id, "num_submits": num_submits, "stats": stats}

def extract_answer(response_text,num_submits):
    try:
        response_json = json.loads(response_text)
        answers = response_json.get("result", {}).get("answers", {})
        is_correct_list = [answers.get(key, {}).get("is_correct", False) for key in answers.keys()]
        return (is_correct_list + [False] * 10)[:num_submits]
    except json.JSONDecodeError:
        return [False] * num_submits

def submit_quiz():
    url = "https://lms.ptit.edu.vn/slides/slide/quiz/submit"
    headers = {
        "Accept": "*/*",
        "Content-Type": "application/json",
        "Cookie": f"session_id={SESSION_ID}",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/133.0.0.0 Safari/537.36 OPR/118.0.0.0"
    }

    for slide_id, data in SLIDE_DATA.items():
        start_ans_id = data["start_ans_id"]
        num_submits = data["num_submits"]
        stats = data["stats"]
        if stats:
            continue

        print(f"🔎 Đang thử câu {slide_id} với {num_submits} đáp án, bắt đầu từ {start_ans_id}")

        answer_list = [start_ans_id + i * 4 for i in range(num_submits)]
        test_point = 0
        test_time = 0
        brute_force = False
        while True:
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
            print(f"-> Status: {response.status_code}")
            print(f"-> Response: {response_text}")
            check = extract_answer(response_text, num_submits)
            print(check)
            if check[test_point]:
                test_point+=1
                test_time = 0
                continue
            else: 
                answer_list[test_point]+=1
                test_time+=1
                if test_time == 4:
                    test_point+=1
                    test_time = 0
                if test_point == num_submits:
                    break
            
            try:
                response_json = json.loads(response_text)
                if response_json.get("result", {}).get("error") == "slide_quiz_done":
                    print(f"⏩ Bỏ qua {slide_id} vì đã hoàn thành!")
                    break
                if response_json.get("result", {}).get("error") == "slide_quiz_incomplete":
                    print(f"⏩ {slide_id} cần chạy brute force!")
                    brute_force = True
                    break
            except json.JSONDecodeError:
                pass
        if brute_force:
            print(f"🔄 Đang chạy brute force")
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
                    if response_json.get("result", {}).get("error") == "user":
                        break
                except json.JSONDecodeError:
                    pass
        
        print(f"🔄 Hoàn thành kiểm tra {slide_id}")

def __test__():
    print("Testing SLIDE_DATA:")
    print(f"Extracted Quiz IDs: {quiz_ids}")
    for quiz_id, data in SLIDE_DATA.items():
        print(f"Quiz ID: {quiz_id}, Data: {data}")
    test_response = '{"jsonrpc": "2.0", "id": 1, "result": {"answers": {"407": {"is_correct": false, "comment": false}, "408": {"is_correct": false, "comment": false}, "409": {"is_correct": false, "comment": false}, "410": {"is_correct": false, "comment": false}, "411": {"is_correct": false, "comment": false}, "412": {"is_correct": false, "comment": false}, "413": {"is_correct": false, "comment": false}, "414": {"is_correct": true, "comment": false}, "415": {"is_correct": true, "comment": false}, "416": {"is_correct": false, "comment": false}}, "completed": false, "channel_completion": 23, "quizKarmaWon": 0, "quizKarmaGain": 2, "quizAttemptsCount": 43, "rankProgress": {}}}'
    answer_list = extract_answer(test_response)
    print(f"Extracted Answers: {answer_list}")
    print("Testing SLIDE_DATA:")
    print(f"Extracted Quiz IDs: {quiz_ids}")
    for quiz_id, data in SLIDE_DATA.items():
        print(f"Quiz ID: {quiz_id}, Data: {data}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "__test__":
        __test__()
    else:
        submit_quiz()
        print("🏁 Hoàn thành kiểm tra tất cả slide!")
