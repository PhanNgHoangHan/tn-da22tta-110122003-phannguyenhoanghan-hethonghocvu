# ĐỒ ÁN TỐT NGHIỆP: HỆ THỐNG QUẢN LÝ HỌC VỤ VÀ CẢNH BÁO HỌC VỤ SINH VIÊN (ĐẠI HỌC TRÀ VINH)

## Giới thiệu chung
Hệ thống Quản lý học vụ và Cảnh báo học vụ sinh viên là một dự án được thiết kế nhằm mục đích hỗ trợ Phòng Đào tạo (Giáo vụ), Cố vấn học tập (CVHT) và Sinh viên trong việc theo dõi thông tin học tập, quản lý điểm số, chương trình đào tạo và tự động tính toán, phát hiện các trường hợp sinh viên có nguy cơ bị cảnh báo học vụ hoặc buộc thôi học dựa trên Quy chế Đào tạo Tín chỉ của **Trường Đại học Trà Vinh (TVU)**.

Hệ thống được phát triển bằng ngôn ngữ **Python** kết hợp với framework **Django**, cơ sở dữ liệu **SQLite** và giao diện web thân thiện, tương thích với nhiều thiết bị.

---

## Các tính năng chính

### 1. Phân quyền và Quản lý Người dùng
Hệ thống hỗ trợ 4 vai trò chính với các quyền truy cập riêng biệt:
*   **Quản trị viên (Admin):** Quản lý toàn bộ người dùng, phân quyền hệ thống và cấu hình hệ thống.
*   **Giáo vụ (giaovu):** Quản lý chương trình đào tạo (môn học, ngành học, lớp học, học kỳ), quản lý hồ sơ sinh viên, import danh sách sinh viên, môn học và kết quả học tập từ Excel.
*   **Cố vấn học tập (covan):** Quản lý lớp học được phân công phụ trách, xem danh sách sinh viên, kết quả học tập của từng sinh viên trong lớp, xuất báo cáo danh sách cảnh báo học vụ ra file Excel, gửi email báo cáo cảnh báo học vụ cho Khoa/Trường, gửi email cảnh báo sớm cho sinh viên có nguy cơ.
*   **Sinh viên (sinhvien):** Xem thông tin cá nhân, cố vấn học tập phụ trách, xem kết quả học tập chi tiết theo từng học kỳ, xem thống kê điểm trung bình học kỳ (ĐTBCHK), điểm trung bình tích lũy (ĐTBCTL), số tín chỉ nợ đọng, và lịch sử cảnh báo học vụ của bản thân.

### 2. Thuật toán Tự động Tính toán & Cảnh báo Học vụ (Theo Quy chế TVU)
Hệ thống tự động phân tích điểm tổng kết môn học ($ĐTgK = \frac{ĐTBQT + ĐKT}{2}$) để quy đổi ra điểm chữ ($A, B+, B, C+, C, D+, D, F$) và điểm hệ 4 ($4.0 \rightarrow 0.0$).
Từ kết quả học tập của sinh viên ở mỗi học kỳ chính, hệ thống tự động quét 4 điều kiện cảnh báo học vụ:
1.  **Số tín chỉ không đạt trong học kỳ:** Vượt quá 50% số tín chỉ đăng ký học trong học kỳ đó.
2.  **Số tín chỉ nợ đọng từ đầu khóa:** Tổng số tín chỉ nợ đọng (điểm F chưa học cải thiện đạt) tích lũy vượt quá **24 tín chỉ**.
3.  **Điểm trung bình học kỳ (ĐTBCHK - hệ 4):**
    *   Dưới **0.80** đối với học kỳ đầu tiên của khóa học.
    *   Dưới **1.00** đối với các học kỳ tiếp theo.
4.  **Điểm trung bình tích lũy (ĐTBCTL - hệ 4):**
    *   Dưới **1.20** đối với sinh viên năm thứ nhất.
    *   Dưới **1.40** đối với sinh viên năm thứ hai.
    *   Dưới **1.60** đối với sinh viên năm thứ ba.
    *   Dưới **1.80** đối với sinh viên các năm tiếp theo.

