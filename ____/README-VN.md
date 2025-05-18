### Cho Người Không Biết Lập Trình

Script này giống như một con robot tiện dụng tự động hóa ba nhiệm vụ lớn cho bạn: tải video từ internet, tải tệp lên lưu trữ trực tuyến và giữ một bản ghi gọn gàng về mọi thứ trên một trang web. Dưới đây là những gì nó làm một cách đơn giản:

1. **Tải Video:**
   - Bạn cung cấp cho nó một tệp văn bản với danh sách các địa chỉ web (URL) nơi có video—như liên kết đến YouTube hoặc các trang khác.
   - Script sẽ tải những video đó và lưu chúng vào một thư mục trên máy tính của bạn. Nó đặt tên cho mỗi tệp video với các chi tiết như tiêu đề, ngày tải lên và một ID video duy nhất, để dễ nhận biết.
   - Nếu một trang web yêu cầu bạn đăng nhập để tải video (như video riêng tư), script có thể sử dụng "cookies" đặc biệt (hãy nghĩ chúng như giấy phép kỹ thuật số) từ một thư mục bạn thiết lập. Nó tự động chọn cookies phù hợp dựa trên địa chỉ của trang web.

2. **Tải Tệp Lên:**
   - Sau khi video được tải xuống—hoặc nếu bạn đã có tệp trong thư mục—script sẽ lấy mọi thứ trong thư mục đó (và bất kỳ thư mục con nào) và tải chúng lên hai dịch vụ lưu trữ trực tuyến: Gofile và Pixeldrain.
   - Điều này cho bạn hai bản sao của mỗi tệp trực tuyến, rất tốt để sao lưu hoặc chia sẻ với bạn bè.
   - Đối với mỗi tệp nó tải lên, script tạo một ID duy nhất (như một mã ngẫu nhiên), ghi chú ngày tháng và lưu liên kết web nơi bạn có thể tìm thấy tệp. Nó giữ tất cả thông tin này trong một tệp có tên "upload_log.json" trên máy tính của bạn.

3. **Giữ Bản Ghi trên Trang Web:**
   - Script cũng cập nhật một trang web đặc biệt trên GitHub được gọi là "Gist." Hãy nghĩ về nó như một cuốn sổ tay trực tuyến.
   - Nó lấy thông tin từ nhật ký tải lên và thêm các mục mới vào một tệp Markdown (một tệp văn bản đơn giản có định dạng). Mỗi mục hiển thị ID duy nhất, ngày tháng và liên kết đến tệp đã tải lên.
   - Sau đó, nó gửi toàn bộ tệp Markdown đến Gist, để bạn có một danh sách cập nhật trực tuyến. Nếu chi tiết của một lần tải lên đã có ở đó, nó sẽ không thêm lại—nó thông minh như vậy!

**Cách Sử Dụng:**
- Bạn cần thiết lập một tệp có tên `.env` với một số mã bí mật (như mật khẩu) cho Gofile, Pixeldrain và GitHub, đồng thời cho biết các thư mục của bạn ở đâu.
- Chạy script bằng cách gõ một lệnh như `python combined_script.py my_urls.txt` trong terminal của máy tính, trong đó `my_urls.txt` là danh sách liên kết video của bạn.
- Script kiểm tra xem mọi thứ có được thiết lập đúng không (như đảm bảo thư mục cookies tồn tại) và dừng lại nếu có gì đó thiếu, để bạn biết cần sửa gì.

Tóm lại, script này tiết kiệm cho bạn rất nhiều thời gian bằng cách xử lý tải video, tải lên và lưu giữ bản ghi tất cả trong một lần, giữ mọi thứ ngăn nắp và dễ truy cập.

---

### Cho Người Biết Về Lập Trình

Script Python này tự động hóa việc tải video từ URL, tải tệp lên Gofile và Pixeldrain, và cập nhật một GitHub Gist với chi tiết tải lên. Nó có cấu trúc mô-đun, sử dụng biến môi trường cho cấu hình và bao gồm xử lý lỗi để tăng độ tin cậy. Dưới đây là phân tích chi tiết.

#### Các Tính Năng Chính

