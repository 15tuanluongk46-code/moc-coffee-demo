# Bỏ gạch nối giữa cảnh

Phạm vi được duyệt: bỏ dãy viên gạch sáng màu trong các đoạn nối, giữ bốn cảnh và chuyển động camera. Không đổi giao diện, vật liệu, ánh sáng hay bố cục.

## Bản dựng

- Nguồn giữ nguyên: `source/moc-journey-v01.blend`.
- Biến thể: `source/moc-journey-no-connectors-v02.blend`.
- Script: `scripts/remove_connectors.py`.
- Đã kiểm tra đúng 24 đối tượng có tiền tố `GEO-MOC-journey-stepping-stone` trước khi xóa.
- Từ 567 xuống 543 đối tượng. Kiểm tra tên, kiểu, dữ liệu mesh, transform, vật liệu và trạng thái render của toàn bộ đối tượng còn lại không đổi.
- Hai camera có transform, ortho scale, shift và lens giống nguồn ở cả 288 frame.
- Bản kê đầy đủ: `docs/connector-removal.json`.
- `journey_scene.py` cũng bỏ bước sinh gạch để lần dựng lại không tạo chúng trở lại.

## Tái tạo

```bash
blender -b source/moc-journey-v01.blend --python scripts/remove_connectors.py
blender -b source/moc-journey-no-connectors-v02.blend --python scripts/render_journey.py -- --view desktop --output-root renders/no-connectors-v2
blender -b source/moc-journey-no-connectors-v02.blend --python scripts/render_journey.py -- --view mobile --output-root renders/no-connectors-v2
python3 scripts/package_media.py --render-root renders/no-connectors-v2 --media-subdir journey-v2 --posters-from-frames
python3 scripts/check_connectors.py
```

Render và media dùng thư mục phiên bản riêng để giữ bản cũ và tránh cache CDN một ngày của các URL cũ. Poster lấy từ chính các frame mới, cùng thời điểm dừng 1/97/193/288.

## Trạng thái xác minh

- PASS: phạm vi sửa bản dựng và camera (bản kê JSON).
- PASS: hai chuỗi đủ 288 frame, toàn bộ 576 PNG giải mã được, đúng kích thước 1280×800 và 720×1440; không có frame đồng màu. Báo cáo `renders/no-connectors-v2/frame-check.json`.
- PASS: hai MP4 H.264, 288 frame, 24 fps, 12 giây; tám poster lấy từ frame mới. Media và probe nằm trong `web/media/journey-v2/` và `renders/no-connectors-v2/media-report.json`.
- PASS: 48 kiểm thử local, 83.617 giây; `test_web.py` đạt ba viewport với điều hướng tiến/lùi, popup/bàn phím, reduced motion, đổi nguồn, lỗi media và Blob seek.
- PASS: `node --check web/app.js` và `python3 -m compileall -q scripts`.
- Đã tạo contact sheet chuyển cảnh desktop/mobile. Công cụ vision chỉ trả mô tả chung, không trả lời đáng tin cậy về từng frame; không coi đây là visual quality PASS.
- Phát hành công khai được ghi riêng tại `docs/deployment.md` sau khi kiểm tra production.
- Kiểm tra cấu trúc và giải mã frame không thay thế đánh giá thẩm mỹ/chuyển động trực quan hoặc kiểm tra Safari trên thiết bị thật.
