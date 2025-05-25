# 用于人脸数据训练
import cv2
import os
import numpy as np
def train_model(data_dir='files/face_pictures'):
    recognizer = cv2.face.LBPHFaceRecognizer_create()

    detector = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
    faces = []
    labels = []
    label_dict = {}
    current_label = 0

    # 遍历训练数据
    for root, dirs, files in os.walk(data_dir):
        for name in dirs:
            label_dict[current_label] = name
            subject_dir = os.path.join(root, name)

            for filename in os.listdir(subject_dir):
                if filename.startswith('.'):
                    continue

                path = os.path.join(subject_dir, filename)
                img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
                face = detector.detectMultiScale(img)

                if len(face) == 1:
                    x, y, w, h = face[0]
                    faces.append(img[y:y + h, x:x + w])
                    labels.append(current_label)

            current_label += 1

    # 训练模型
    recognizer.train(faces, np.array(labels))
    recognizer.save('files/face_data/face_model.yml')
    return label_dict
