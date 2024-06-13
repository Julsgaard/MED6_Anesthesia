import sys
sys.path.append('./data')
import os
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
from dataset import MaDataset
from VGG19_CA import VGG19CA
from torch.autograd import Variable
from library.mallampati_image_prep import prepare_loader

#宏定义一些数据
BATCH_SIZE=16
a,b=[],[]

# ================================ step 1/3 数据 =================================
#split_dir=os.path.join(".","data","Aug_mouth")
#train_dir=os.path.join('C:\\Users\Kristian\Desktop\Github\MED6_Anesthesia\python\library\mallampati_datasets\\training_data')   #Train_all所有的训练数据
#test_dir=os.path.join('C:\\Users\Kristian\Desktop\Github\MED6_Anesthesia\python\library\mallampati_datasets\\test_data')       #测试数据

#对训练集所需要做的预处理   
train_transform=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.485,0.456,0.406),(0.229,0.224,0.225))
])
#对测试集所需要做的预处理
test_transform=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.485,0.456,0.406),(0.229,0.224,0.225))
])

# 构建MyDataset实例
#train_data=MaDataset(data_dir=train_dir,transform=train_transform)
#test_data=MaDataset(data_dir=test_dir,transform=test_transform)

# 构建DataLoader
# 训练集数据不做打乱
# DataLoader的实质就是把数据集加上一个索引号，再返回
#train_loader=DataLoader(dataset=train_data,batch_size=BATCH_SIZE,shuffle=False)
#test_loader=DataLoader(dataset=test_data,batch_size=BATCH_SIZE)

train_loader = prepare_loader(path='C:\\Users\Kristian\Desktop\Github\MED6_Anesthesia\python\library\mallampati_datasets\\training_data', image_pixel_size=224, normalization=False,
                              data_augmentation=True)
test_loader = prepare_loader(path='C:\\Users\Kristian\Desktop\Github\MED6_Anesthesia\python\library\mallampati_datasets\\test_data', image_pixel_size=224, normalization=False)

# ================================ step 2/3 模型 ================================
net = VGG19CA()
net.head= nn.Sequential(*[           
            nn.Flatten(start_dim=1, end_dim=-1),
            nn.Linear(512 * 7 * 7, 4096),
            nn.ReLU(inplace=True)
        ])     #丢弃原来结构的最后两个全连接层用来提取基于Attention的深层特征
net.load_state_dict(torch.load('./weight/VGG19_CA_7.pkl'),strict=False) #加载epoch=8时的权重参数
print(net)
if torch.cuda.is_available():
    net.cuda()

#============================ step 3/3 提取深层特征 ============================
for i,data in enumerate(train_loader):       #提取训练数据的深层特征存进NPY文件
    img,label=data
    img = Variable(img)
    if torch.cuda.is_available():
        img=img.cuda()
    out=net(img)
    a=np.append(a,out.data.cpu().numpy()) 
Train_deep_features=a.reshape(-1,4096)     #(n,4096)n为训练样本个数，4096为4096-dimensional
print(Train_deep_features.shape)
np.save('./Train_deep_futures' + '.npy', Train_deep_features)

for i,test_data in enumerate(test_loader):  #提取测试数据的深层特征存进NPY文件
    test_img,test_label=test_data
    test_img = Variable(test_img)
    if torch.cuda.is_available():
        test_img=test_img.cuda()
    # 前向传播
    test_out=net(test_img)
    b=np.append(b,test_out.data.cpu().numpy()) 
Test_deep_features=b.reshape(-1,4096)     #(m,4096)m为测试样本个数，4096为4096-dimensional
print(Test_deep_features.shape)
np.save('./Test_deep_futures' + '.npy', Test_deep_features)