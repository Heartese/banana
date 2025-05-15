from flask import Flask, render_template, request, redirect, url_for, Response, jsonify
from werkzeug.utils import secure_filename
import cv2
from ultralytics import YOLO
import numpy as np
from PIL import Image
import io
import base64

app = Flask(__name__)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

banana_ripeness_detection_model = YOLO("C:/Program Files/Python311/Fruit-Ripeness-Detection-main/banana_flask/yolov8_train_output/content/runs/detect/train/weights/best.pt")

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')


@app.route('/detect_objects', methods=['POST'])
def detect_objects():
    image_data = request.json['image_data'].split(',')[1]  
    image_bytes = base64.b64decode(image_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    image = cv2.imdecode(image_array, cv2.IMREAD_COLOR)
    results = fruit_detection_model(image)

    detected_objects = []
    for result in results:
        boxes = result.boxes.xywh.cpu()  
        clss = result.boxes.cls.cpu().tolist()  
        names = result.names 
        confs = result.boxes.conf.float().cpu().tolist()  
        for box, cls, conf in zip(boxes, clss, confs):
            detected_objects.append({'class': names[cls], 'bbox': box.tolist(), 'confidence': conf})

    return jsonify(detected_objects)


@app.route('/disease_detection')
def ripeness_detection():
    return render_template('disease_detection.html')


@app.route('/banana_detection', methods=['GET', 'POST'])
def banana_detection():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            img = Image.open(io.BytesIO(file.read())).convert("RGB")
            class_names = detect_ripeness(banana_ripeness_detection_model, img)
            img_str = image_to_base64(img)
            return render_template('uploaded_image.html', img_str=img_str, class_names=class_names)
    return render_template('banana_detection.html')

def detect_ripeness(model, image):
    results = model(image)
    class_names = []

    for result in results:
        boxes = result.boxes
        if boxes is not None:
            clss = boxes.cls.cpu().tolist()
            for cls in clss:
                class_name = result.names[int(cls)]
                if "ripe" in class_name.lower():
                    class_names.append(class_name)

    return class_names


def image_to_base64(image):
    buffered = io.BytesIO()
    image.save(buffered, format="JPEG")
    return base64.b64encode(buffered.getvalue()).decode()


@app.route('/uploads/<filename>')
def uploaded_image(filename):
    return render_template('uploaded_image.html', filename=filename)



if __name__ == '__main__':
    app.run(host="0.0.0.0", port=4000, debug=True)

