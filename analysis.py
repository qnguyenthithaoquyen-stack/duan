import cv2
import mediapipe as mp
import numpy as np

# --- Phần 1: Khởi tạo MediaPipe ---
mp_pose = mp.solutions.pose
pose = mp_pose.Pose(static_image_mode=True, min_detection_confidence=0.5)
mp_drawing = mp.solutions.drawing_utils

# --- Phần 2: Hàm tính góc ---
def calculate_angle(a, b, c):
    """Hàm tính góc giữa 3 điểm a, b, c (góc tại b)"""
    a = np.array(a) # Điểm đầu
    b = np.array(b) # Điểm giữa (đỉnh góc)
    c = np.array(c) # Điểm cuối

    # Tính vector từ b đến a và từ b đến c
    radians = np.arctan2(c[1]-b[1], c[0]-b[0]) - np.arctan2(a[1]-b[1], a[0]-b[0])
    angle = np.abs(radians*180.0/np.pi)

    if angle > 180.0:
        angle = 360-angle

    return angle

# --- Phần 3: Phân tích ảnh ---
file_path = 'test_image.jpg.jpg'
image = cv2.imread(file_path)

# THÊM ĐOẠN KIỂM TRA NÀY VÀO
if image is None:
    print(f"LỖI: Không thể đọc được file ảnh tại đường dẫn: {file_path}")
    print("Vui lòng kiểm tra lại tên file, phần mở rộng, và đảm bảo file không bị hỏng.")
else:
    # Tất cả các dòng này phải bắt đầu ở cùng một mức thụt lề
    image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
    results = pose.process(image_rgb)

    if results.pose_landmarks:
        # Code bên trong if này sẽ được thụt vào một mức nữa
        landmarks = results.pose_landmarks.landmark
        
        right_hip = [landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_HIP.value].y]
        right_knee = [landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_KNEE.value].y]
        right_ankle = [landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].x, landmarks[mp_pose.PoseLandmark.RIGHT_ANKLE.value].y]
        
        knee_angle = calculate_angle(right_hip, right_knee, right_ankle)
        
        if knee_angle > 160:
            print("Cảnh báo: Đầu gối duỗi quá thẳng khi tiếp đất!")
        elif knee_angle < 90:
            print("Lỗi: Đầu gối gập quá sâu!")

        mp_drawing.draw_landmarks(image, results.pose_landmarks, mp_pose.POSE_CONNECTIONS)

    # Các dòng này phải thẳng hàng với dòng 'if' và 'image_rgb' ở trên
    cv2.imshow('MediaPipe Pose Analysis', image)
    cv2.waitKey(0) 
    cv2.destroyAllWindows()