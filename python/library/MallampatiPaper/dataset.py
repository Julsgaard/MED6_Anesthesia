import os
import random
from tkinter import Label
from PIL import Image
from torch.utils.data import Dataset
import cv2 as cv
import numpy as np

random.seed(1)

class MaDataset(Dataset):
    def __init__(self, data_dir, transform=None):
        self.transform = transform
        self.data_info = self.get_img_info(data_dir)

    def __getitem__(self, index):
        path_img, label = self.data_info[index]
        img = Image.open(path_img).convert('RGB')
        if self.transform is not None:
            img = self.transform(img)
        return img, label

    def __len__(self):
        return len(self.data_info)

    def get_img_info(self, data_dir):
        data_info = list()
        # print(f'Scanning directory: {data_dir}')
        for root, dirs, _ in os.walk(data_dir):
            # print(f'Found subdirectories: {dirs} in {root}')
            for sub_dir in dirs:
                full_dir_path = os.path.join(root, sub_dir)
                img_names = os.listdir(full_dir_path)
                # print(f'Files in {full_dir_path}: {img_names}')
                img_names = list(filter(lambda x: x.endswith('.jpeg') or x.endswith('.jpg'), img_names))
                # print(f'Filtered JPEG images in {sub_dir}: {img_names}')

                for i in range(len(img_names)):
                    img_name = img_names[i]
                    path_img = os.path.join(root, sub_dir, img_name)
                    # Assign labels based on directory name
                    if sub_dir == 'Class1+2':
                        label = 0  # Assign 0 for Class1+2
                    elif sub_dir == 'Class3+4':
                        label = 1  # Assign 1 for Class3+4
                    else:
                        raise ValueError(f"Unexpected directory name: {sub_dir}")
                    data_info.append((path_img, label))
                    #print(f'Added image: {path_img, label}')
                    #print(f'Added image: {path_img, label}')
        # print(f'Total images found: {len(data_info)}')
        unique_labels = set([label for _, label in data_info])
        # print(f'Unique labels: {unique_labels}')
        return data_info


class M_Dataset(Dataset):
    # 自定义Dataset类，必须继承Dataset并重写__init__和__getitem__函数
    def __init__(self, data_dir):
        # data_info存储所有融合后的特征向量和对应的标签（元组的列表），在DataLoader中通过index读取样本
        self.data_info = self.get_img_info(data_dir)

    def __getitem__(self, index):
        vetor, label = self.data_info[index]
        #print(vetor.shape,label)
        return vetor, label

    def __len__(self):
        return len(self.data_info)

    # 自定义方法，用于融合后的特征向量以及标签
    @staticmethod
    def get_img_info(data_dir):
        data_info = list()
        split_dir=os.path.join(".","data","Aug_mouth")
        train_dir=os.path.join(split_dir,"Trian_all")   #Trian_all是所有的训练数据
        test_dir=os.path.join(split_dir,"test")   #测试数据
        if (data_dir==train_dir):
            x_hog  = np.load('./Train_HOG_futures.npy')
            x_lbp  = np.load('./Train_LBP_futures.npy')
            x_deep = np.load('./Train_deep_futures.npy')
            x_hand=np.concatenate((x_hog, x_lbp), axis=1)
            x_fusion =np.concatenate((x_hand, x_deep), axis=1)
            y      = np.load('./Train_Label.npy')
        if (data_dir==test_dir):
            x_hog  = np.load('./Test_HOG_futures.npy')
            x_lbp  = np.load('./Test_LBP_futures.npy')
            x_deep = np.load('./Test_deep_futures.npy')
            x_hand=np.concatenate((x_hog, x_lbp), axis=1)
            x_fusion =np.concatenate((x_hand, x_deep), axis=1)
            y      = np.load('./Test_Label.npy')
        for i in range(len(y)):
            data_info.append((x_fusion[i],int(y[i])))
        return data_info


