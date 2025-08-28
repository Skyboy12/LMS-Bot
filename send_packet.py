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
                    channel_completion = result['channel_completion']
                    if channel_completion == 100:
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
        return quiz_data.get("quiz_ids", {}).get(str(ID), {})
    
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
        quiz_data = SEND_PACKET.QUIZ_DATA(ID)
        start = quiz_data.get("start", 0)
        amount = quiz_data.get("amount", 0)
        __ = quiz_data.get("list", [])
        if __ == []:
            return f"⏩ {ID} Chưa có dữ liệu quiz! Vui lòng báo lại"
        answer_list = [start]
        for i in range(1, amount):
            answer_list.append(answer_list[i-1] + __[i-1])

        test_point = 0
        test_time = 0
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
            if check[test_point]:
                test_point+=1
                test_time = 0
                continue
            else: 
                answer_list[test_point]+=1
                test_time+=1
                if test_time == __[test_point]:
                    test_point+=1
                    test_time = 0
                if test_point == amount:
                    break
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
    def ADD_QUIZ_DATA(ID, start, amount):
        with open(QUIZ_LIST, "r") as f:
            quiz_data = json.load(f)
        quiz_data["quiz_ids"][str(ID)] = {
            "start": start,
            "amount": amount,
            "list": [4] * amount
        }
        with open(QUIZ_LIST, "w") as f:
            json.dump(quiz_data, f)
    def FIX_QUIZ_DATA_LIST(ID, list_):
        with open(QUIZ_LIST, "r") as f:
            quiz_data = json.load(f)
        quiz_data["quiz_ids"][str(ID)]["list"] = list_
        with open(QUIZ_LIST, "w") as f:
            json.dump(quiz_data, f)
