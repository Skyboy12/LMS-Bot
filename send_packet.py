import requests
import os
import json
import time
from dotenv import load_dotenv
from bs4 import BeautifulSoup

load_dotenv()

SLIDE_URL = os.getenv("SLIDE_URL")
QUIZ_URL = os.getenv("QUIZ_URL")
USER_AGENT = os.getenv("USER_AGENT")
H_DATA = os.getenv("H_DATA")

# Fallback to local quiz_list.json if QUIZ_LIST is not set in environment
QUIZ_LIST = os.getenv("QUIZ_LIST") or os.path.join(os.path.dirname(__file__), "quiz_list.json")
ALL_COURSES = os.path.join(os.path.dirname(__file__), "List_môn", "all_courses.json")

class SEND_PACKET:
    def PING():
        """Ping server để kiểm tra kết nối.
        
        Trả về:
        - status_code: HTTP status code
        - response_time: thời gian phản hồi (ms)
        - message: thông báo kết quả
        """
        import time
        try:
            headers = {
                "Content-Type": H_DATA,
                "Accept": H_DATA,
                "User-Agent": USER_AGENT
            }
            payload = {
                "jsonrpc": "2.0",
                "method": "call",
                "params": {},
                "id": 0
            }
            
            start_time = time.time()
            response = requests.post(SLIDE_URL, json=payload, headers=headers, timeout=10)
            response_time = round((time.time() - start_time) * 1000, 2)
            
            if response.status_code == 200:
                return {
                    "status": "online",
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "message": "Server đang hoạt động bình thường"
                }
            else:
                return {
                    "status": "warning",
                    "status_code": response.status_code,
                    "response_time": response_time,
                    "message": f"Server phản hồi với status code {response.status_code}"
                }
        except requests.exceptions.Timeout:
            return {
                "status": "timeout",
                "status_code": 0,
                "response_time": 0,
                "message": "Timeout: Server không phản hồi trong 10 giây"
            }
        except requests.exceptions.ConnectionError:
            return {
                "status": "offline",
                "status_code": 0,
                "response_time": 0,
                "message": "Không thể kết nối tới server"
            }
        except Exception as e:
            return {
                "status": "error",
                "status_code": 0,
                "response_time": 0,
                "message": f"Lỗi: {str(e)}"
            }
    
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
        max_attempts = 10  # tránh vòng lặp vô hạn nếu session lỗi
        attempts = 0
        
        while True:
            attempts += 1
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
                # Nếu server trả về lỗi cấp cao (không nằm trong result)
                if 'error' in response_json and not isinstance(response_json.get('error'), str):
                    data = response_json['error'].get('data', {})
                    msg = data.get('message') or str(response_json['error'])
                    if msg:
                        return f"⏩ {ID} Lỗi: {msg}"

                error = response_json.get("result", {}).get("error")
                # Chặn vòng lặp khi session là public_user (không đăng nhập/hết hạn)
                if error == "public_user":
                    return f"⏩ {ID} Session không hợp lệ hoặc đã hết hạn (public_user). Hãy đăng nhập lại."
                if error == "slide_quiz_done":
                    return f"⏩ {ID} Đã hoàn thành!"
                if error == "slide_quiz_incomplete":
                    return f"⏩ {ID} Có lỗi! Vui lòng kiểm tra lại!"
                if error == "slide_access":
                    return f"⏩ {ID} Bạn không có quyền truy cập!"
            except json.JSONDecodeError:
                # Nếu không parse được JSON, dừng để tránh lặp vô hạn
                return f"⏩ {ID} Lỗi: Không thể đọc phản hồi từ server."

            # Nếu đã thử quá số lần cho phép, dừng
            if attempts >= max_attempts:
                return f"⏩ {ID} Dừng sau {max_attempts} lần thử do không nhận được trạng thái hợp lệ."

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

