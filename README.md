# MỘC Coffee — Từ đất lành, đến vị nguyên bản

Demo landing page kể chuyện bằng cuộn: **nông trại → xưởng rang → espresso → ly cà phê & bao bì**. Toàn bộ hình học/vật liệu được dựng mới bằng Blender; video cuộn được render tại máy. Không dùng API trả phí, không cần npm hoặc backend ứng dụng.

## Mở demo

**Website công khai:** https://moc-coffee-demo.pages.dev/

**Khu sản phẩm:** https://moc-coffee-demo.pages.dev/#collection

Đã triển khai Cloudflare Pages với HTTPS; không cần bật máy local để người khác truy cập. Cách cập nhật và kết quả kiểm tra: [docs/deployment.md](docs/deployment.md).

Chạy bản local để phát triển:

```bash
python3 scripts/serve.py
```

Mở **http://127.0.0.1:8046/**. Server chỉ lắng nghe loopback và hỗ trợ HTTP Range cho video. Dùng cuộn trang, menu hoặc số chương để đi tiến/lùi. Nút **Chế độ tĩnh** chuyển sang poster; hệ điều hành bật giảm chuyển động thì website tự dùng poster, không tải video. CTA mở bảng hương vị minh họa.

MỘC là thương hiệu giả định cho demo; chưa có giỏ hàng, thanh toán hoặc backend. Bản công khai là website static. Video tải thành Blob trong trình duyệt để cuộn được cả khi CDN không trả HTTP Range; chế độ tĩnh vẫn không tải video.

## Cấu trúc

### Motion 3 — nhịp cảnh và chữ

Bản mới: https://moc-coffee-demo.pages.dev/?v=motion-3#origin

- Intro đợi font và video sẵn sàng; sau 2 giây có thể dùng poster. Không phát lại intro muộn khi người dùng đã thao tác.
- Một đợt lăn chuột chuyển cảnh trong 1,2 giây. Chữ xuất hiện theo frame video thực sự được trình duyệt trình bày, tránh reveal trong lúc khung còn mờ.
- Ảnh và nội dung sản phẩm xuất hiện theo nhịp; túi xoay giới thiệu khoảng 1,5 giây rồi trở về nhãn trước.
- Animation do MỘC quản lý có phục hồi khi bị kẹt `pending` trong Chrome. Chế độ tĩnh, giảm chuyển động và animation đang pause vẫn được tôn trọng.
- Bốn cảnh, camera, video `journey-v2` và sửa khung an toàn giữ nguyên. Chi tiết xác minh: [docs/motion-v3-validation.md](docs/motion-v3-validation.md).

- `web/` — website hoàn chỉnh, HTML/CSS/JavaScript không dependency.
- `web/media/journey-v2/` — MP4 desktop/mobile và 8 WebP poster hiện tại, đã bỏ dãy gạch nối.
- `source/moc-journey-v01.blend` — bốn trạm cùng đường camera 288 frame / 24 fps.
- `scripts/journey_scene.py` — mô hình/camera, mở rộng từ `farm_scene.py`.
- `scripts/render_journey.py` — render tiếp tục từ frame còn thiếu, GPU với CPU fallback.
- `scripts/package_media.py` — mã hóa H.264, GOP ngắn phục vụ seek và đóng gói poster.
- `scripts/test_web.py` — kiểm thử Chromium, lưu screenshot/report vào `renders/browser/`.
- `scripts/test_ux.py` — 10 kiểm thử hồi quy luồng người dùng, gồm xoay màn hình, lịch sử, popup, timeout/retry và cuộn trên chữ.
- `web/motion.js` — motion trang trí độc lập với điều hướng và thời gian video.
- `web/scroll-stops.js` — gom đợt lăn chuột và tính điểm dừng theo cảnh/kích thước nội dung.
- `scripts/test_motion.py` — 6 kiểm thử intro, chuyển chương, hủy hiệu ứng, popup, hover và giảm chuyển động.
- `scripts/test_motion_v2.py` — 6 kiểm thử mở cảnh, chữ theo camera, idle, marker điều hướng và hiệu ứng đóng popup.
- `docs/design.md`, `docs/validation-full.md` — thiết kế và phạm vi xác minh.
- `assets/ATTRIBUTION.md` — nguồn và thông tin giấy phép.