*   **Buộc thôi học:** Sinh viên bị cảnh báo học vụ **vượt quá 2 lần liên tiếp**.
*   *Lưu ý:* Các môn Giáo dục thể chất và Giáo dục quốc phòng (mã môn bắt đầu bằng `19` và không phải `190`) được loại trừ khỏi thuật toán tính điểm trung bình (GPA) nhưng vẫn tính tín chỉ đạt/không đạt.

### 3. Import & Export Dữ liệu Hàng loạt
*   Import danh sách sinh viên, danh sách môn học/chương trình đào tạo và bảng điểm học kỳ từ file Excel (`.xlsx`).
*   Tự động phát hiện lỗi trùng lặp dữ liệu, thiếu thông tin môn học, mã sinh viên không tồn tại trong file excel trước khi nạp vào DB.
*   Xuất danh sách sinh viên bị cảnh báo học vụ và thống kê học tập ra file Excel phục vụ lưu trữ báo cáo.

### 4. Gửi email Báo cáo & Cảnh báo học vụ sớm
*   Cố vấn học tập có thể gửi báo cáo danh sách cảnh báo của lớp trực tiếp qua Email.
*   Hệ thống hỗ trợ gửi Email cảnh báo sớm riêng cho từng sinh viên kèm chi tiết lý do và lời khuyên định hướng học tập.

---

## Công nghệ sử dụng
*   **Ngôn ngữ chính:** Python (phiên bản 3.10 trở lên)
*   **Web Framework:** Django
*   **Thư viện xử lý Excel:** `openpyxl`
*   **Cơ sở dữ liệu:** SQLite (mặc định)
*   **Frontend:** Bootstrap, CSS tùy chỉnh (Custom TVU Brand), Javascript, Chart.js (vẽ biểu đồ phân phối điểm và thống kê).

---

## Hướng dẫn cài đặt và chạy đồ án

### Bước 1: Chuẩn bị môi trường
Yêu cầu máy tính đã cài đặt Python (Khuyến nghị phiên bản 3.10 đến 3.13) và Git.

1.  Mở Terminal / PowerShell và di chuyển vào thư mục gốc của đồ án:
    ```bash
    cd đường_dẫn_đến_thư_mục_DB_CBHV
    ```
2.  Khởi tạo môi trường ảo Python (Virtual Environment) để tránh xung đột thư viện:
    ```bash
    # Trên Windows:
    python -m venv venv
    
    # Trên macOS/Linux:
    python3 -m venv venv
    ```
3.  Kích hoạt môi trường ảo:
    ```bash
    # Trên Windows (PowerShell):
    .\venv\Scripts\Activate.ps1
    
    # Trên Windows (Command Prompt):
    .\venv\Scripts\activate.bat
    
    # Trên macOS/Linux:
    source venv/bin/activate
    ```

### Bước 2: Cài đặt các thư viện cần thiết
Cài đặt Django và thư viện openpyxl phục vụ đọc/ghi file Excel:
```bash
pip install django openpyxl
```

### Bước 3: Di cư cơ sở dữ liệu (Database Migrations)
Khởi tạo cấu trúc bảng trong cơ sở dữ liệu SQLite:
```bash
# Di chuyển vào thư mục chứa mã nguồn src
cd src

# Thực hiện đồng bộ database
python manage.py makemigrations
python manage.py migrate
```

### Bước 4: Nạp dữ liệu thử nghiệm (Seeding Data)
Hệ thống đi kèm các lệnh tự động (custom management commands) để nạp trước học kỳ, môn học thực tế của TVU cùng dữ liệu mẫu để bạn chạy thử ngay lập tức:

1.  **Nạp danh sách học kỳ và môn học thực tế:**
    ```bash
    python manage.py load_monhoc
    ```
2.  **Tạo dữ liệu mẫu chung (Admin, Giáo vụ, Cố vấn, 30 Sinh viên kèm điểm & cảnh báo):**
    ```bash
    python manage.py seed_data
    ```
