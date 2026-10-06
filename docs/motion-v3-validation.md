# Motion 3 — xác minh nhịp chuyển động

Ngày: 2026-10-06. Phạm vi: JavaScript và vòng đời motion; không dựng lại hình, camera hoặc bố cục bốn cảnh.

## Điều chỉnh

- `animation-clock.js`: WAAPI bắt đầu trên document timeline rõ ràng. Bộ kiểm tra 250 ms chỉ phục hồi animation thuộc MỘC khi đang running, pending và chưa có startTime; không tiếp tục animation đang pause hoặc khi trang ẩn/chế độ tĩnh.
- Intro camera 1.400 ms đợi font cùng video hoặc poster fallback sau 2 giây. Nếu người dùng tương tác trong lúc chờ, không phát intro muộn.
- Chuyển một cảnh bằng wheel: 1.200 ms, easing cosine; khu nội dung thông thường 850 ms. Vẫn gom một đợt wheel thành một bước và cho phép đảo chiều.
- Chữ chờ video trình bày frame ở vùng đến có độ rõ tối thiểu 0,95. `requestVideoFrameCallback` theo frame thực; trình duyệt không hỗ trợ dùng sự kiện seeked.
- Product hero/macro: ảnh 1.000 ms, nội dung 680 ms với stagger 120 ms. Turntable giới thiệu 0→60°→0, chín bước cách 170 ms; thao tác thật hủy phần giới thiệu.
- Chế độ tĩnh/reduced motion hủy motion; không thay nguồn `media/journey-v2/` hay khôi phục dãy gạch đã bỏ.

## Bằng chứng

- PASS: 54 unittest local, 99,687 giây, gồm 6 kiểm thử timing/readiness mới, các kiểm thử UX, motion, scroll stops, boutique, polish, CDN, khung cảnh và ba kiểm thử sản phẩm/tư vấn được giữ lại.
- PASS: `scripts/test_web.py` local — ba viewport, điều hướng/seek tiến-lùi, popup/focus, reduced motion không tải video, đổi nguồn responsive, lỗi video dùng poster, Blob scrubbing.
- PASS: kiểm tra cú pháp `app.js`, `motion.js`, `boutique.js`, `animation-clock.js`.
- Chrome AI headed thực tế: moc-drift/moc-warmth không còn pending, thời gian tăng khoảng 700 ms qua hai lần đo cách 700 ms. Trước sửa, chúng đứng ở thời gian 0 với startTime null dù trang visible. Cơ chế phục hồi được xác minh; nguyên nhân gốc bên trong Chrome chưa kết luận.
- Một lần đo wheel 140 px trong Chromium sạch: desktop 1440×900 trình bày 36 frame video; mobile 390×844 trình bày 39 frame. Chữ mới bắt đầu khoảng 1.036/1.039 ms sau lúc bắt đầu lấy mẫu, opacity 0,989/1,0, frame media 3,5/3,542 giây. Lần audit trước ghi nhận 20/22 frame ở hai viewport. Đây là số frame trình bày trong thao tác đo, không phải benchmark FPS và không bảo đảm mọi máy đạt cùng kết quả.

## Giới hạn

Các kiểm thử xác minh thời gian và hành vi, không thay thế đánh giá thẩm mỹ chuyển động đầy đủ. Chưa kiểm tra Safari/iPhone thật hoặc mọi cấu hình GPU/mạng. Hình 3D vẫn là video render của bốn cảnh gốc; motion idle không biến thành mô phỏng vật thể thời gian thực.

Kết quả kiểm tra production và SHA gói phát hành được ghi tại `docs/deployment.md` sau khi triển khai.