## Boutique, sản phẩm và barista

Mở **http://127.0.0.1:8046/?v=atelier-2#collection** để đến bản sản phẩm mới; quay về đầu bằng logo MỘC. Hành trình bốn chương nối tiếp khu vực sản phẩm, ảnh macro, tư vấn và hướng dẫn pha.

- **Ảnh studio:** bản desktop/mobile riêng, dựng bằng Blender; font Be Vietnam Pro và Fraunces tự host, kèm OFL.
- **Xoay túi 360°:** 24 ảnh render, kéo ngang hoặc dùng nút/phím trái–phải; Home/nút nhãn trước để đặt lại. Vuốt dọc vẫn cuộn trang. Các góc còn lại chỉ tải khi đến gần viewer; ảnh lỗi không thay ảnh đang xem.
- **Barista minh họa:** ba câu hỏi về gu, cách pha và sữa; quay lại, chỉnh hoặc làm lại. Gợi ý theo quy tắc ngay trên trang, không gửi câu trả lời ra ngoài và không lưu sau reload.
- **Nguồn hiện tại:** `source/moc-product-v02.blend`, `scripts/product_atelier.py`, `web/boutique.js`, `web/advisor.js`, `web/boutique.css`. Bản v01 và media cũ vẫn được giữ riêng.
- **Kiểm thử:** `python scripts/test_boutique.py`; báo cáo `docs/boutique-validation.md`.

Tái tạo ảnh sản phẩm Atelier v2 (ghi lại output v2):

```bash
python3 scripts/prepare_boutique.py --fonts-only
blender --factory-startup -b -t 8 --python scripts/product_atelier.py
python3 scripts/prepare_boutique.py --version 2
```

Đóng gói ảnh cần Pillow trong môi trường Python chạy `prepare_boutique.py`.

Atelier v2 đặt tên sản phẩm Cầu Đất / Arabica làm phân cấp chính, giới hạn bề ngang nội dung trên màn hình rộng, bỏ khung vòm lặp lại, đổi viewer sang cột trái và macro thành khung ngang. Bao bì có nhãn giấy và chữ ôm theo bề mặt; bộ studio dùng ánh sáng xiên, bệ đá và một tách espresso. Barista và biểu tượng pha chế cùng nét vẽ đơn sắc. Báo cáo: `docs/atelier-validation.md`; chụp/kiểm tra 20 trạng thái responsive bằng `python scripts/check_atelier.py`.

## Tái tạo video

### Khung cảnh gốc — bản hiện tại

Bản `no-connectors-2` bỏ đúng 24 viên gạch nối giữa các khu vực và render lại video/poster desktop/mobile. Bốn cảnh gốc (gồm scene 3), các đối tượng còn lại, ánh sáng và camera giữ nguyên. Nguồn biến thể: `source/moc-journey-no-connectors-v02.blend`; bản v01 còn được lưu. Chi tiết và lệnh tái tạo: `docs/connector-removal-validation.md`.

Khung hiển thị từ bản `frame-1` vẫn giữ đúng tỉ lệ, khoảng an toàn và mép mềm. Overlay Extraction Studio đã ngừng hiển thị. Chi tiết khung: `docs/frame-validation.md`.

### Khoảnh khắc chiết xuất — thử nghiệm đã ngừng hiển thị

Phần dưới là tài liệu lịch sử. Module và media được giữ để tham khảo nhưng trang hiện tại không tải chúng. Các kiểm thử loop/hotspot trong `test_extraction.py` thuộc tính năng đã bỏ; chỉ ba kiểm thử tương tác sản phẩm/tư vấn còn áp dụng.

Cảnh espresso có một studio riêng: máy pha, tách cà phê, dòng chiết xuất và gợn mặt cà phê. Khi dừng ở chương 03, cảnh chuyển bằng dissolve sang vòng lặp 6 giây; video hành trình vẫn giữ vai trò đồng hồ cuộn. Đây là chuyển cảnh có chủ đích giữa hai góc dựng, không phải nối camera khớp từng pixel.

