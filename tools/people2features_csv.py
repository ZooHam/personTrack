# -*- coding: utf-8 -*-
# !@time: 19-4-27 下午9:42
# !@author: superMC @email: 18758266469@163.com
# !@fileName: people2features.py
import os
import csv
import numpy as np
import cv2
import torch
from torch.backends import cudnn

from fid.insightFace.faceNet import FaceNet
from fid.mtcnn.mtcnn import MTCNN
from fid.retinaFace.detector import Detector as RetinaFace

cudnn.benchmark = True
torch.set_grad_enabled(False)


def one_manImg(img_dir, csv_path, retinaFace_weight="fid/retinaFace/retinaFace_checkpoints/mobilenet0.25_Final.pth",
               faceNet_weigt="fid/insightFace/facenet_checkpoints/model_ir_se50.pth"):
    detector = RetinaFace(retinaFace_weight)  # choice mtcnn/retinaFace
    # detector = MTCNN()
    mobileFace = FaceNet(faceNet_weigt)
    img_paths = os.listdir(img_dir)
    if not os.path.exists(csv_path):
        print('创建数据库')
        with open(csv_path, 'w', encoding='UTF-8') as file_csv:
            writer = csv.writer(file_csv)
            header = ['Features%d' % x for x in range(512)]
            header.insert(0, 'Name')
            writer.writerow(header)

    with open(csv_path, 'r', encoding='UTF-8') as file_csv:
        reader = csv.reader(file_csv)
        names = [row[0] for row in reader][1:]
    with open(csv_path, 'a+', encoding='UTF-8') as file_csv:
        writer = csv.writer(file_csv)
        for img_path in img_paths:
            label = os.path.splitext(img_path)[0]
            if label in names:
                print('%s的数据已存在,跳过' % label)
            else:
                img_path = os.path.join(img_dir, img_path)
                image = cv2.imread(img_path)
                faces, _ = detector.forward_for_makecsv(image)
                if len(faces) == 1:
                    print('正在输入:', label)
                    cv2.imwrite('data/cache/' + os.path.split(img_path)[-1], faces[0])
                    features = mobileFace(faces[0])[0]
                    content = np.append(label, features)
                    writer.writerow(content)

                else:
                    print('%s图片不符合要求' % img_path)


def no_detect_one_manImg(img_dir, csv_path,
                         model_path="fid/insightFace/facenet_checkpoints/model_ir_se50.pth"):
    mobileFace = FaceNet(model_path)
    img_paths = os.listdir(img_dir)
    img_paths = [x for x in img_paths if x.endswith('.png') or x.endswith('.jpg')]
    if not os.path.exists(csv_path):
        print('创建数据库')
        with open(csv_path, 'w', encoding='UTF-8') as file_csv:
            writer = csv.writer(file_csv)
            header = ['Features%d' % x for x in range(512)]
            header.insert(0, 'Name')
            writer.writerow(header)

    with open(csv_path, 'r', encoding='UTF-8') as file_csv:
        reader = csv.reader(file_csv)
        names = [row[0] for row in reader][1:]

    with open(csv_path, 'a+', encoding='UTF-8') as file_csv:
        writer = csv.writer(file_csv)
        for img_path in img_paths:
            label = os.path.splitext(img_path)[0]
            if label in names:
                print('%s的数据已存在,跳过' % label)
            else:
                print('正在输入:', label)
                img_path = os.path.join(img_dir, img_path)
                face = cv2.imread(img_path)
                features = mobileFace(face)[0]
                content = np.append(label, features)
                writer.writerow(content)


if __name__ == '__main__':
    one_manImg('data/person_with_name', 'data/one_man_img.csv')
    no_detect_one_manImg('data/face_with_name', 'data/one_man_img.csv')