- **Thiết Lập Môi Trường:**
  - Tải cấu hình từ tệp `.env` bằng `dotenv`, bao gồm các token API (`GOFILE_TOKEN`, `PIXELDRAIN_API_KEY`, `GITHUB_TOKEN`), đường dẫn thư mục (`FOLDER`, `COOKIES_FOLDER`), và chi tiết Gist (`GIST_ID`, `MD_FILE`).
  - Xác nhận tất cả các biến môi trường bắt buộc và đảm bảo `COOKIES_FOLDER` là một thư mục hợp lệ, thoát với lỗi nếu không.

- **Tải Video:**
  - Sử dụng `yt_dlp` để tải video từ các URL được liệt kê trong một tệp được cung cấp làm đối số dòng lệnh.
  - Lưu tệp vào một thư mục được chỉ định với mẫu: `[title][upload_date]_id.ext`.
  - Hỗ trợ cookies cho các tải xuống yêu cầu xác thực bằng cách khớp các tệp cookies cụ thể cho từng miền (ví dụ: `youtube.com_cookies.txt`) từ `COOKIES_FOLDER`.

- **Tải Tệp Lên:**
  - Đệ quy tải tất cả các tệp từ thư mục được chỉ định lên Gofile và Pixeldrain bằng API của họ.
  - Tạo một ID 10 ký tự duy nhất cho mỗi lần tải lên bằng `generate_random_id`.
  - Ghi nhật ký mỗi lần tải lên trong `upload_log.json` với ID, ngày, tên dịch vụ và URL tải xuống.
  - Hiển thị tiến trình với thanh tiến trình `tqdm`.

- **Cập Nhật Gist:**
  - Đọc `upload_log.json`, kiểm tra các mục mới bằng cách so sánh ID với những ID trong tệp Markdown hiện có (`MD_FILE`), và thêm các mục mới với định dạng: `#### ID: {id} - {date}\n\nURL: {link}`.
  - Cập nhật GitHub Gist với nội dung Markdown đầy đủ qua yêu cầu PATCH đến GitHub API, sử dụng `GITHUB_TOKEN` để xác thực.

#### Phân Tích Hàm

- **Hàm Tiện Ích:**
  - **`generate_random_id(length=10)`**: Trả về một chuỗi ngẫu nhiên của các chữ cái và chữ số.
  - **`get_files_recursive(folder_path)`**: Sử dụng `pathlib` để liệt kê tất cả các tệp trong một thư mục và các thư mục con của nó một cách đệ quy.

- **Hàm Tải Xuống và Tải Lên:**
  - **`get_gofile_server()`**: Truy vấn API Gofile để lấy tên máy chủ tải lên.
  - **`upload_to_gofile(file_path)`**: Tải tệp lên Gofile với token, trả về URL trang tải xuống.
  - **`upload_to_pixeldrain(file_path)`**: Tải tệp lên Pixeldrain với Basic Auth, trả về URL tải xuống.
  - **`append_to_log(entry)`**: Thêm một đối tượng JSON vào `upload_log.json`, xử lý việc tạo tệp và lỗi.
  - **`download_videos(url_file, folder)`**: Tải video với `yt_dlp`, sử dụng cookies nếu có.
  - **`upload_files(folder_path)`**: Tải tất cả các tệp lên cả hai dịch vụ, ghi nhật ký mỗi thành công.

- **Hàm Cập Nhật Gist:**
  - **`update_gist(json_file, md_file, gist_id, github_token)`**: Xử lý nhật ký, cập nhật tệp Markdown và vá Gist.

- **Hàm Chính:**
  - **`main()`**: Nhận tệp URL làm `sys.argv[1]`, chạy `download_videos`, `upload_files`, và `update_gist` theo thứ tự.

#### Chi Tiết Kỹ Thuật

- **Phụ Thuộc:** `sys`, `os`, `json`, `random`, `string`, `base64`, `datetime`, `pathlib`, `requests`, `dotenv`, `tqdm`, `yt_dlp`, `urllib.parse`.
- **Xử Lý Lỗi:** Kiểm tra sự tồn tại của tệp, JSON hợp lệ, trạng thái phản hồi API và lỗi mạng, in thông báo mô tả.
- **Thực Thi:** Chạy với `python combined_script.py <url_list.txt>`.

Script này là một công cụ mạnh mẽ để tự động hóa các luồng công việc quản lý video và tệp, với cấu trúc rõ ràng dễ mở rộng hoặc gỡ lỗi.