3.  **Tạo dữ liệu mẫu riêng cho Sinh viên Phan Nguyễn Hoàng Hân (mssv: 110122003) kèm kịch bản bị cảnh báo học vụ ở Học kỳ 1 (2022-2023) và Học kỳ 1 (2025-2026):**
    ```bash
    python manage.py add_sv_han
    ```

### Bước 5: Khởi chạy Server
Chạy server cục bộ để bắt đầu sử dụng ứng dụng:
```bash
python manage.py runserver
```
Sau khi chạy lệnh trên, truy cập ứng dụng thông qua trình duyệt web tại địa chỉ: [http://127.0.0.1:8000/](http://127.0.0.1:8000/)

---

## Danh sách tài khoản thử nghiệm
Sau khi chạy các lệnh nạp dữ liệu ở **Bước 4**, bạn có thể đăng nhập bằng các tài khoản mẫu sau:

| Vai trò | Tên đăng nhập (Username) | Mật khẩu (Password) | Mô tả / Nhiệm vụ thử nghiệm |
| :--- | :--- | :--- | :--- |
| **Quản trị viên** | `admin` | `admin123` | Quản trị viên hệ thống, truy cập trang `/admin/`. |
| **Giáo vụ** | `giaovu1` | `giaovu123` | Quản lý danh sách sinh viên, môn học, nhập điểm. |
| **Cố vấn học tập** | `covan1` | `covan123` | Phụ trách lớp `CNTT21A`. Gửi email báo cáo lớp. |
| **Cố vấn học tập** | `covan2` | `covan123` | Phụ trách lớp `KTPM21A`. |
| **Sinh viên mẫu** | `sv001` | `sv123` | Sinh viên xem điểm và trạng thái học tập cá nhân. |
| **Sinh viên Hân** | `110122003` | `110122003` | Sinh viên **Phan Nguyễn Hoàng Hân** lớp `DA22TTA` (Bị cảnh báo 2 lần). |

---

## Cấu hình Gửi Email (Không bắt buộc)
Để chạy tính năng gửi email báo cáo lớp hoặc email cảnh báo học tập sớm cho sinh viên, hệ thống sử dụng cấu hình SMTP Gmail.
Mặc định hệ thống đã được cấu hình với tài khoản thử nghiệm trong `settings.py`. Nếu bạn muốn cấu hình tài khoản Gmail của riêng mình:
1.  Bật chế độ xác thực 2 bước cho tài khoản Google của bạn.
2.  Tạo **Mật khẩu ứng dụng (App Password)** cho ứng dụng thư.
3.  Cấu hình các biến môi trường trên máy tính hoặc chỉnh sửa trực tiếp trong `src/config/settings.py` (dòng 98-99):
    ```python
    EMAIL_HOST_USER = 'your-email@gmail.com'
    EMAIL_HOST_PASSWORD = 'your-app-password-16-chars'
    ```
*(Nếu không cấu hình SMTP, hệ thống sẽ tự động chuyển sang chế độ `console` - in nội dung email trực tiếp ra màn hình terminal chạy code).*

---

## Cấu trúc thư mục dự án
```text
DB_CBHV/
├── docs/                      # Tài liệu đồ án (PDF, DOCX)
└── src/                       # Thư mục mã nguồn Django chính
    ├── config/                # Cài đặt cấu hình hệ thống (settings.py, urls.py)
    ├── accounts/              # Module Quản lý tài khoản & Phân quyền
    ├── students/              # Module Quản lý Ngành, Lớp, Sinh viên & CTĐT
    ├── results/               # Module Quản lý Điểm & Tính toán Cảnh báo
    ├── academic_warnings/     # Module Quản lý Cảnh báo học vụ, lịch sử gửi email
    ├── dashboard/             # Giao diện Trang chủ và các Báo cáo thống kê
    ├── static/                # Tài nguyên tĩnh (CSS, JS, Hình ảnh)
    ├── templates/             # Giao diện HTML (Base & các module)
    ├── db.sqlite3             # File cơ sở dữ liệu SQLite
    └── manage.py              # File quản lý chạy lệnh của Django
```

---
*Chúc bạn bảo vệ đồ án tốt nghiệp thành công đạt kết quả cao nhất!*
