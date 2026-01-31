# Hướng dẫn khắc phục lỗi - LMS PTIT Session ID Extension

## 🐛 Các lỗi thường gặp và cách khắc phục

### 1. Lỗi hiển thị tiếng Việt (ký tự bị lỗi)
**Nguyên nhân**: Thiếu khai báo encoding UTF-8
**Đã khắc phục**: Thêm `<meta charset="UTF-8">` vào popup.html

### 2. Báo "chưa đăng nhập" dù đã đăng nhập
**Nguyên nhân**: 
- Session ID có thể được lưu với tên khác (PHPSESSID thay vì session_id)
- Cookie domain không khớp
- Session đã hết hạn

**Cách khắc phục**:
1. Sử dụng nút **"Debug Info"** để kiểm tra:
   - URL hiện tại
   - Tất cả cookies có sẵn
   - LocalStorage và SessionStorage

2. Thử các bước sau:
   - Đăng xuất và đăng nhập lại
   - Xóa cache và cookies của browser
   - Refresh trang web trước khi dùng extension
   - Kiểm tra trong DevTools (F12) → Application → Cookies

### 3. Không tìm thấy session_id
**Extension hiện tại sẽ tìm session ID theo thứ tự**:
1. Cookie `session_id`
2. Cookie `PHPSESSID` 
3. LocalStorage `session_id` hoặc `PHPSESSID`
4. SessionStorage `session_id` hoặc `PHPSESSID`
5. Bất kỳ cookie nào có chứa từ "session"
6. Meta tags với name="csrf-token" hoặc "session-id"

### 4. Extension không hoạt động
**Kiểm tra**:
1. Đảm bảo đang ở đúng trang lms.ptit.edu.vn
2. Extension đã được load và enable
3. Không có lỗi trong Console (F12)

## 🔍 Cách debug

### Bước 1: Sử dụng nút Debug Info
- Nhấn nút **"Debug Info"** trong extension
- Xem tất cả thông tin cookies và storage
- Copy thông tin này để phân tích

### Bước 2: Kiểm tra Console
1. Mở DevTools (F12)
2. Vào tab Console
3. Nhấn "Lấy Session ID" trong extension
4. Xem log output để hiểu extension đang làm gì

### Bước 3: Kiểm tra Cookies thủ công
1. Mở DevTools (F12)
2. Vào Application → Cookies → https://lms.ptit.edu.vn
3. Tìm cookie có tên chứa "session" hoặc "PHPSESS"
4. Copy giá trị này làm session ID

## 🛠️ Cách cập nhật extension

1. Sửa code trong thư mục extension
2. Vào chrome://extensions/
3. Nhấn nút "Reload" trên extension
4. Test lại

## 📞 Liên hệ support

Nếu vẫn gặp vấn đề, hãy cung cấp:
1. Screenshot lỗi
2. Output của nút "Debug Info"  
3. Console log (nếu có)
4. Phiên bản Chrome đang dùng