- Vòng lặp tải khi đến chương espresso, dùng Blob để tương thích CDN; poster vẫn hiện khi tải lỗi.
- Chuyển động tạm dừng lúc cuộn, mở popup hoặc ẩn tab. Chế độ tĩnh/giảm chuyển động không tải vòng lặp.
- Hai nút khám phá đầu chiết xuất/tách dùng được bằng bàn phím; parallax nhỏ chỉ dành cho con trỏ chuột chính xác.
- Viewer sản phẩm giới thiệu bằng một lượt xoay ngắn, dừng ngay khi tương tác; reset đi đường ngắn về nhãn trước. Tư vấn có phản hồi lựa chọn và chuyển bước theo hướng tiến/lùi.

```bash
blender --factory-startup -b -t 8 --python scripts/espresso_studio.py
python3 scripts/package_extraction.py
python scripts/test_extraction.py
python scripts/check_extraction.py
```

Nguồn: `source/moc-extraction-v01.blend`, `scripts/espresso_studio.py`; 72 frame gốc mỗi khung desktop/mobile, mã hóa chậm thành 144 frame / 24 fps. Script tiếp tục từ PNG hiện có; muốn thay hình học cần lưu riêng các frame cũ trước khi dựng lại. Hơi nước là lớp CSS đặt theo tọa độ camera của tách, không phải mô phỏng chất lỏng vật lý.

Cần Blender 5.2, FFmpeg/FFprobe, ImageMagick và Python 3.10+. Chạy tại thư mục dự án:

```bash
blender -b source/moc-journey-v01.blend -t 8 --python scripts/render_journey.py -- --view desktop
blender -b source/moc-journey-v01.blend -t 8 --python scripts/render_journey.py -- --view mobile
python3 scripts/package_media.py
```

Thêm `--cpu` khi cần. `--proof` chỉ render bốn trạm; `--start 100 --end 150` render một đoạn. Script tiếp tục từ PNG đã tồn tại có đúng độ phân giải. Nếu thay đổi nội dung/camera, chuyển các frame cũ ra thư mục lưu riêng trước khi render lại.

Desktop 1280×800; mobile 720×1440 với camera/crop riêng. Mỗi video 12 giây, 288 frame, 24 fps, H.264/yuv420p, không âm thanh. Camera đi qua một thế giới liên tục; bản demo dùng góc nhìn diorama trực giao, không phải chuyển động bay xuyên bên trong từng công trình như mọi đoạn của reference.

## Dựng lại từ đầu

```bash
blender -b --factory-startup --python scripts/rebuild.py
blender -b source/moc-journey-v01.blend --python scripts/finalize_blend.py -- --journey
```

Builder từ chối nếu scene đã tồn tại. Lệnh này tạo lại các file nguồn trong dự án; giữ bản sao khi muốn bảo toàn những chỉnh sửa thủ công.

## Kiểm thử

Sau khi chạy server, dùng môi trường Python có Playwright và Chromium:

```bash
python scripts/test_web.py
python scripts/test_ux.py
python scripts/test_motion.py
python scripts/test_motion_v2.py
python scripts/test_boutique.py
python scripts/test_scroll_stops.py
```

Trên máy hiện tại đã có môi trường tương thích:

```bash
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_web.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_ux.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_motion.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_motion_v2.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_boutique.py
/home/sss/AI-Home/projects/flowbot/.venv/bin/python scripts/test_scroll_stops.py
```

Không sửa project flowbot; chỉ mượn Python/Playwright đã cài. `--static-only` kiểm tra poster trước khi video sẵn sàng.

Đợt sửa UX ngày 2026-10-06: xem `docs/ux-validation.md`. Chế độ ảnh tĩnh/video có nhãn và thông báo trạng thái rõ ràng; tải video quá 12 giây sẽ chuyển sang poster và cho thử lại. Back/Forward theo các lần chọn chương, xoay màn hình giữ tiến trình, popup khóa cuộn nền. Khi tắt JavaScript, bốn chương hiển thị thành nội dung đọc thông thường.

## Motion — Chậm một nhịp, đậm một chút

Motion v2: cảnh mở đầu tiến nhẹ trong 1,4 giây, headline hiện qua mask từng dòng. Khi camera đi giữa hai trạm, chữ giảm độ nổi rồi trở lại ở điểm đến. Đứng yên vẫn có chuyển động cảnh rất nhẹ theo chu kỳ 8 giây; chỉ cảnh chuyển động, khối chữ giữ nguyên vị trí. Marker chương trượt theo điều hướng; cuộn ngược đảo hướng reveal và chuyển nhanh hủy hiệu ứng cũ. Popup mở trong 420ms, ba hương vị cách nhau 90ms; đóng trong 220ms rồi trả focus về nút.

