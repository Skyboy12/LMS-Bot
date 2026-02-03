# Bot Discord LMS

Bot Discord này giúp tương tác với slide và quiz trên hệ thống LMS PTIT. Bot cho phép người dùng tự động hoàn thành slide, gửi đáp án quiz và quản lý dữ liệu quiz trực tiếp từ Discord.

## Tính năng
- **Hoàn thành slide**: Đánh dấu slide đã hoàn thành với lệnh `!slide`.
- **Tự động quiz**: Tự động gửi đáp án cho quiz với lệnh `!quiz`.
- **Chạy tự động khóa học**: Tự động hoàn thành tất cả slides và quizzes cho một khóa học với lệnh `!course`.
- **Chạy tất cả khóa học**: Tự động hoàn thành tất cả slides và quizzes cho tất cả khóa học với lệnh `!all`.
- **Quản lý dữ liệu quiz**: Thêm và xem dữ liệu quiz với lệnh `!add_quiz` và `!show_quiz`.
- **Kiểm tra kết nối**: Kiểm tra bot có hoạt động không với lệnh `!ping`.
- **Ghi log**: Mọi hoạt động của bot đều được ghi vào file `bot.log` để dễ dàng kiểm tra và giám sát.

## Cài đặt

### Yêu cầu
- Python 3.8 trở lên
- Token bot Discord

### Cài đặt
1. Clone repository:
   ```powershell
   git clone <repo-url>
   cd LMS-Bot
   ```
2. Cài đặt các thư viện:
   ```powershell
   pip install -r requirements.txt
   ```
3. Thiết lập biến môi trường:
   - Sao chép file `.env` và điền token bot Discord cùng các thông tin cần thiết.

### Chạy bot
```powershell
python discord_bot.py
```

## Sử dụng

### Các lệnh
- `!ping` — Kiểm tra bot có hoạt động không.
- `!slide <session_id> <slide_id>` — Hoàn thành một slide.
- `!quiz <session_id> <quiz_id>` — Chạy tự động quiz (tìm đáp án đúng).
- `!course <session_id> <course_id>` — Chạy tự động tất cả slides và quizzes của một khóa học.
- `!all <session_id>` — Chạy tự động tất cả slides và quizzes của tất cả khóa học (với progress bar).
- `!add_quiz <id> <quiz_ids> <starts> <amounts>` — Thêm dữ liệu quiz. Chấp nhận mảng JSON hoặc danh sách phân tách bằng dấu phẩy.
- `!show_quiz <id>` — Hiển thị dữ liệu quiz cho ID đã cho.

### Ví dụ
```
!ping
!slide SESSION_ID 123
!quiz SESSION_ID 123
!course SESSION_ID 5
!all SESSION_ID
!add_quiz 150 "[1001,1002,1003]" "[0,0,1]" "[4,4,2]"
!show_quiz 150
```

### Lưu ý
- `SESSION_ID` là cookie session của bạn khi đăng nhập vào LMS (sao chép từ browser).
- Lệnh `!all` sẽ chạy tất cả khóa học một lần, quá trình này có thể mất vài phút.
- Nếu gặp lỗi trong quá trình chạy, bot sẽ dừng ngay và báo lỗi cụ thể.

## Cấu trúc thư mục
- `discord_bot.py` — Logic chính của bot và các lệnh.
- `send_packet.py` — Xử lý gửi yêu cầu tới server LMS và quản lý dữ liệu quiz.
- `quiz_list.json` — Lưu trữ dữ liệu quiz.
- `.env` — Biến môi trường.
- `all_courses.json` — Lưu trữ thông tin tất cả khóa học.
- `requirements.txt` — Các thư viện Python cần thiết.

## Khắc phục sự cố
- Kiểm tra file `bot.log` để xem thông báo lỗi.
- Đảm bảo file `.env` đã được cấu hình đúng.
- Đảm bảo token bot hợp lệ và có đủ quyền truy cập.

## Giấy phép
MIT