class CRAWL_DATA:
    """Class để crawl dữ liệu từ dashboard LMS PTIT"""
    
    DASHBOARD_URL = "https://lms.ptit.edu.vn/dashboard"
    
    @staticmethod
    def get_dashboard_html(session_id):
        """Lấy HTML của trang dashboard
        
        Args:
            session_id: Session ID để xác thực
            
        Returns:
            str: HTML content của dashboard
            
        Raises:
            Exception: Nếu không thể lấy dashboard
        """
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        cookies = {
            "session_id": session_id
        }
        
        try:
            response = requests.get(
                CRAWL_DATA.DASHBOARD_URL,
                headers=headers,
                cookies=cookies,
                timeout=15
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            raise Exception("Timeout: Server dashboard không phản hồi trong 15 giây")
        except requests.exceptions.ConnectionError:
            raise Exception("Không thể kết nối tới dashboard")
        except Exception as e:
            raise Exception(f"Lỗi khi lấy dashboard: {str(e)}")
    
    @staticmethod
    def parse_courses(html_content):
        """Phân tích HTML dashboard để lấy danh sách khóa học từ course-section
        
        Args:
            html_content: HTML content của dashboard
            
        Returns:
            dict: {course_id: {
                "name": str, 
                "url": str, 
                "completion": int,  # Phần trăm hoàn thành
                "lessons": int,     # Số bài học
                "status": str       # Status badge (Đang học, Hoàn thành, etc.)
            }}
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        courses = {}
        
        try:
            # Tìm course-section (bỏ my-course-section)
            course_section = soup.find('div', class_='courses-section')
            if not course_section:
                print("⚠️  Không tìm thấy courses-section")
                return courses
            
            # Tìm tất cả course cards trong course-section
            course_cards = course_section.find_all('div', class_='course-card')
            
            for card in course_cards:
                try:
                    # Lấy link khóa học
                    course_link = card.find('a', class_='course-link')
                    if not course_link:
                        continue
                    
                    course_url = course_link.get('href', '')
                    if not course_url:
                        continue
                    
                    # Trích xuất course ID từ URL
                    # URL format: /slides/bsa1365-thuong-mai-ien-tu-can-ban-83
                    if '/slides/' in course_url:
                        course_id_str = course_url.split('/slides/')[-1]
                        # Lấy ID số từ cuối URL (sau dấu -)
                        try:
                            course_id = int(course_id_str.split('-')[-1])
                        except (ValueError, IndexError):
                            continue
                    else:
                        continue
                    
                    # Lấy tên khóa học từ course-title
                    course_title_elem = card.find('h3', class_='course-title')
                    course_name = course_title_elem.get_text(strip=True) if course_title_elem else f"Course {course_id}"
                    
                    # Lấy phần trăm hoàn thành
                    completion = 0
                    completion_elem = card.find('span', class_='completion-percent')
                    if completion_elem:
                        try:
                            completion_text = completion_elem.get_text(strip=True)
                            completion = int(completion_text.replace('%', '').strip())
                        except (ValueError, AttributeError):
                            pass
                    
                    # Lấy số bài học
                    lessons = 0
                    lesson_count_elem = card.find('span', class_='lesson-count')
                    if lesson_count_elem:
                        try:
                            lesson_text = lesson_count_elem.get_text(strip=True)
                            # Thường có format như "5 bài" hoặc "5"
                            lessons = int(lesson_text.split()[0])
                        except (ValueError, IndexError, AttributeError):
                            pass
                    
                    # Lấy status badge nếu có
                    status = ""
                    status_elem = card.find('span', class_='course-badge')
                    if status_elem:
                        status = status_elem.get_text(strip=True)
                    
                    courses[course_id] = {
                        "name": course_name,
                        "url": course_url,
                        "completion": completion,
                        "lessons": lessons,
                        "status": status,
                        "course_id_str": course_id_str
                    }
                    
                except Exception as e:
                    print(f"Lỗi khi phân tích course card: {e}")
                    continue
            
        except Exception as e:
            print(f"Lỗi khi phân tích courses: {e}")
        
        return courses
    
    @staticmethod
    def get_course_page_html(session_id, course_url):
        """Lấy HTML của trang course cụ thể
        
        Args:
            session_id: Session ID để xác thực
            course_url: URL của course (ví dụ: /slides/course-name-123)
            
        Returns:
            str: HTML content của course page
        """
        headers = {
            "User-Agent": USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        }
        cookies = {
            "session_id": session_id
        }
        
        # Xây dựng full URL
        if course_url.startswith('http'):
            full_url = course_url
        else:
            full_url = f"https://lms.ptit.edu.vn{course_url}"
        
        try:
            response = requests.get(
                full_url,
                headers=headers,
                cookies=cookies,
                timeout=15
            )
            response.raise_for_status()
            return response.text
        except requests.exceptions.Timeout:
            raise Exception(f"Timeout: Course page không phản hồi trong 15 giây")
        except requests.exceptions.ConnectionError:
            raise Exception("Không thể kết nối tới course page")
        except Exception as e:
            raise Exception(f"Lỗi khi lấy course page: {str(e)}")
    
    @staticmethod
    def parse_course_slides(html_content):
        """Phân tích HTML course page để lấy danh sách slides/quizzes/files
        
        Args:
            html_content: HTML content của course page
            
        Returns:
            dict: {slide_id: {"type": "slide"|"quiz"|"file", "completed": bool}}
        """
        soup = BeautifulSoup(html_content, 'html.parser')
        slides_data = {}
        
        try:
            # Tìm tất cả <li> có data-slide-id
            slide_items = soup.find_all('li', attrs={'data-slide-id': True})
            
            if not slide_items:
                # Fallback: tìm các element khác có data-slide-id
                slide_items = soup.find_all(attrs={'data-slide-id': True})
            
            for item in slide_items:
                try:
                    # Lấy slide ID từ data-slide-id
                    slide_id = int(item.get('data-slide-id'))
                    
                    # Xác định loại dựa trên icon class
                    slide_type = "slide"  # default
                    icon = item.find('i', class_=lambda x: x and 'fa' in x)
                    
                    if icon:
                        classes = icon.get('class', [])
                        # Xác định loại dựa trên class
                        if any(c in classes for c in ['fa-video-camera', 'fa-play', 'fa-file-video-o']):
                            slide_type = "slide"
                        elif any(c in classes for c in [
                            'fa-list', 'fa-list-ul', 'fa-check-square-o', 'fa-check-square',
                            'fa-question', 'fa-question-circle', 'fa-question-circle-o',
                            'fa-pencil-square-o', 'fa-certificate', 'fa-trophy'
                        ]):
                            slide_type = "quiz"
                        elif any(c in classes for c in ['fa-file', 'fa-file-o', 'fa-download', 'fa-file-pdf-o', 'fa-file-text']):
                            slide_type = "file"
                    
                    # Lấy URL nếu có
                    slide_url = None
                    link = item.find('a', href=True)
                    if link:
                        slide_url = link.get('href')

                    # Kiểm tra completed status
                    completed = False
                    done_button = item.find('div', class_='o_wslides_sidebar_done_button')
                    if done_button:
                        completed_attr = done_button.get('data-completed', 'False')
                        completed = completed_attr == 'True'
                    
                    slides_data[slide_id] = {
                        "type": slide_type,
                        "completed": completed,
                        "url": slide_url
                    }
                    
                except (ValueError, TypeError, AttributeError) as e:
                    continue
            
            # Nếu không tìm thấy bằng data-slide-id, thử tìm bằng href
            if not slides_data:
                slide_links = soup.find_all('a', href=True)
                
                for link in slide_links:
                    href = link.get('href', '')
                    
                    if '/slide/' not in href:
                        continue
                    
                    try:
                        slide_id_str = href.split('/slide/')[-1]
                        slide_id = int(slide_id_str.split('-')[-1])
                        
                        # Xác định type từ icon
                        slide_type = "slide"
                        icon = link.find('i', class_=lambda x: x and 'fa' in x)
                        if not icon:
                            parent = link.parent
                            if parent:
                                icon = parent.find('i', class_=lambda x: x and 'fa' in x)
                        
                        if icon:
                            classes = icon.get('class', [])
                            if any(c in classes for c in ['fa-list', 'fa-check-square-o', 'fa-question', 'fa-certificate']):
                                slide_type = "quiz"
                            elif any(c in classes for c in ['fa-file', 'fa-download', 'fa-file-pdf-o']):
                                slide_type = "file"
                        
                        slides_data[slide_id] = {
                            "type": slide_type,
                            "completed": False,  # Unknown khi dùng fallback
                            "url": href
                        }
                    except (ValueError, IndexError):
                        continue
            
        except Exception as e:
            print(f"Lỗi khi phân tích course slides: {e}")
        
        return slides_data
    
    @staticmethod
    def get_course_slides(session_id, course_url):
        """Lấy danh sách slides cho một course (combine get + parse)
        
        Args:
            session_id: Session ID
            course_url: URL của course
            
        Returns:
            dict: {slide_id: type}
        """
        html = CRAWL_DATA.get_course_page_html(session_id, course_url)
        slides = CRAWL_DATA.parse_course_slides(html)
        return slides
    
    @staticmethod
    def get_quiz_page_html(session_id, slide_id=None, slide_url=None):
        """Lấy HTML của trang quiz
        
        Args:
            session_id: Session ID
            slide_id: ID của slide quiz
            slide_url: URL của slide (ưu tiên nếu có)
            
        Returns:
            str: HTML content
        """
        if slide_url:
            if slide_url.startswith('http'):
                url = slide_url
            else:
                url = f"https://lms.ptit.edu.vn{slide_url}"
        else:
            url = f"https://lms.ptit.edu.vn/slides/slide/quiz-{slide_id}"
        headers = {
            "Cookie": f"session_id={session_id}",
            "User-Agent": USER_AGENT
        }
        
        try:
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            return response.text
        except Exception as e:
            print(f"Lỗi khi lấy quiz HTML cho slide {slide_id}: {e}")
            return ""
    
    @staticmethod
    def parse_quiz_html(html_content):
        """Parse HTML quiz và trích xuất dữ liệu
        
        Args:
            html_content: HTML content từ trang quiz
            
        Returns:
            tuple: (slide_id, question_ids, correct_answers) hoặc (None, [], []) nếu lỗi
        """
        import re
        
        try:
            # Extract slide ID from data attribute hoặc URL
            slide_id_match = re.search(r'data-main-object="slide\.slide\((\d+),\)"', html_content)
            if not slide_id_match:
                slide_id_match = re.search(r'/slides/slide/[^/]+-(\d+)', html_content)
            
            if not slide_id_match:
                print("Không tìm thấy slide ID trong HTML")
                return None, [], []
            
            slide_id = int(slide_id_match.group(1))
            
            # Extract tất cả questions với data-question-id
            question_pattern = re.compile(
                r'<div[^>]+class="[^"]*o_wslides_js_lesson_quiz_question[^"]*"[^>]+data-question-id="(\d+)"',
                re.DOTALL
            )
            
            questions = question_pattern.findall(html_content)
            question_ids = [int(qid) for qid in questions]
            
            # Tìm correct answer cho mỗi question
            correct_answers = []
            
            # Split content theo question divs
            question_blocks = re.split(
                r'<div[^>]+class="[^"]*o_wslides_js_lesson_quiz_question[^"]*"[^>]+data-question-id="\d+"',
                html_content
            )[1:]  # Skip phần trước question đầu tiên
            
            for i, block in enumerate(question_blocks):
                # Tìm answer có success check icon
                answer_pattern = re.compile(
                    r'data-answer-id="(\d+)"[^>]*>.*?<i[^>]+class="[^"]*fa-check-circle[^"]*text-success[^"]*"',
                    re.DOTALL
                )
                
                matches = answer_pattern.findall(block)
                if matches:
                    correct_answers.append(int(matches[0]))
                else:
                    # Nếu không có success icon, tìm list-group-item-action
                    answer_pattern_active = re.compile(
                        r'data-answer-id="(\d+)"[^>]+class="[^"]*list-group-item-action[^"]*"',
                        re.DOTALL
                    )
                    matches_active = answer_pattern_active.findall(block)
                    if matches_active:
                        correct_answers.append(int(matches_active[0]))
                    else:
                        # Default: lấy answer đầu tiên
                        answer_any = re.search(r'data-answer-id="(\d+)"', block)
                        if answer_any:
                            correct_answers.append(int(answer_any.group(1)))
                        else:
                            correct_answers.append(0)
            
            if len(question_ids) != len(correct_answers):
                print(f"⚠️ Warning: Tìm thấy {len(question_ids)} questions nhưng {len(correct_answers)} answers")
            
            return slide_id, question_ids, correct_answers
            
        except Exception as e:
            print(f"Lỗi khi parse quiz HTML: {e}")
            return None, [], []
    
    @staticmethod
    def save_quiz_data(slide_id, question_ids, correct_answers, amounts=None):
        """Lưu dữ liệu quiz vào quiz_list.json
        
        Args:
            slide_id: ID của slide
            question_ids: List các question ID
            correct_answers: List các correct answer ID
            amounts: List số lượng đáp án cho mỗi question (default 4)
        """
        if amounts is None:
            amounts = [4] * len(question_ids)
        
        try:
            # Đọc quiz_list.json hiện tại
            if os.path.isfile(QUIZ_LIST):
                with open(QUIZ_LIST, "r", encoding="utf-8") as f:
                    quiz_data = json.load(f)
            else:
                quiz_data = {
                    "quiz_ids": {},
                    "quiz_data": {
                        "question_answer_start": [],
                        "question_amount": []
                    }
                }
            
            # Lấy dữ liệu hiện tại
            quiz_ids_map = quiz_data.get("quiz_ids", {})
            start_arr = quiz_data.get("quiz_data", {}).get("question_answer_start", [])
            amount_arr = quiz_data.get("quiz_data", {}).get("question_amount", [])
            
            # Tìm index lớn nhất hiện tại
            max_index = 0
            for qid_list in quiz_ids_map.values():
                if qid_list:
                    max_index = max(max_index, max(qid_list))
            
            # Tạo mapping từ question_id sang index mới
            new_indices = []
            for i, qid in enumerate(question_ids):
                new_index = max_index + i + 1
                new_indices.append(new_index)
                
                # Mở rộng arrays nếu cần
                while len(start_arr) <= new_index:
                    start_arr.append(0)
                while len(amount_arr) <= new_index:
                    amount_arr.append(4)
                
                # Gán giá trị
                start_arr[new_index] = correct_answers[i]
                amount_arr[new_index] = amounts[i]
            
            # Cập nhật quiz_ids mapping
            quiz_ids_map[str(slide_id)] = new_indices
            
            # Lưu lại
            quiz_data["quiz_ids"] = quiz_ids_map
            quiz_data["quiz_data"]["question_answer_start"] = start_arr
            quiz_data["quiz_data"]["question_amount"] = amount_arr
            
            # Tạo thư mục nếu chưa tồn tại
            quiz_dir = os.path.dirname(QUIZ_LIST)
            if quiz_dir:
                os.makedirs(quiz_dir, exist_ok=True)
            
            # Ghi file
            with open(QUIZ_LIST, "w", encoding="utf-8") as f:
                json.dump(quiz_data, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            print(f"Lỗi khi lưu quiz data: {e}")
            return False
    
    @staticmethod
    def crawl_and_save_quiz(session_id, slide_id, slide_url=None):
        """Crawl quiz HTML và lưu vào quiz_list.json
        
        Args:
            session_id: Session ID
            slide_id: ID của slide quiz
            slide_url: URL của slide (nếu có)
            
        Returns:
            bool: True nếu thành công
        """
        print(f"\n🔍 Đang crawl quiz {slide_id}...")
        
        # Lấy HTML
        html = CRAWL_DATA.get_quiz_page_html(session_id, slide_id=slide_id, slide_url=slide_url)
        if not html:
            print(f"❌ Không lấy được HTML cho quiz {slide_id}")
            return False
        
        # Parse HTML
        parsed_slide_id, question_ids, correct_answers = CRAWL_DATA.parse_quiz_html(html)
        
        if not question_ids:
            print(f"❌ Không tìm thấy questions trong quiz {slide_id}")
            return False
        
        print(f"✅ Tìm thấy {len(question_ids)} questions")
        
        # Lưu vào quiz_list.json
        success = CRAWL_DATA.save_quiz_data(slide_id, question_ids, correct_answers)
        
        if success:
            print(f"💾 Đã lưu dữ liệu quiz {slide_id} vào quiz_list.json")
            return True
        else:
            print(f"❌ Không thể lưu dữ liệu quiz {slide_id}")
            return False
    
    @staticmethod
    def list_courses(session_id):
        """Liệt kê tất cả khóa học từ dashboard
        
        Args:
            session_id: Session ID để xác thực
            
        Returns:
            dict: {course_id: course_info}
        """
        html = CRAWL_DATA.get_dashboard_html(session_id)
        courses = CRAWL_DATA.parse_courses(html)
        return courses
    
    @staticmethod
    def display_courses(courses):
        """Hiển thị danh sách khóa học theo định dạng dễ đọc
        
        Args:
            courses: dict từ list_courses()
        """
        if not courses:
            print("❌ Không tìm thấy khóa học nào!")
            return
        
        print("\n" + "="*100)
        print(f"{'ID':<6} {'Tên Khóa Học':<45} {'Tiến độ':<10} {'Bài':<5} {'Trạng thái'}")
        print("="*100)
        
        for course_id, info in sorted(courses.items()):
            course_name = info['name'][:40]
            completion = info.get('completion', 0)
            lessons = info.get('lessons', 0)
            status = info.get('status', '')
            
            # Tạo progress bar
            progress_bar = "█" * (completion // 10) + "░" * (10 - completion // 10)
            completion_str = f"{progress_bar} {completion}%"
            
            print(f"{course_id:<6} {course_name:<45} {completion_str:<10} {lessons:<5} {status}")
        
        print("="*100 + "\n")
    
    @staticmethod
    def run_course_auto(session_id, course_id, process_slides=True, process_quizzes=True, verbose=True):
        """Chạy tự động slide và quiz cho một khóa học
        
        Args:
            session_id: Session ID để xác thực
            course_id: ID của khóa học
            process_slides: Có chạy slides không (default: True)
            process_quizzes: Có chạy quizzes không (default: True)
            verbose: Có in log không (default: True)
            
        Returns:
            dict: {
                "course_id": int,
                "course_name": str,
                "completion": int,
                "slides_processed": int,
                "quizzes_processed": int,
                "results": [...]
            }
        """
        try:
            # Lấy danh sách khóa học
            courses = CRAWL_DATA.list_courses(session_id)
            
            if course_id not in courses:
                return {
                    "status": "error",
                    "message": f"Không tìm thấy khóa học với ID {course_id}"
                }
            
            course_info = courses[course_id]
            course_name = course_info['name']
            completion = course_info.get('completion', 0)
            course_url = course_info.get('url', '')
            
            if verbose:
                print(f"\n🎓 Bắt đầu xử lý khóa học: {course_name}")
                print(f"📊 Tiến độ: {completion}%")
                print(f"📚 Số bài học: {course_info.get('lessons', 0)}")
            
            results = []
            slides_processed = 0
            quizzes_processed = 0
            
            # Lấy danh sách slides từ all_courses.json
            slides_data = {}
            try:
                if os.path.isfile(ALL_COURSES):
                    with open(ALL_COURSES, "r", encoding="utf-8") as f:
                        all_courses_data = json.load(f)
                        course_data = all_courses_data.get(str(course_id), {})
                        slides_data = course_data.get("slides", {})
            except (FileNotFoundError, json.JSONDecodeError) as e:
                if verbose:
                    print(f"⚠️  Không thể đọc all_courses.json: {e}")
            
            # Nếu có dữ liệu nhưng thiếu type (toàn 'slide'), thử crawl lại để cập nhật type
            if slides_data and course_url:
                try:
                    has_non_slide_type = any(
                        (v.get('type') if isinstance(v, dict) else v) in ["quiz", "file"]
                        for v in slides_data.values()
                    )
                except Exception:
                    has_non_slide_type = False
                
                if not has_non_slide_type:
                    if verbose:
                        print("🔍 Dữ liệu hiện tại thiếu type quiz/file, đang crawl lại course...")
                    try:
                        refreshed = CRAWL_DATA.get_course_slides(session_id, course_url)
                        if refreshed:
                            slides_data = refreshed
                            # Lưu lại all_courses.json
                            try:
                                if os.path.isfile(ALL_COURSES):
                                    with open(ALL_COURSES, "r", encoding="utf-8") as f:
                                        all_courses_data = json.load(f)
                                else:
                                    all_courses_data = {}
                                
                                if str(course_id) not in all_courses_data:
                                    all_courses_data[str(course_id)] = {
                                        "name": course_name,
                                        "slides": {}
                                    }
                                
                                slides_simple = {}
                                for sid, sdata in slides_data.items():
                                    slides_simple[str(sid)] = sdata.get('type', 'slide') if isinstance(sdata, dict) else sdata
                                
                                all_courses_data[str(course_id)]["slides"] = slides_simple
                                os.makedirs(os.path.dirname(ALL_COURSES), exist_ok=True)
                                with open(ALL_COURSES, "w", encoding="utf-8") as f:
                                    json.dump(all_courses_data, f, ensure_ascii=False, indent=2)
                                
                                if verbose:
                                    print("💾 Đã cập nhật type vào all_courses.json")
                            except Exception as e:
                                if verbose:
                                    print(f"⚠️  Không thể lưu cập nhật all_courses.json: {e}")
                    except Exception as e:
                        if verbose:
                            print(f"⚠️  Không thể crawl lại course: {e}")
            
            # Nếu không có slides trong all_courses.json, crawl trang course
            if not slides_data and course_url:
                if verbose:
                    print(f"🔍 Không có dữ liệu trong all_courses.json, đang crawl trang course...")
                
                try:
                    slides_data = CRAWL_DATA.get_course_slides(session_id, course_url)
                    
                    if slides_data:
                        if verbose:
                            completed_count = sum(1 for s in slides_data.values() if s.get('completed'))
                            print(f"✅ Tìm thấy {len(slides_data)} slides ({completed_count} đã hoàn thành)")
                        
                        # Lưu vào all_courses.json với format đúng
                        try:
                            if os.path.isfile(ALL_COURSES):
                                with open(ALL_COURSES, "r", encoding="utf-8") as f:
                                    all_courses_data = json.load(f)
                            else:
                                all_courses_data = {}
                            
                            # Cập nhật dữ liệu - chuyển về format cũ cho tương thích
                            if str(course_id) not in all_courses_data:
                                all_courses_data[str(course_id)] = {
                                    "name": course_name,
                                    "slides": {}
                                }
                            
                            # Chuyển từ {id: {type, completed}} sang {id: type}
                            slides_simple = {}
                            for sid, sdata in slides_data.items():
                                slides_simple[str(sid)] = sdata.get('type', 'slide')
                            
                            all_courses_data[str(course_id)]["slides"] = slides_simple
                            
                            # Tạo thư mục nếu chưa tồn tại
                            os.makedirs(os.path.dirname(ALL_COURSES), exist_ok=True)
                            
                            # Lưu file
                            with open(ALL_COURSES, "w", encoding="utf-8") as f:
                                json.dump(all_courses_data, f, ensure_ascii=False, indent=2)
                            
                            if verbose:
                                print(f"💾 Đã lưu dữ liệu vào all_courses.json")
                        except Exception as e:
                            if verbose:
                                print(f"⚠️  Không thể lưu vào all_courses.json: {e}")
                    else:
                        if verbose:
                            print(f"⚠️  Không tìm thấy slides từ trang course")
                except Exception as e:
                    if verbose:
                        print(f"❌ Lỗi khi crawl course page: {e}")
            
            # Chuyển slides_data thành list items (giữ type và thứ tự trong all_courses.json)
            items_list = []
            url_map = {}
            if slides_data:
                for sid_str, slide_type in slides_data.items():
                    try:
                        sid = int(sid_str)
                    except (ValueError, TypeError):
                        continue
                    if isinstance(slide_type, dict):
                        slide_url = slide_type.get("url")
                        if slide_url:
                            url_map[sid] = slide_url
                        slide_type = slide_type.get("type")
                    if not slide_type:
                        slide_type = "slide"
                    items_list.append({"id": sid, "type": slide_type})

            # Nếu có quiz nhưng chưa có URL, refresh một lần để lấy URL
            if items_list and course_url:
                quiz_missing_url = any(
                    item.get("type") == "quiz" and item.get("id") not in url_map
                    for item in items_list
                )
                if quiz_missing_url:
                    try:
                        refreshed = CRAWL_DATA.get_course_slides(session_id, course_url)
                        if refreshed:
                            for rsid, rdata in refreshed.items():
                                if isinstance(rdata, dict) and rdata.get("url"):
                                    url_map[int(rsid)] = rdata.get("url")
                    except Exception:
                        pass
            
            # Nếu vẫn không có slides, fallback sang quiz_list.json (type=quiz)
            if not items_list:
                try:
                    with open(QUIZ_LIST, "r", encoding="utf-8") as f:
                        quiz_data = json.load(f)
                        quiz_ids_map = quiz_data.get("quiz_ids", {})
                        for slide_id_str in quiz_ids_map.keys():
                            try:
                                slide_id = int(slide_id_str)
                                items_list.append({"id": slide_id, "type": "quiz"})
                            except (ValueError, TypeError):
                                pass
                    # Loại trùng
                    seen = set()
                    items_list = [item for item in items_list if not (item["id"] in seen or seen.add(item["id"]))]
                    items_list = sorted(items_list, key=lambda x: x["id"])
                except (FileNotFoundError, json.JSONDecodeError):
                    pass
            
            # Nếu vẫn không có, dùng course_id như slide
            if not items_list:
                items_list = [{"id": course_id, "type": "slide"}]
            
            if verbose:
                print(f"📋 Tổng cộng {len(items_list)} items để xử lý")
            
            # Xử lý theo đúng thứ tự items_list (slide/quiz/file)
            if items_list:
                if verbose:
                    print(f"\n🔄 Đang xử lý {len(items_list)} items theo thứ tự...")
                
                for item in items_list:
                    slide_id = item["id"]
                    item_type = item.get("type", "slide")
                    
                    # Bỏ qua file
                    if item_type == "file":
                        if verbose:
                            print(f"  ⏭️ File {slide_id} (bỏ qua)")
                        continue
                    
                    # Chạy slide
                    if item_type == "slide":
                        if not process_slides:
                            continue
                        try:
                            if verbose:
                                print(f"  ⏳ Slide {slide_id}...", end=" ")
                            
                            result = SEND_PACKET.SLIDE(session_id, slide_id)
                            result_message = result[2] if isinstance(result, list) and len(result) > 2 else str(result)
                            result_status = result[0] if isinstance(result, list) and len(result) > 0 else ""
                            results.append({
                                "type": "slide",
                                "id": slide_id,
                                "result": result_message
                            })
                            slides_processed += 1
                            
                            if verbose:
                                print("✅")
                            
                            # Dừng khi slide gặp lỗi
                            if result_status != "Yêu cầu thành công!" or any(
                                key in result_message.lower()
                                for key in [
                                    "không có quyền",
                                    "không tìm thấy",
                                    "public_user",
                                    "thất bại",
                                    "lỗi"
                                ]
                            ):
                                return {
                                    "status": "error",
                                    "message": f"Slide {slide_id} lỗi: {result_message}",
                                    "course_id": course_id,
                                    "course_name": course_name,
                                    "completion": completion,
                                    "slides_processed": slides_processed,
                                    "quizzes_processed": quizzes_processed,
                                    "total_results": len(results),
                                    "results": results
                                }
                            
                            time.sleep(1)
                        except Exception as e:
                            if verbose:
                                print(f"❌ ({str(e)[:50]})")
                            results.append({
                                "type": "slide",
                                "id": slide_id,
                                "error": str(e)
                            })
                        continue
                    
                    # Chạy quiz
                    if item_type == "quiz":
                        if not process_quizzes:
                            continue
                        try:
                            if verbose:
                                print(f"  ⏳ Quiz {slide_id}...", end=" ")
                            
                            # Kiểm tra xem slide này có quiz data không
                            has_quiz_data = False
                            try:
                                quiz_ids, _, _ = SEND_PACKET.QUIZ_DATA(slide_id)
                                if quiz_ids:
                                    has_quiz_data = True
                            except ValueError:
                                has_quiz_data = False
                            
                            # Nếu không có data, crawl quiz
                            if not has_quiz_data:
                                if verbose:
                                    print("⚠️ (Không có dữ liệu) ", end="")
                                
                                slide_url = url_map.get(slide_id)
                                # Nếu chưa có URL, thử crawl lại course để lấy URL
                                if not slide_url and course_url:
                                    try:
                                        refreshed = CRAWL_DATA.get_course_slides(session_id, course_url)
                                        if refreshed:
                                            for rsid, rdata in refreshed.items():
                                                if isinstance(rdata, dict) and rdata.get("url"):
                                                    url_map[int(rsid)] = rdata.get("url")
                                            slide_url = url_map.get(slide_id)
                                    except Exception:
                                        pass
                                
                                crawl_success = CRAWL_DATA.crawl_and_save_quiz(session_id, slide_id, slide_url=slide_url)
                                if not crawl_success:
                                    if verbose:
                                        print("⏭️ (Không thể crawl)")
                                    return {
                                        "status": "error",
                                        "message": f"Quiz {slide_id} lỗi: Không thể crawl quiz",
                                        "course_id": course_id,
                                        "course_name": course_name,
                                        "completion": completion,
                                        "slides_processed": slides_processed,
                                        "quizzes_processed": quizzes_processed,
                                        "total_results": len(results),
                                        "results": results
                                    }
                                
                                if verbose:
                                    print("✅ (Đã crawl) ", end="")
                                
                                try:
                                    quiz_ids, _, _ = SEND_PACKET.QUIZ_DATA(slide_id)
                                    if not quiz_ids:
                                        if verbose:
                                            print("⏭️ (Không có quiz)")
                                        return {
                                            "status": "error",
                                            "message": f"Quiz {slide_id} lỗi: Không có quiz sau khi crawl",
                                            "course_id": course_id,
                                            "course_name": course_name,
                                            "completion": completion,
                                            "slides_processed": slides_processed,
                                            "quizzes_processed": quizzes_processed,
                                            "total_results": len(results),
                                            "results": results
                                        }
                                except ValueError:
                                    if verbose:
                                        print("⏭️ (Lỗi data)")
                                    return {
                                        "status": "error",
                                        "message": f"Quiz {slide_id} lỗi: Dữ liệu quiz không hợp lệ",
                                        "course_id": course_id,
                                        "course_name": course_name,
                                        "completion": completion,
                                        "slides_processed": slides_processed,
                                        "quizzes_processed": quizzes_processed,
                                        "total_results": len(results),
                                        "results": results
                                    }
                            
                            result = SEND_PACKET.QUIZ(session_id, slide_id)
                            results.append({
                                "type": "quiz",
                                "id": slide_id,
                                "result": result
                            })
                            quizzes_processed += 1
                            
                            if verbose:
                                print("✅")
                            
                            # Dừng khi quiz gặp lỗi
                            if isinstance(result, str) and any(
                                key in result.lower()
                                for key in [
                                    "lỗi",
                                    "không có quyền",
                                    "public_user",
                                    "không hợp lệ",
                                    "dừng sau",
                                    "có lỗi"
                                ]
                            ):
                                return {
                                    "status": "error",
                                    "message": f"Quiz {slide_id} lỗi: {result}",
                                    "course_id": course_id,
                                    "course_name": course_name,
                                    "completion": completion,
                                    "slides_processed": slides_processed,
                                    "quizzes_processed": quizzes_processed,
                                    "total_results": len(results),
                                    "results": results
                                }
                        except Exception as e:
                            if verbose:
                                print(f"❌ ({str(e)[:50]})")
                            results.append({
                                "type": "quiz",
                                "id": slide_id,
                                "error": str(e)
                            })
                            return {
                                "status": "error",
                                "message": f"Quiz {slide_id} lỗi: {str(e)}",
                                "course_id": course_id,
                                "course_name": course_name,
                                "completion": completion,
                                "slides_processed": slides_processed,
                                "quizzes_processed": quizzes_processed,
                                "total_results": len(results),
                                "results": results
                            }
                        
                        # Delay để tránh bị block
                        time.sleep(2)
            
            if verbose:
                print(f"\n✨ Hoàn thành! Slides: {slides_processed}, Quizzes: {quizzes_processed}\n")
            
            return {
                "status": "success",
                "course_id": course_id,
                "course_name": course_name,
                "completion": completion,
                "slides_processed": slides_processed,
                "quizzes_processed": quizzes_processed,
                "total_results": len(results),
                "results": results
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": str(e)
            }
    
    @staticmethod
    def run_multiple_courses(session_id, course_ids, process_slides=True, process_quizzes=True, verbose=True):
        """Chạy tự động slide và quiz cho nhiều khóa học
        
        Args:
            session_id: Session ID để xác thực
            course_ids: List các course ID
            process_slides: Có chạy slides không
            process_quizzes: Có chạy quizzes không
            verbose: Có in log không
            
        Returns:
            dict: Kết quả chung
        """
        results = []
        
        if verbose:
            print(f"\n🚀 Bắt đầu xử lý {len(course_ids)} khóa học...")
        
        for course_id in course_ids:
            try:
                result = CRAWL_DATA.run_course_auto(
                    session_id,
                    course_id,
                    process_slides=process_slides,
                    process_quizzes=process_quizzes,
                    verbose=verbose
                )
                results.append(result)
            except Exception as e:
                if verbose:
                    print(f"❌ Lỗi xử lý khóa học {course_id}: {e}")
                results.append({
                    "status": "error",
                    "course_id": course_id,
                    "message": str(e)
                })
        
        return {
            "total_courses": len(course_ids),
            "completed": sum(1 for r in results if r.get("status") == "success"),
            "failed": sum(1 for r in results if r.get("status") == "error"),
            "results": results
        }

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