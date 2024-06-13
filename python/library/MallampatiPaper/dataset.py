import os
import random
from tkinter import Label
from PIL import Image
from torch.utils.data import Dataset
import cv2 as cv
import numpy as np

random.seed(1)

class MaDataset(Dataset):
    # 自定义Dataset类，必须继承Dataset并重写__init__和__getitem__函数
    def __init__(self, data_dir, transform=None):
        # data_info存储所有图片路径和标签（元组的列表），在DataLoader中通过index读取样本
        self.data_info = self.get_img_info(data_dir)
        self.transform = transform

    def __getitem__(self, index):
        path_img, label = self.data_info[index]
        # 打开图片，默认为PIL，需要转成RGB
        img = Image.open(path_img).convert('RGB')
        # 如果预处理的条件不为空，应该进行预处理操作
        if self.transform is not None:
            img = self.transform(img)
        return img, label      #返回RGB图像及标签

    def __len__(self):
        return len(self.data_info)

    # 自定义方法，用于返回所有图片的路径以及标签
    @staticmethod
    def get_img_info(data_dir):
        data_info = list()
        for root, dirs, _ in os.walk(data_dir):
            # 遍历类别
            for sub_dir in dirs:           #0 1
                # listdir为列出文件夹下所有文件和文件夹名
                img_names = os.listdir(os.path.join(root, sub_dir))
                # 过滤出所有后缀名为jpg的文件名（那当然也就把文件夹过滤掉了）
                img_names = list(filter(lambda x: x.endswith('.jpg'), img_names))      #图
                # 遍历图片
                for i in range(len(img_names)):
                    img_name = img_names[i]
                    path_img = os.path.join(root, sub_dir, img_name)
                    # 在我们的命名设置中，文件夹名等于标签名
                    label = sub_dir
                    data_info.append((path_img, int(label)))
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


