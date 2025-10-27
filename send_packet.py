import requests
import os
import json
from dotenv import load_dotenv

load_dotenv()

SLIDE_URL = os.getenv("SLIDE_URL")
QUIZ_URL = os.getenv("QUIZ_URL")
USER_AGENT = os.getenv("USER_AGENT")
H_DATA = os.getenv("H_DATA")

# Fallback to local quiz_list.json if QUIZ_LIST is not set in environment
QUIZ_LIST = os.getenv("QUIZ_LIST") or os.path.join(os.path.dirname(__file__), "quiz_list.json")

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
        """Đọc dữ liệu quiz cho slide ID.

        Trả về:
        - quiz_id_list: list[int] các quiz-id theo slide
        - question_answer_start_list: list[int] vị trí bắt đầu trả lời cho từng quiz-id
        - question_amount_list: list[int] số lượng đáp án có thể thử cho từng quiz-id

        Ném ValueError nếu dữ liệu không hợp lệ hoặc không tìm thấy ID.
        """
        # Đảm bảo file tồn tại
        if not os.path.isfile(QUIZ_LIST):
            raise FileNotFoundError(f"Không tìm thấy file QUIZ_LIST tại: {QUIZ_LIST}")

        with open(QUIZ_LIST, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)

        quiz_ids_map = quiz_data.get("quiz_ids", {})
        quiz_id_list = quiz_ids_map.get(str(ID))
        if not quiz_id_list:
            raise ValueError(f"Không tìm thấy quiz_ids cho slide ID={ID}")

        quiz_data_block = quiz_data.get("quiz_data", {})
        start_arr = quiz_data_block.get("question_answer_start", [])
        # Hỗ trợ cả key bị gõ sai 'question_ammount' lẫn 'question_amount'
        amount_arr = quiz_data_block.get("question_amount")
        if amount_arr is None:
            amount_arr = quiz_data_block.get("question_ammount", [])

        if not isinstance(start_arr, list) or not isinstance(amount_arr, list):
            raise ValueError("question_answer_start hoặc question_amount/ammount không phải dạng list")

        question_answer_start_list: list[int] = []
        question_amount_list: list[int] = []

        max_index_needed = max(quiz_id_list)
        if max_index_needed >= len(start_arr):
            raise ValueError(
                f"Index vượt quá giới hạn trong question_answer_start: cần {max_index_needed}, có {len(start_arr)-1}"
            )
        if max_index_needed >= len(amount_arr):
            raise ValueError(
                f"Index vượt quá giới hạn trong question_amount/ammount: cần {max_index_needed}, có {len(amount_arr)-1}"
            )

        for qid in quiz_id_list:
            question_answer_start_list.append(start_arr[qid])
            question_amount_list.append(amount_arr[qid])

        # Kiểm tra độ dài khớp
        if not (len(question_answer_start_list) == len(quiz_id_list) == len(question_amount_list)):
            raise ValueError("Độ dài dữ liệu không khớp giữa quiz_ids, question_answer_start và question_amount/ammount")

        return quiz_id_list, question_answer_start_list, question_amount_list
    
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
        # Validate input lengths
        if not (len(quiz_id_list) == len(question_answer_start) == len(question_amount)):
            raise ValueError("Đầu vào không hợp lệ: độ dài quiz_id_list, question_answer_start, question_amount phải bằng nhau")

        if not os.path.isfile(QUIZ_LIST):
            raise FileNotFoundError(f"Không tìm thấy file QUIZ_LIST tại: {QUIZ_LIST}")

        with open(QUIZ_LIST, "r", encoding="utf-8") as f:
            quiz_data = json.load(f)

        if "quiz_data" not in quiz_data:
            quiz_data["quiz_data"] = {}

        qdata = quiz_data["quiz_data"]
        # Hỗ trợ cả 'question_amount' và 'question_ammount' (bị gõ sai)
        amount_key = "question_amount" if "question_amount" in qdata else ("question_ammount" if "question_ammount" in qdata else "question_amount")

        if "question_answer_start" not in qdata or not isinstance(qdata.get("question_answer_start"), list):
            qdata["question_answer_start"] = []
        if amount_key not in qdata or not isinstance(qdata.get(amount_key), list):
            qdata[amount_key] = []

        start_arr = qdata["question_answer_start"]
        amount_arr = qdata[amount_key]

        max_index = max(quiz_id_list) if quiz_id_list else -1
        # Mở rộng mảng tới chỉ số lớn nhất cần thiết
        while len(start_arr) <= max_index:
            start_arr.append(0)
        while len(amount_arr) <= max_index:
            amount_arr.append(0)

        # Cập nhật quiz_ids map
        if "quiz_ids" not in quiz_data or not isinstance(quiz_data.get("quiz_ids"), dict):
            quiz_data["quiz_ids"] = {}
        quiz_data["quiz_ids"][str(ID)] = list(quiz_id_list)

        # Ghi dữ liệu cho từng quiz-id tương ứng
        for idx, qid in enumerate(quiz_id_list):
            start_arr[qid] = question_answer_start[idx]
            amount_arr[qid] = question_amount[idx]

        with open(QUIZ_LIST, "w", encoding="utf-8") as f:
            json.dump(quiz_data, f, ensure_ascii=False, indent=4)
        return "Đã thêm dữ liệu quiz thành công!"

if __name__ == "__main__":
    try:
        print("Nhập vào ID quiz:")
        id_value = int(input())
        quiz_ids, starts, amounts = SEND_PACKET.QUIZ_DATA(id_value)

        print(f"ID quiz: {id_value}")
        print(f"Quiz IDs: {quiz_ids}")
        print(f"Starts: {starts}")
        print(f"Amounts: {amounts}")
    except Exception as e:
        print(f"Lỗi khi đọc dữ liệu quiz: {e}")