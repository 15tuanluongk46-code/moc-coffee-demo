# Cloudflare Pages — phát hành công khai

Ngày xác minh: 2026-10-06.

- Production: https://moc-coffee-demo.pages.dev/
- Khu sản phẩm: https://moc-coffee-demo.pages.dev/#collection
- Project: `moc-coffee-demo`, Cloudflare Pages Direct Upload, tài khoản đã xác minh `15tuanluongk46@gmail.com`.
- Phát hành qua Dashboard, môi trường Production; không mua tên miền hoặc nâng gói.
- Bản hiện tại: Motion 3 — đồng bộ cảnh/chữ và phục hồi animation bị pending, https://moc-coffee-demo.pages.dev/?v=motion-3#origin
- Gói: `dist/moc-coffee-demo.zip`, 96 file, 10,373,515 byte.
- SHA-256: `1b14d8a2e1b2929571e8dbccdab7ba0b847a05b4cebd5d2882b85afe41a04fda`.
- Chỉ nội dung `web/` được đóng gói; không gửi mã dựng Blender, nguồn `.blend`, tài liệu nội bộ hoặc credentials.

## Điều chỉnh khi triển khai

Tiêu đề sản phẩm được bỏ outline khi nhận focus, còn đường viền focus của link/nút vẫn giữ cho bàn phím.

Trong kiểm tra thực tế, CDN trả HTTP 200 với toàn bộ MP4 ngay cả khi yêu cầu byte range. Video trực tiếp bị kẹt seek. `app.js` tải clip nhỏ thành Blob rồi gán Object URL: đã kiểm tra cuộn tiến/lùi, ngắt seek và đổi video theo viewport trên URL production. Request cũ được hủy, Blob URL được thu hồi khi đổi chế độ/nguồn; timeout và poster fallback vẫn hoạt động. Cách này cần tải xong clip trước khi scrub; poster hiển thị trong lúc chờ.

`_headers`: HTML gốc, JavaScript và CSS revalidate; media cache một ngày, font bảy ngày. Khi thay nội dung media nên dùng tên file/thư mục phiên bản mới.

## Xác minh

- PASS: 54 kiểm thử hồi quy local, 99.687 giây: bộ 48 kiểm thử trước cùng sáu kiểm thử timing/readiness/clock của Motion 3. Sáu kiểm thử riêng của overlay Extraction Studio đã bỏ không thuộc hợp đồng bản hiện tại.
- PASS: `python scripts/test_web.py --base-url https://moc-coffee-demo.pages.dev` — desktop 1440×900, mobile 390×844 và 360×640; cuộn video tiến/lùi, seek liên tiếp, popup/Escape/focus, không tràn ngang và không lỗi JavaScript; reduced motion không tải MP4; đổi nguồn responsive; poster khi tải lỗi.
- PASS: bảy kiểm thử production (`scripts/test_motion_timing.py` và `scripts/test_scene_frame.py`), 23.989 giây: intro/media/poster readiness, không replay muộn, phục hồi pending và tôn trọng pause, reveal theo frame đến, product entry/chế độ tĩnh; sáu viewport × bốn chương × hai pha chuyển động giữ giới hạn hình cách mép ít nhất 8 px và tải đúng `media/journey-v2/`.
- PASS: bản dựng riêng chỉ bỏ 24 object gạch nối, 567 → 543 object. Thuộc tính các object còn lại và cả hai camera trên toàn bộ 288 frame được đối chiếu không đổi. Đã giải mã kiểm tra kích thước và nội dung không đồng nhất của 576 frame desktop/mobile; hai MP4 đều 288 frame, 24 fps, 12 giây.
- HTTP Range trên CDN: không hỗ trợ trong lần đo (200); Blob scrubbing đã xác minh. Không ghi nhận đây là Range PASS.
- Chưa kiểm tra Safari/iPhone thật hoặc độ mượt trên mọi thiết bị/mạng. Kết quả trình duyệt dùng Chromium sạch, viewport và touch mô phỏng.

Bản `frame-1` bỏ overlay Extraction Studio theo yêu cầu người dùng, khôi phục scene 3 từ video gốc. Khung giữ đúng tỉ lệ desktop/portrait, có khoảng an toàn và làm mềm mép. Các file Extraction Studio cũ vẫn được lưu nhưng không được trang tải. Chi tiết: `docs/frame-validation.md`. Kiểm tra bounding box xác minh giới hạn CSS, không chứng minh mọi chi tiết đã bị cắt sẵn trong video nguồn được khôi phục.

Bản `no-connectors-2` render lại cùng hành trình sau khi xóa riêng dãy gạch nối giữa các đảo. Video/poster được đặt trong thư mục phiên bản mới để tránh cache cũ. Không đổi thiết kế bốn cảnh, camera hoặc bố cục UI. Báo cáo phạm vi thay đổi và giới hạn đánh giá thị giác: `docs/connector-removal-validation.md`; đối chiếu Blender: `docs/connector-removal.json`.

Bản `motion-3` giữ nguyên media và khung của bản trên. Cải thiện nhịp wheel 1,2 giây, reveal theo frame đã trình bày, intro sau readiness, product entry và turntable; phục hồi animation MỘC kẹt pending trong Chrome. Chi tiết đo và giới hạn: `docs/motion-v3-validation.md`. Dashboard xác nhận Production deployment thành công; các kiểm thử ở trên chạy lại trên URL công khai sau triển khai.

Python có Playwright trên máy này: `/home/sss/AI-Home/projects/flowbot/.venv/bin/python`.

## Cập nhật lần sau

1. Sửa nội dung trong `web/`, chạy các kiểm thử liên quan.
2. Tại gốc dự án chạy `python3 scripts/package_site.py`. Script tạo ZIP và bản kê release trong `dist/`.
3. Cloudflare Dashboard → Workers & Pages → `moc-coffee-demo` → Create deployment → Production.
4. Upload `dist/moc-coffee-demo.zip`, chờ tất cả file thành công rồi Save and deploy.
5. Chạy lại kiểm tra URL public bằng lệnh ở trên. Kiểm tra cả trang gốc và `#collection`.

Nếu cần quay lại, chọn deployment trước đó trong lịch sử Cloudflare và dùng thao tác rollback khi phù hợp. Giữ lại ZIP/bản kê của từng phiên bản cần khôi phục.
