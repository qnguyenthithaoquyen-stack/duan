// Đợi cho toàn bộ nội dung trang web được tải xong rồi mới chạy code
document.addEventListener('DOMContentLoaded', () => {
    // Lấy các phần tử trên trang web bằng ID của chúng
    const imageInput = document.getElementById('imageInput');
    const analyzeButton = document.getElementById('analyzeButton');
    const previewImage = document.getElementById('previewImage');
    const resultsDiv = document.getElementById('results');

    let selectedFile; // Biến để lưu file ảnh người dùng đã chọn

    // Xử lý sự kiện khi người dùng chọn một file ảnh
    imageInput.addEventListener('change', (event) => {
        selectedFile = event.target.files[0];
        if (selectedFile) {
            // Hiển thị ảnh xem trước
            previewImage.src = URL.createObjectURL(selectedFile);
            previewImage.style.display = 'block'; // Đảm bảo ảnh hiển thị
        }
    });

    // Xử lý sự kiện khi người dùng nhấn nút "Phân Tích"
    analyzeButton.addEventListener('click', () => {
        // Kiểm tra xem đã chọn file chưa
        if (!selectedFile) {
            alert('Vui lòng chọn một ảnh để phân tích!');
            return;
        }

        // Hiển thị thông báo đang xử lý
        resultsDiv.innerHTML = '<p>Đang phân tích, vui lòng chờ...</p>';
        
        // Tạo một đối tượng FormData để gửi file đi
        const formData = new FormData();
        formData.append('file', selectedFile);

        // Gửi yêu cầu đến API của backend (Flask)
        fetch('/api/analyze_image', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json()) // Chuyển đổi phản hồi thành dạng JSON
        .then(data => {
            // Hiển thị kết quả trả về từ backend
            if (data.errors) {
                let htmlResult = '<ul>';
                data.errors.forEach(error => {
                    htmlResult += `<li>${error}</li>`;
                });
                htmlResult += '</ul>';
                resultsDiv.innerHTML = htmlResult;
            } else {
                resultsDiv.innerHTML = '<p>Có lỗi xảy ra trong quá trình phân tích.</p>';
            }
        })
        .catch(error => {
            // Xử lý nếu có lỗi mạng
            console.error('Lỗi:', error);
            resultsDiv.innerHTML = '<p>Không thể kết nối đến máy chủ phân tích. Hãy đảm bảo bạn đã chạy file app.py.</p>';
        });
    });
});