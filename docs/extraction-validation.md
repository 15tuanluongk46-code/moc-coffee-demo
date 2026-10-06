# Khoảnh khắc chiết xuất — kiểm chứng

Ngày: 2026-10-06. Nguồn: `source/moc-extraction-v01.blend`, scene riêng `MOC - Extraction Studio`, 74 objects; đã mở lại bằng Blender background. Không chỉnh scene Blender đang làm việc của người dùng.

## Media và tương tác

- Hai camera riêng: desktop 1280×800, mobile 720×1440. Mỗi camera render 72 ảnh; FFmpeg nội suy blend và chuẩn hóa timestamp thành 144 frame, 24 fps, 6 giây, H.264/yuv420p/faststart.
- MP4 desktop 186,498 byte; mobile 174,211 byte. `package_extraction.py` kiểm tra số frame, tốc độ trung bình và thời lượng bằng ffprobe.
- Chuyển từ hành trình cũ sang studio bằng dissolve có chủ đích, không phải nối camera khớp từng pixel. Dòng cà phê và gợn mặt cốc được render; hơi nước là lớp CSS đặt theo phép chiếu camera, không phải mô phỏng fluid.
- Loop tải khi tới cảnh pha, dùng Blob để tương thích CDN; dừng khi rời cảnh, đang cuộn, ẩn tab, mở popup hoặc bật chế độ tĩnh/reduced motion. Khi video lỗi vẫn có poster và điều khiển khám phá.
- Hai nút khám phá hỗ trợ bàn phím; parallax giới hạn 8×6px với con trỏ chính xác. Sản phẩm có intro xoay ngắn, reset theo đường ngắn và trạng thái tải/kéo; bước tư vấn có hướng tiến/lùi, hủy motion khi giảm chuyển động.

## Kiểm tra local đã chạy

- PASS: 53 unittest trong `test_extraction`, `test_video_cdn`, `test_ux`, `test_motion`, `test_motion_v2`, `test_scroll_stops`, `test_polish`, `test_boutique` — 86.195 giây.
- PASS: 9 test extraction chạy lại sau chuẩn hóa video CFR — 5.718 giây.
- PASS: `scripts/test_web.py`: ba viewport, cuộn/seek tiến-lùi, popup, keyboard, không tràn ngang/lỗi JS, reduced motion, responsive media, poster fallback.
- PASS: `scripts/check_extraction.py`: 7 viewport từ 320×568 đến 1440×900, gồm landscape; vùng chữ/điều khiển/footer không chồng nhau. Trên màn hình thấp, nội dung chữ có thể cuộn bên trong thay vì thu nhỏ font.
- PASS: `scripts/check_atelier.py`: 20 kiểm tra bố cục; syntax JS và compile Python.

## Bằng chứng thị giác và giới hạn

Contact sheets: `renders/extraction/contact-desktop.jpg`, `contact-mobile.jpg`. Screenshot: `renders/browser/extraction-1440.png`, `extraction-390.png`.

Model chính không đọc được ảnh; vision phụ kiểm tra một screenshot desktop và báo headline bên trái, máy/cốc bên phải, không bị cắt khung, nút không che cốc. Đây là kiểm tra lấy mẫu, không phải xác nhận thẩm mỹ hoặc độ liền mạch mọi frame. Chưa đánh giá bằng mắt toàn bộ loop ở tốc độ thực, chưa đo FPS thiết bị thật, chưa kiểm tra Safari/iPhone thật. Kiểm thử touch/viewport dùng Chromium mô phỏng. Kết quả production được ghi riêng trong `deployment.md` sau phát hành.
