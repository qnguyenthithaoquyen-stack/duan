// Import các công cụ cần thiết từ thư viện MediaPipe
import { PoseLandmarker, FilesetResolver } from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/vision_bundle.js";

// Lấy các phần tử HTML
const imageInput = document.getElementById('imageInput');
const analyzeButton = document.getElementById('analyzeButton');
const previewImage = document.getElementById('previewImage');
const resultsDiv = document.getElementById('results');

let poseLandmarker;
let selectedFile;

// Hàm khởi tạo mô hình AI
async function createPoseLandmarker() {
    const vision = await FilesetResolver.forVisionTasks("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm");
    poseLandmarker = await PoseLandmarker.createFromOptions(vision, {
        baseOptions: {
            modelAssetPath: `https://storage.googleapis.com/mediapipe-models/pose_landmarker/pose_landmarker_lite/float16/1/pose_landmarker_lite.task`,
            delegate: "GPU"
        },
        runningMode: "IMAGE",
        numPoses: 1
    });
    analyzeButton.disabled = false;
    analyzeButton.textContent = "Phân Tích";
    console.log("Pose Landmarker is ready.");
}

// Chạy hàm khởi tạo
analyzeButton.disabled = true;
analyzeButton.textContent = "Đang tải mô hình AI...";
createPoseLandmarker();

// Xử lý khi người dùng chọn ảnh
imageInput.addEventListener('change', (event) => {
    selectedFile = event.target.files[0];
    if (selectedFile) {
        previewImage.src = URL.createObjectURL(selectedFile);
    }
});

// Hàm tính góc
function calculateAngle(a, b, c) {
    const radians = Math.atan2(c.y - b.y, c.x - b.x) - Math.atan2(a.y - b.y, a.x - b.x);
    let angle = Math.abs(radians * 180.0 / Math.PI);
    if (angle > 180.0) {
        angle = 360 - angle;
    }
    return angle;
}

// Xử lý khi nhấn nút Phân Tích
analyzeButton.addEventListener('click', async () => {
    if (!selectedFile || !poseLandmarker) {
        alert("Vui lòng chọn ảnh hoặc chờ mô hình AI tải xong!");
        return;
    }

    resultsDiv.innerHTML = "<p>Đang phân tích, vui lòng chờ...</p>";

    // Chạy phân tích
    const landmarks = poseLandmarker.detect(previewImage);
    const errors = [];

    if (landmarks.landmarks.length > 0) {
        const pose = landmarks.landmarks[0];

        // Lấy tọa độ các khớp quan trọng
        const rightHip = pose[24];
        const rightKnee = pose[26];
        const rightAnkle = pose[28];
        
        // Tính toán góc
        const kneeAngle = calculateAngle(rightHip, rightKnee, rightAnkle);
        
        // Logic phân tích lỗi
        if (kneeAngle > 160) {
            errors.push(`Cảnh báo: Đầu gối duỗi quá thẳng (${Math.round(kneeAngle)}°). Nguy cơ chấn thương dây chằng.`);
        } else if (kneeAngle < 90) {
            errors.push(`Lỗi: Đầu gối gập quá sâu (${Math.round(kneeAngle)}°). Gây áp lực lên khớp gối.`);
        }

        if (errors.length === 0) {
            errors.push("Tư thế tốt, không phát hiện lỗi ở đầu gối.");
        }
    } else {
        errors.push("Không thể nhận diện được tư thế trong ảnh.");
    }

    // Hiển thị kết quả
    let htmlResult = '<ul>';
    errors.forEach(error => { htmlResult += `<li>${error}</li>`; });
    htmlResult += '</ul>';
    resultsDiv.innerHTML = htmlResult;
});