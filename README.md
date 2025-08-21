# Thiết lập .env
SLIDE_URL = https://lms.ptit.edu.vn/slides/slide/set_completed

QUIZ_URL = https://lms.ptit.edu.vn/slides/slide/quiz/

USER_AGENT = Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.

H_DATA = application/

QUIZ_LIST = quiz_list.json

BOT_TOKEN = {Token bot Discord}


# Sử dụng

## Hoàn thành slide

Sử dụng lệnh:
  !slide {SessionID} {ID slide}

## Hoàn thành quiz

Nạp dữ liệu quiz vào quiz_list.json

    start: ID của đáp án A câu 1 trong mỗi quiz
    
    amount: Số lượng câu hỏi
    
    list: Danh sách số lượng đáp án mỗi câu 

Sử dụng lệnh:
 !quiz {SessionID} {ID quiz}
