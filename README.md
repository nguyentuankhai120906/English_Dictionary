# English Dictionary - Radix Trie Implementation

Dự án này là một ứng dụng Từ điển Tiếng Anh mã nguồn mở, sử dụng cấu trúc dữ liệu **Radix Trie** (một biến thể tối ưu của Trie) để lưu trữ và truy xuất từ vựng hiệu quả. Dự án bao gồm hai phiên bản: một ứng dụng chạy trên trình duyệt web và một ứng dụng dòng lệnh (CLI) bằng ngôn ngữ Python.

---

## 1. Phiên bản Web (Giao diện trực quan)

Đây là phiên bản dành cho người dùng muốn trải nghiệm nhanh giao diện đồ họa và xem cấu trúc cây một cách trực quan.

### Cách sử dụng:
1. **Tải về:** Tải file `English_Dictionary.html` về máy tính của bạn.
2. **Mở ứng dụng:** Nhấp đúp chuột vào file hoặc chuột phải chọn **Open with...** và chọn trình duyệt web (Chrome, Edge, Firefox, v.v.).
3. **Các tính năng chính:**
   * **Tìm kiếm (Search):** Nhập từ cần tra để xem nghĩa.
   * **Thêm từ (Add):** Nhập từ mới và định nghĩa vào các ô tương ứng.
   * **Xóa từ (Delete):** Nhập từ muốn xóa khỏi hệ thống.
   * **Trực quan hóa (Trie Visualization):** Phía bên dưới có sơ đồ cấu trúc cây, giúp bạn hiểu cách các từ được "nén" lại trong Radix Trie như thế nào.

---

## 2. Phiên bản Python (Mã nguồn & CLI)

Phiên bản này dành cho các bạn muốn tìm hiểu sâu về code hoặc chạy ứng dụng trong môi trường terminal.

### Yêu cầu hệ thống:
* Máy tính đã cài đặt **Python 3.10** trở lên.
* Một trình soạn thảo code như VS Code hoặc PyCharm.

### Cấu trúc file:
* `radix_trie.py`: Chứa logic cốt lõi của cấu trúc dữ liệu Radix Trie (Insert, Search, Delete, Prefix Search).
* `main.py`: File thực thi chính. Cung cấp giao diện menu điều khiển.
* `test_trie.py`: File chứa các unit test để kiểm tra độ chính xác của thuật toán.

### Cách chạy chương trình:
1. Giải nén file `English_Dictionary.zip`.
2. Mở Terminal (hoặc Command Prompt) tại thư mục vừa giải nén.
3. Chạy lệnh sau để khởi động ứng dụng:
   ```bash
   python main.py