**Chế độ tĩnh** tắt toàn bộ motion trang trí; `prefers-reduced-motion` luôn được tôn trọng. Idle tạm dừng khi cuộn, tab ẩn hoặc popup mở. Chỉ dùng CSS và Web Animations API có sẵn trong trình duyệt, không thêm thư viện. Mở bản mới tại **http://127.0.0.1:8046/?v=motion-2#origin**; reload để xem lại intro. Chi tiết kiểm thử tại `docs/motion-validation.md`.

## Cuộn có điểm dừng

Mở **http://127.0.0.1:8046/?v=stops-1#origin**. Mỗi đợt lăn chuột đưa hành trình đến một cảnh, gom phần quán tính để tránh nhảy liên tục. Chuyển động kéo dài khoảng 620ms; cuộn ngược có thể đổi hướng ngay. Chế độ tĩnh chuyển trực tiếp.

Khu sản phẩm desktop được cân theo phần màn hình còn lại dưới header. Trên mobile hoặc màn hình thấp, nội dung dài có nhiều điểm dừng theo khối và khoảng đọc chồng nhau; không ép toàn bộ section vào một màn hình bằng cách thu nhỏ chữ. Vuốt dọc và bàn phím vẫn cuộn tự nhiên rồi căn điểm gần phù hợp. Popup, form tư vấn, thao tác zoom và kéo ngang sản phẩm được loại khỏi điều khiển lăn chuột.

Báo cáo: `docs/scroll-stops-validation.md`. Các thiết bị chuột/trackpad thực và Safari vẫn cần kiểm tra riêng.

### Polish sản phẩm và tư vấn

Bản mới: **http://127.0.0.1:8046/?v=polish-1#collection**. Tiêu đề câu hỏi/kết quả tự vào vùng đọc khi cần; kết quả dẫn đến đúng thẻ Phin, Pour-over hoặc Espresso. Chữ phụ và vùng bấm lớn hơn; phần mô tả sản phẩm giữ chiều cao khi đổi lựa chọn. Chạy `python scripts/test_polish.py`; kết quả và phạm vi kiểm tra tại `docs/polish-validation.md`.

## Xem kết quả
- `renders/farm-desktop.png` — 1600×1000, khoảng trống bên trái cho headline.
- `renders/farm-mobile.png` — 900×1200, đảo phía dưới và khoảng trống phía trên.
- `source/moc-farm-v01.blend` — scene riêng, mở bằng Blender 5.2.
- `assets/ATTRIBUTION.md` — nguồn tài nguyên.
- `docs/validation.md` — kết quả kiểm tra và thời gian render thực tế.

Toàn bộ hình học/vật liệu cảnh nông trại được tạo mới; không dùng dịch vụ trả phí.

## Render lại
Chạy từ thư mục dự án, thay `blender` bằng đường dẫn executable nếu chưa có trong PATH:

```bash
blender -b source/moc-farm-v01.blend -t 8 --python scripts/render_proof.py -- desktop --cpu
blender -b source/moc-farm-v01.blend -t 8 --python scripts/render_proof.py -- mobile --cpu
```

Bỏ `--cpu` để thử GPU. Thêm `--preview` để render 50% kích thước, 24 samples.
Script render luôn áp dụng camera/preset mới nhất từ `scripts/farm_scene.py`.

## Dựng lại từ mã nguồn
Trong Blender Python Console, dùng `importlib.util` nạp `scripts/farm_scene.py`, rồi gọi lần lượt `setup()`, `landscape()`, `plants()`, `details()`, `configure('mobile')`, `configure('desktop')`, `export()`.
Builder từ chối tạo lại nếu đã tồn tại scene `MOC - Coffee Origin`; nên dùng Blender trống cho rebuild. `export()` ghi scene library; chạy `scripts/finalize_blend.py` bằng Blender background trên file xuất để tạo project mở trực tiếp.

## Giới hạn kiểm thử

Viewport mobile được giả lập trong Chromium; chưa kiểm thử trên iPhone/Safari thật. Xem báo cáo xác minh để phân biệt kiểm tra tự động, ảnh mẫu và đánh giá chuyển động bằng mắt.
