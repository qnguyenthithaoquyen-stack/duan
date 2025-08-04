# --- Phần 1: Import các thư viện cần thiết ---
from flask import Flask, request, jsonify, render_template
import cv2
import mediapipe as mp
import numpy as np
import os

# --- Phần 2: Khởi tạo ứng dụng Flask ---
# Flask sẽ tự động tìm file HTML trong thư mục 'templates'
# và các file CSS/JS trong thư mục 'static'
app = Flask(__name__)

# --- Phần 3: Khởi tạo MediaPipe và hàm tính toán ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)

def calculate_angle(a, b, c):
    """Hàm tính góc giữa 3 điểm a, b, c (góc tại điểm b)"""
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)
    
    if angle > 180.0:
        angle = 360-angle
        
    return angle

# --- Phần 4: Tạo các đường dẫn (route) cho trang web ---

@app.route('/')
def index():
    """Hàm này sẽ trả về file index.html khi người dùng truy cập trang chủ"""
    return render_template('index.html')

@app.route('/api/analyze_image', methods=['POST'])
def analyze_image():
    """Đây là API endpoint để nhận ảnh, phân tích và trả kết quả"""
    if 'file' not in request.files:
        return jsonify({'error': 'Không có tệp nào được gửi lên'}), 400
    
    file = request.files['file']
    
    # Đọc file ảnh từ bộ nhớ để OpenCV xử lý
    filestr = file.read()
    npimg = np.frombuffer(filestr, np.uint8)
    image = cv2.imdecode(npimg, cv2.IMREAD_COLOR)
    
    # Chạy logic phân tích AI
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)
    
    errors = [] # Tạo một danh sách để lưu các lỗi tìm được
    
    if results.pose_landmarks:
        landmarks = results.pose_landmarks.landmark
        
        # Lấy tọa độ các khớp cần thiết cho đầu gối phải
        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
        
        # Tính toán góc
        knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        # Áp dụng logic phân tích lỗi và thêm vào danh sách
        if knee_angle > 160:
            errors.append(f"Cảnh báo: Đầu gối duỗi quá thẳng ({int(knee_angle)}°). Nguy cơ chấn thương dây chằng.")
        elif knee_angle < 90:
            errors.append(f"Lỗi: Đầu gối gập quá sâu ({int(knee_angle)}°). Gây áp lực lên khớp gối.")
        
        # Nếu không có lỗi nào được tìm thấy
        if not errors:
             errors.append("Tư thế tốt, không phát hiện lỗi ở đầu gối.")

    else:
        errors.append("Không thể nhận diện được tư thế trong ảnh.")
        
    # Trả kết quả về cho frontend dưới dạng JSON
    return jsonify({'errors': errors})

# --- Phần 5: Chạy ứng dụng ---
# Đoạn code này chỉ chạy khi bạn thực thi file app.py trực tiếp
if __name__ == '__main__':
    app.run(debug=True)