# Agent guide — MỘC Coffee

- Đọc README/SETUP và tài liệu validation liên quan. Web là HTML/CSS/JS tĩnh; giữ cấu trúc này, không thêm framework cho nhiệm vụ nhỏ.
- Hiện tại: `web/media/journey-v2/`, scene `moc-journey-no-connectors-v02.blend`, sản phẩm `moc-product-v02.blend`. Scene/media cũ là lịch sử, không xóa hay ghi đè tự động.
- Preserve reduced-motion, chế độ tĩnh không tải video, bàn phím, focus popup và Blob video cho CDN không hỗ trợ Range. Form/advisor chỉ demo local.
- Dùng `.venv-test` riêng với Playwright/Pillow và loopback server theo SETUP. Kiểm tra static trước, rồi hành vi bị ảnh hưởng. Không gọi toàn bộ test Extraction đã nghỉ làm gate.
- `.blend` được track như binary thông thường; không tự chuyển Git LFS hoặc render lại khi chỉ chỉnh web/docs.
- Phân biệt proof render/frame với metadata; không báo Blender/media QA đã pass nếu chỉ chạy browser/static checks.
- Output `dist/`, `renders/`, cache/venv không phải source. Chỉ deploy/commit/push khi được yêu cầu; trước publish rà diff, cập nhật setup khi liên quan, xác minh remote.
