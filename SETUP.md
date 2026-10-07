# Setup MỘC Coffee

Chạy từ root repo. Website static đã có media/font; chỉ cần Python 3.10+ để serve. Không cần Node, npm, Blender hoặc tài khoản Cloudflare để xem local. Linux/WSL là baseline hướng dẫn.

## 1. Chạy website bằng asset có sẵn

```bash
python3 scripts/serve.py
```

Mở http://127.0.0.1:8046. Server hỗ trợ HTTP Range; đừng dùng `file://` để đánh giá video/Blob. `python3 scripts/serve.py --port 8047` đổi cổng nếu cần, nhưng các test có thể mặc định 8046.

## 2. Môi trường test riêng

```bash
python3 -m venv .venv-test
.venv-test/bin/python -m pip install playwright Pillow
.venv-test/bin/python -m playwright install chromium
mkdir -p renders
.venv-test/bin/python scripts/test_web.py --static-only
.venv-test/bin/python scripts/test_web.py
.venv-test/bin/python scripts/test_ux.py
.venv-test/bin/python scripts/test_boutique.py
.venv-test/bin/python scripts/test_scroll_stops.py
```

Giữ server ở terminal riêng trong lúc test. Không mượn virtualenv Flowbot. Linux thiếu thư viện browser: dùng hướng dẫn lỗi Playwright hoặc `playwright install --with-deps chromium` trong venv với quyền cài package phù hợp. Test web có `--base-url`; xem từng script trước khi đổi cổng cho suite khác.

Các test motion (`test_motion.py`, `test_motion_v2.py`, `test_motion_timing.py`), khung (`test_scene_frame.py`), polish và CDN là kiểm tra chuyên biệt theo tài liệu `docs/`; đọc kỳ vọng so với phiên bản hiện tại trước khi dùng làm gate. `test_video_cdn.py` có thể truy cập site public; không đưa vào smoke local mặc định. `test_extraction.py` còn kỳ vọng overlay đã bỏ: không chạy toàn bộ như gate hiện tại. Báo rõ case lỗi thay vì xóa test lịch sử để có màu xanh.

## 3. Đóng gói static

```bash
python3 scripts/package_site.py
```

Sinh `dist/moc-coffee-demo.zip` và `dist/release.json` từ `web/`. Chỉ upload khi user yêu cầu theo [deployment](docs/deployment.md). Source `.blend` và render trung gian không thuộc website deploy.

## 4. Tái dựng 3D — tùy chọn, có thể ghi đè output

Cần Blender 5.2, FFmpeg/FFprobe, ImageMagick, Python 3.10+ và Pillow. Giữ bản sao scene/frame đã chỉnh trước khi render; resume có thể dùng frame cũ dù nội dung scene đã đổi.

- Hành trình hiện tại: `source/moc-journey-no-connectors-v02.blend`, media `web/media/journey-v2/`; dùng lệnh trong [connector-removal-validation](docs/connector-removal-validation.md).
- Sản phẩm: `source/moc-product-v02.blend`; `scripts/product_atelier.py` dựng và render; `scripts/prepare_boutique.py --version 2` đóng gói. Lệnh `--fonts-only` chuẩn bị font khi tái dựng.
- `rebuild.py`, `moc-journey-v01.blend`, Extraction Studio là pipeline/lịch sử riêng, không phải bước setup hay rebuild tất cả bản hiện tại.

## Đầu vào và khắc phục

Tracked: `web/`, `source/`, `scripts/`, giấy phép trong `assets/` và font. Generated: venv, `renders/`, `dist/`, browser reports. Không commit venv/cache.

- Video không tải: kiểm tra server/đường dẫn media, HTTP Range và console; dùng chế độ tĩnh để phân biệt video với layout.
- Thiếu Pillow: cài vào đúng venv đang gọi script.
- Test báo thiếu selector Extraction: kiểm tra tính năng lịch sử, không phục hồi overlay chỉ để test pass.
- Chưa render Blender hoặc chưa kiểm tra browser khác: ghi NOT RUN, không dùng record lịch sử thay bằng chứng mới.
