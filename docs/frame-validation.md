# Khôi phục cảnh gốc và giới hạn khung

Yêu cầu: giữ cảnh gốc, chỉ sửa tràn viền.

## Thay đổi

- Gỡ import, video overlay, steam và controls của Extraction Studio khỏi trang.
- Giữ nguyên `journey-desktop.mp4`, `journey-mobile.mp4` và các poster của bốn cảnh. Không sửa Blender hoặc render lại.
- Khung desktop 8:5 và portrait 1:2 vừa viewport, có khoảng đệm 24–64 px. Chuyển động idle vẫn nằm trong vùng an toàn.
- Làm mềm 3% mép khung bằng mask. Không thêm khung viền hoặc thay bố cục nội dung.
- Giữ các cải tiến sản phẩm/tư vấn đã được chấp nhận.

## Kiểm tra local 2026-10-06

- PASS: 48 kiểm thử hiện hành: scene-frame 1, CDN 1, UX 10, motion 6, motion-v2 6, scroll-stops 8, polish 5, boutique 8 và ba kiểm thử sản phẩm/tư vấn trong test_extraction. Lượt cuối 101.036 giây.
- PASS: test_scene_frame kiểm tra bốn chương ở sáu viewport (1440×900, 2494×1100, 768×1024, 390×844, 320×568, 844×390), cả hai đầu chu kỳ idle; hình cách mép viewport ít nhất 8 px, không tải media Extraction Studio.
- PASS: test_web đầy đủ trên ba viewport: cuộn tiến/lùi, popup/bàn phím, không tràn ngang, responsive media, reduced motion, poster fallback và Blob seek.
- PASS: `node --check web/app.js`.
- Một lượt đầu có timeout kiểm thử đợt lăn chuột và gọi sai tên lớp test; kiểm tra tập trung và toàn bộ lượt cuối đều đạt, không sửa thuật toán cuộn.

## Giới hạn

Kiểm tra bounding box chứng minh giới hạn hiển thị, không chứng minh mọi chi tiết đã có sẵn trong video đều được camera ghi trọn. Không sửa nội dung pixel/camera trong nguồn. Kết quả đọc ảnh tham chiếu qua vision không đủ tin cậy để khẳng định nguyên nhân cắt hình bên trong video. Chưa kiểm tra Safari/iPhone thật.
