# LMS PTIT Session ID Extension

Extension Chrome giúp lấy giá trị `session_id` từ cookie của trang web LMS PTIT (https://lms.ptit.edu.vn).

## Tính năng

- ✅ Lấy session_id từ cookie một cách tự động
- ✅ Giao diện đơn giản, dễ sử dụng
- ✅ Tự động copy session_id vào clipboard
- ✅ Kiểm tra và thông báo lỗi chi tiết
- ✅ Hỗ trợ nhiều phương pháp lấy session_id

## Cách cài đặt

1. Mở Chrome và truy cập `chrome://extensions/`
2. Bật "Developer mode" ở góc trên bên phải
3. Nhấn "Load unpacked" và chọn thư mục `extension_session_id`
4. Extension sẽ được cài đặt và hiển thị icon trên thanh công cụ

## Cách sử dụng

1. Truy cập trang web https://lms.ptit.edu.vn và đăng nhập
2. Nhấn vào icon extension trên thanh công cụ Chrome
3. Nhấn nút "Lấy Session ID"
4. Session ID sẽ được hiển thị và có thể copy vào clipboard

## Cấu trúc file

- `manifest.json` - Cấu hình chính của extension
- `popup.html` - Giao diện popup của extension
- `popup.js` - Logic xử lý chính
- `content.js` - Script chạy trên trang web LMS PTIT
- `icon48.png` - Icon của extension

## Quyền truy cập

Extension yêu cầu các quyền sau:
- `cookies` - Để đọc cookie từ trang web
- `activeTab` - Để tương tác với tab hiện tại
- `scripting` - Để inject script vào trang web
- `host_permissions` cho `https://lms.ptit.edu.vn/*` - Để truy cập trang web LMS PTIT

## Xử lý lỗi

- Nếu không tìm thấy session_id: Vui lòng đăng nhập vào LMS PTIT trước
- Nếu không ở đúng trang web: Extension chỉ hoạt động trên lms.ptit.edu.vn
- Nếu có lỗi khác: Kiểm tra console của extension để biết chi tiết

## Phát triển

Extension sử dụng Manifest V3 và tương thích với Chrome phiên bản mới nhất.