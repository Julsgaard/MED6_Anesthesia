import numpy as np
import cv2 as cv
import sys
sys.path.append('./data')
import os
import random
from PIL import Image
from torch.utils.data import Dataset
import cv2
import torchvision.transforms as transforms
import torch
import resize 
from PIL import Image,ImageChops,ImageEnhance
import skimage

expand_times=6 

def get_info(data_dir):
    data_info = []
    sub_dir_info=[]
    sub_name_info=[]
    img_name_info=[]
    for root, dirs, _ in os.walk(data_dir):
        for sub_dir in dirs:     #train/test
            sub_names = os.listdir(os.path.join(root, sub_dir))
            sub_names = list(filter(lambda x: not x.endswith('.jpg'), sub_names)) 
            for sub_name in sub_names:   # 0/1
                img_names = os.listdir(os.path.join(root, sub_dir, sub_name))
                img_names = list(filter(lambda x:x.endswith('.jpg'), img_names))  #图像名称
                for i in range(len(img_names)):
                    img_name = img_names[i]
                    path_img = os.path.join(root, sub_dir, sub_name, img_name)  #图像路径
                    img=cv.imread(path_img)
                    img=resize.resize_padding_im(img,(224,224))      #在不发生形变的情况下resize至(224,224)

                    data_info.append(img)                                    #list       
                    #data_info=np.append(data_info,img)
                    sub_dir_info=np.append(sub_dir_info,sub_dir)
                    sub_name_info=np.append(sub_name_info,sub_name)
                    img_name_info=np.append(img_name_info,img_name)                 
    #print(len(data_info),sub_dir_info.shape,sub_name_info.shape,img_name_info.shape)
    return data_info,sub_dir_info,sub_name_info,img_name_info

    
Orig_dir=os.path.join(".",r"./data/mouth")
save_path="./data/Aug_mouth/"
images,train_tests,Patient_types,image_names = get_info(Orig_dir)

for a in range(len(images)): 
    if (train_tests[a]=='train'):               #只对训练数据增强
        if (Patient_types[a]== "0"):             #Ma 1-2级记为0类
            for c in range(int(expand_times)):  #Ma 1-2级扩大6倍
                if (not os.path.exists(save_path+train_tests[a]+"/"+Patient_types[a])):
                    os.makedirs(save_path+train_tests[a]+"/"+Patient_types[a]) 
                dir=save_path+train_tests[a]+"/"+Patient_types[a]  
                image=Image.fromarray(np.uint8(images[a]))
                transform = transforms.Compose([       #数据增强的形式
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(7),
                #transforms.RandomAffine( degrees=2, translate=(0.01,0.01),shear=( 0.05, 0.05), resample=False),
                transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.05),
                transforms.Resize([230, 230]),
                transforms.RandomCrop([224, 224])
                ])
                image=transform(image)
                #images[a] = np.array(image)
                cv.imwrite(os.path.join(dir,str(c)+"_"+image_names[a]),np.array(image))


        if (Patient_types[a]== "1" ):      #Ma 3-4级记为1类
            for b in range(expand_times*2): #Ma 3-4级扩大12倍
                if (not os.path.exists(save_path+train_tests[a]+"/"+Patient_types[a])):
                    os.makedirs(save_path+train_tests[a]+"/"+Patient_types[a]) 
                dir=save_path+train_tests[a]+"/"+Patient_types[a]  
                image=Image.fromarray(np.uint8(images[a]))
                transform = transforms.Compose([        #数据增强的形式
                transforms.RandomHorizontalFlip(),
                transforms.RandomRotation(7),
                #transforms.RandomAffine( degrees=2, translate=(0.01,0.01),shear=( 0.05, 0.05), resample=False),
                transforms.ColorJitter(brightness=0.1, contrast=0.1, saturation=0.1, hue=0.05),
                transforms.Resize([230, 230]),
                transforms.RandomCrop([224, 224])
                ])
                image=transform(image)
                #images[a] = np.array(image)
                cv.imwrite(os.path.join(dir,str(b)+"_"+image_names[a]),np.array(image))

               
    else:   #测试数据不增强 直接另存
        if (not os.path.exists(save_path+train_tests[a]+"/"+Patient_types[a])):                                   
            os.makedirs(save_path+train_tests[a]+"/"+Patient_types[a])
        dir=save_path+train_tests[a]+"/"+Patient_types[a]
        cv.imwrite(os.path.join(dir,image_names[a]),images[a])
    



    


