import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

SLIDE_URL = os.getenv("SLIDE_URL")
QUIZ_URL = os.getenv("QUIZ_URL")
USER_AGENT = os.getenv("USER_AGENT")
H_DATA = os.getenv("H_DATA")
QUIZ_LIST = os.getenv("QUIZ_LIST")

class SEND_PACKET:
    def SLIDE(SESSION_ID, ID):
        headers = {
            "Content-Type": H_DATA,
            "Accept": H_DATA,
            "User-Agent": USER_AGENT
        }
        cookies = {
            "session_id": SESSION_ID
        }
        payload = {
            "jsonrpc": "2.0",
            "method": "call",
            "params": {
                "slide_id": ID
            },
            "id": 0
        }
        response = requests.post(SLIDE_URL, json=payload, headers=headers, cookies=cookies)
        if response.status_code == 200:
            message = "Không có thông báo từ máy chủ."
            try:
                response_json = response.json()
                result = response_json.get("result", {})
                if 'error' in result:
                    error = result['error']
                    if error == "slide_not_found":
                        message = "Không tìm thấy slide."
                    elif error == "slide_access":
                        message = "Không có quyền truy cập vào slide."
                    elif error == "public_user":
                        message = "Người dùng công khai không thể truy cập slide. Vui lòng kiểm tra lại sessionID"
                    else:
                        message = 'Đã xảy ra lỗi không xác định.'
                elif 'channel_completion' in result:
                    message = "Đã hoàn thành slide. Vui lòng kiểm tra và báo lại nếu có vấn đề."
                elif 'error' in response_json:
                        data = response_json['error']['data']
                        message = data.get('message', 'Đã xảy ra lỗi không xác định.')

            except (ValueError, KeyError):
                message = "Không thể phân tích dữ liệu trả về từ máy chủ."
            return ["Yêu cầu thành công!", response.json(), message]
        else:
            message = "Kết nối từ bot đến máy chủ thất bại. Vui lòng thử lại sau"
            return ["Yêu cầu thất bại", response.status_code, message]

    def QUIZ_DATA(ID):
        with open(QUIZ_LIST, "r") as f:
            quiz_data = json.load(f)
        quiz_ids = quiz_data.get("quiz_ids", {})
        quiz_list = quiz_ids.get(str(ID), [])
        quiz_start = quiz_data.get("quiz_data", {}).get("question_answer_start", [])
        quiz_amount = quiz_data.get("quiz_data", {}).get("question_amount", [])
        quiz_start_list = []
        quiz_amount_list = []
        if not (len(quiz_start_list) == len(quiz_list) and len(quiz_amount_list) == len(quiz_list)):
            raise ValueError("Dữ liệu quiz không hợp lệ trong quiz_list.json")
        for quiz_id in quiz_list:
            quiz_start_list.append(quiz_start[quiz_id])
            quiz_amount_list.append(quiz_amount[quiz_id])
        return quiz_list, quiz_start_list, quiz_amount_list
    
    def extract_answer(response_text,num_submits):
        try:
            response_json = json.loads(response_text)
            answers = response_json.get("result", {}).get("answers", {})
            is_correct_list = [answers.get(key, {}).get("is_correct", False) for key in answers.keys()]
            return (is_correct_list + [False] * num_submits)[:num_submits]
        except json.JSONDecodeError:
            return [False] * num_submits
        
    def QUIZ(SESSION_ID, ID):
        headers = {
            "Accept": "*/*",
            "Content-Type": H_DATA,
            "Cookie": f"session_id={SESSION_ID}",
            "User-Agent": USER_AGENT
        }

        quiz_id_list, question_answer_start, question_amount = SEND_PACKET.QUIZ_DATA(ID)
        amount = len(quiz_id_list)
        answer_list = question_answer_start.copy()
        
        while True:
            print(f"Thử {list(answer_list)}")

            payload = {
                "id": 1,
                "jsonrpc": "2.0",
                "method": "call",
                "params": {
                    "slide_id": ID,
                    "answer_ids": list(answer_list)
                }
            }

            response = requests.post(QUIZ_URL, json=payload, headers=headers)
            response_text = response.text

            check = SEND_PACKET.extract_answer(response_text, amount)

            for i in range(amount):
                if not check[i] and question_amount[i] > 1:
                    answer_list[i] += 1
                    question_amount[i] -= 1
                    
            print(f"-> Status: {response.status_code}, Response: {response_text}")
            
            try:
                response_json = json.loads(response_text)
                error = response_json.get("result", {}).get("error")
                if error == "slide_quiz_done":
                    return f"⏩ {ID} Đã hoàn thành!"
                if error == "slide_quiz_incomplete":
                    return f"⏩ {ID} Có lỗi! Vui lòng kiểm tra lại!"
                if error == "slide_access":
                    return f"⏩ {ID} Bạn không có quyền truy cập!"
            except json.JSONDecodeError:
                pass

    def ADD_QUIZ_DATA(ID, quiz_id_list, question_answer_start, question_amount):
        with open(QUIZ_LIST, "r") as f:
            quiz_data = json.load(f)
        # Thêm dữ liệu quiz mới vào quiz_data
        # Tìm giá trị lớn nhất hiện có trong quiz_id_list và so sánh với question_answer_start và question_amount tương ứng để thêm dữ liệu mới
        max_quiz_id_list = max(quiz_id_list) if quiz_id_list else 0
        length_question_answer_start_in_quiz_data = len(quiz_data["quiz_data"]["question_answer_start"])
        length_question_amount_in_quiz_data = len(quiz_data["quiz_data"]["question_amount"])
        if max_quiz_id_list >= length_question_answer_start_in_quiz_data:
            for i in range(length_question_answer_start_in_quiz_data, max_quiz_id_list + 1):
                quiz_data["quiz_data"]["question_answer_start"][i] = 0
        if max_quiz_id_list >= length_question_amount_in_quiz_data:
            for i in range(length_question_amount_in_quiz_data, max_quiz_id_list + 1):
                quiz_data["quiz_data"]["question_amount"][i] = 0
        # Cập nhật quiz_ids
        quiz_data["quiz_ids"][str(ID)] = quiz_id_list
        for i in range(len(quiz_id_list)):
            quiz_data["quiz_data"]["question_answer_start"][quiz_id_list[i]] = question_answer_start[i]
            quiz_data["quiz_data"]["question_amount"][quiz_id_list[i]] = question_amount[i]
        with open(QUIZ_LIST, "w") as f:
            json.dump(quiz_data, f)
        return "Đã thêm dữ liệu quiz thành công!"

if __name__ == "test_quiz_data":
    print("Nhập vào ID quiz:")
    id = int(input())
    quiz_ids, starts, amounts = SEND_PACKET.QUIZ_DATA(id)

    print(f"ID quiz: {id}")
    print(f"Quiz IDs: {quiz_ids}")
    print(f"Starts: {starts}")
    print(f"Amounts: {amounts}")