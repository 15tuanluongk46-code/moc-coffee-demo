# MỘC Coffee — thiết kế đã duyệt

## Mục tiêu
Demo landing page kể hành trình hạt cà phê bằng diorama 3D và video điều khiển theo cuộn. Thương hiệu hư cấu, nội dung tiếng Việt. Ưu tiên công cụ miễn phí, mã nguồn mở và tài nguyên có giấy phép rõ ràng.

## Hướng hình ảnh
Kem, xanh rừng, nâu espresso, điểm nhấn đồng; ánh sáng mềm; miniature có hình khối rõ và khoảng trống cho chữ HTML.

1. Nông trại: “Bắt đầu từ một hạt nhỏ.”
2. Rang: “Đánh thức từng tầng hương.”
3. Espresso: “Chắt lọc trong từng giọt.”
4. Ly và bao bì: “Một khoảng lặng, đậm vị.” — CTA “Khám phá hương vị”.

## Mốc hiện tại
Người dùng đã yêu cầu chạy toàn bộ một lượt, không hỏi duyệt từng cảnh (2026-10-05). Hoàn thiện bốn cảnh và website, tự kiểm tra trước khi bàn giao. Không cần tải asset nếu hình học tự dựng đáp ứng được cảnh. Asset bên ngoài chỉ dùng khi phù hợp, ưu tiên CC0, ghi nguồn nếu dùng.

## Kiến trúc giai đoạn tiếp theo
Blender xuất một hành trình camera liên tục qua bốn diorama trong cùng thế giới, FFmpeg tối ưu seek. JavaScript không phụ thuộc thư viện điều khiển tiến/lùi theo cùng nguyên lý scroll-world; bản demo tự viết engine nhỏ để dùng một video liền mạch, không cần nối clip. Chữ, điều hướng và CTA là HTML. Mobile có render camera riêng; reduced-motion hoặc media lỗi dùng ảnh tĩnh theo chương. Kiểm tra cuộn nhanh, tải và fallback trước khi bàn giao website.

## Bảo toàn dữ liệu
Tạo scene MOC riêng, xuất riêng các dependencies của scene; không ghi đè file Blender người dùng đang mở. Không gọi API trả phí, không tự commit.
