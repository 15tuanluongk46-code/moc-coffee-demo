# Cuộn có điểm dừng — 2026-10-06

## Hành vi đã triển khai

- Bốn điểm dừng hành trình tương ứng bốn cảnh và vị trí video rõ ràng.
- Một đợt wheel nhận một điểm đến; khoảng lặng 240ms hoặc đảo hướng bắt đầu đợt mới. Delta pixel/line/page được quy đổi; ngưỡng tích lũy 8px lọc chuyển động rất nhỏ.
- Di chuyển 620ms bằng requestAnimationFrame; giảm chuyển động/chế độ tĩnh chuyển tức thì. Đảo chiều có thể ngắt chuyển động đang chạy.
- Điểm dừng phần nội dung tính từ kích thước header và section thực tế. Section dài có điểm theo khối nội dung, bổ sung bước đọc có chồng lấn để tránh bỏ qua đoạn.
- Layout desktop rộng tối thiểu 1101px và cao tối thiểu 750px cân ảnh/khoảng cách theo chiều cao khả dụng. Mobile và màn hình thấp giữ nội dung đọc theo nhiều bước.
- Touch/bàn phím dùng cuộn native; khi kết thúc mới căn cảnh hoặc điểm gần trong nội dung dài. Không áp đặt scroll-snap toàn trang.
- Không chặn wheel zoom, wheel ngang, popup và form tư vấn. Khối có cuộn nội bộ được đọc trước khi chuyển điểm trang.

## Xác minh

Môi trường: Chromium qua Playwright, server local `127.0.0.1:8046`.

```bash
/home/sss/AI-Home/projects/flowbot/.venv/bin/python -m unittest scripts/test_scroll_stops.py scripts/test_boutique.py scripts/test_motion.py scripts/test_motion_v2.py scripts/test_ux.py
```

**PASS: 38 tests, 65.287 giây.** Trong đó 8 kiểm thử mới xác minh burst/quán tính, cuộn ngược, đi qua ranh giới hành trình–sản phẩm, hero/viewer nằm dưới header, nhiều bước đọc mobile, popup/zoom không bị chặn, ngắt chuyển động giữa chừng, thời gian video và độ rõ chữ khi đến cảnh, PageDown và wheel trong khu tư vấn.

Các kiểm thử cũ tiếp tục kiểm tra kéo chuột/touch sản phẩm, vuốt dọc, lỗi ảnh/retry, tư vấn quay lại/làm lại, lịch sử, xoay màn hình, giảm chuyển động, popup và vòng đời motion.

Lượt kiểm tra cùng đợt trước suite tổng:
- `scripts/check_atelier.py`: PASS 20 trạng thái bố cục trên 5 viewport, gồm màn hình rộng 2494px và mobile 320px; báo cáo `renders/browser/atelier-layout.json`.
- `scripts/test_web.py`: PASS trên 1440×900, 390×844 và 360×640; điều hướng/seek video, popup, reduced-motion không tải MP4, đổi nguồn responsive, fallback lỗi và HTTP Range.

## Phạm vi kết luận

Đã xác minh hành vi và hình học bố cục trong Chromium giả lập. Không coi các phép đo DOM hoặc test tự động là chứng nhận thẩm mỹ toàn bộ cảnh. Chưa kiểm tra Safari/iPhone thật hoặc quán tính của mọi chuột/trackpad vật lý. Nội dung dài trên màn hình nhỏ chủ đích cần nhiều bước đọc, không cam kết mỗi section luôn vừa một màn hình.
