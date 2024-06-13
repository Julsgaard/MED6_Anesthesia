import sys
sys.path.append('./data')
import os
import random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torchvision.transforms as transforms
import torch.optim as optim
from matplotlib import pyplot as plt
from dataset import MaDataset
from VGG19_CA import VGG19CA
import torchvision
from torch.autograd import Variable
from library.mallampati_image_prep import prepare_loader


#宏定义一些数据，如epoch数，batchsize等
MAX_EPOCH=8
BATCH_SIZE=16
LR=0.00001
log_interval=3
val_interval=1

# ============================ step 1/5 数据 ============================
split_dir=os.path.join(".","data","Aug_mouth")
train_dir='mallampati_datasets/training_data'   #所有训练数据Trian_all的80%
valid_dir='mallampati_datasets/validation_data'  #所有训练数据Trian_all的20%

#对训练集所需要做的预处理   
train_transform=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.485,0.456,0.406),(0.229,0.224,0.225))
])
#对验证集所需要做的预处理
valid_transform=transforms.Compose([
    transforms.ToTensor(),
    transforms.Normalize((0.485,0.456,0.406),(0.229,0.224,0.225))
])

# 构建MyDataset实例
#train_data=MaDataset(data_dir=train_dir,transform=train_transform)
#valid_data=MaDataset(data_dir=valid_dir,transform=valid_transform)

# 构建DataLoader
# 训练集数据最好打乱
# DataLoader的实质就是把数据集加上一个索引号，再返回
#train_loader=DataLoader(dataset=train_data,batch_size=BATCH_SIZE,shuffle=True)
#valid_loader=DataLoader(dataset=valid_data,batch_size=BATCH_SIZE)

train_loader = prepare_loader(path='C:\\Users\krill\Documents\Github\MED6_Anesthesia\python\library\mallampati_datasets\\training_data', image_pixel_size=224, normalization=True,
                              data_augmentation=True)
valid_loader = prepare_loader(path='C:\\Users\krill\Documents\Github\MED6_Anesthesia\python\library\mallampati_datasets\\validation_data', image_pixel_size=224, normalization=True)

# ============================ step 2/5 模型 ==============================
net = VGG19CA()    #添加了CA attention模块的VGG19
#print(net)
#将在ImageNet上预训练好的VGG19的参数加载到我们的模型上
net.load_state_dict(torch.load('C:/Users/krill/.cache/torch/hub/checkpoints/vgg19-dcbb9e9d.pth'),strict=False)
if torch.cuda.is_available():
    net.cuda()

# ============================ step 3/5 损失函数 ============================
criterion=nn.CrossEntropyLoss()
# ============================ step 4/5 优化器 ============================
optimizer=optim.Adam(net.parameters(),lr=LR,  weight_decay=0.001,betas=(0.9, 0.99))
# ============================ step 5/5 训练 ============================
# 记录每一次的数据，方便绘图
net.train()
T_loss_curve=list()
V_loss_curve=list()
T_acc_curve=list()
V_acc_curve=list()
for epoch in range(MAX_EPOCH):
    loss_mean=0.
    correct=0.
    valid_correct=0.
    total=0.
    valid_total=0.
    train_loss = 0.0
    valid_loss = 0.0

    for i,data in enumerate(train_loader):
        img,label=data
        img = Variable(img)
        label = Variable(label)
        if torch.cuda.is_available():
            img=img.cuda()
            label=label.cuda()
        # 前向传播
        out=net(img)       
        optimizer.zero_grad()  # 归0梯度
        loss=criterion(out,label)#得到损失函数
        print_loss=loss.data.item()
        loss.backward()#反向传播
        optimizer.step()#优化
        train_loss += float(loss.data.item())
        if (i+1)%log_interval==0:
            print('epoch:{},loss:{:.4f}'.format(epoch+1,loss.data.item()))
        _, predicted = torch.max(out.data, 1)
        total += label.size(0)
        # print("============================================")
        # print("源数据标签：",label)
        # print("============================================")
        # print("预测结果：",predicted)
        # print("相等的结果为：",predicted == label)
        correct += (predicted == label).sum()
    print("============================================")
    loss_mean=train_loss/len(train_loader)
    T_loss_curve.append(loss_mean)
    accurancy=correct / total
    T_acc_curve.append(accurancy.data.cpu().numpy())
    print('The recognition accuracy of the training set for epoch %d is: %d%%' % (epoch + 1, 100 * accurancy))

    #模型评估
    net.eval()
    for i,valid_data in enumerate(valid_loader):
        valid_img,valid_label=valid_data
        valid_img = Variable(valid_img)
        valid_label = Variable(valid_label)
        if torch.cuda.is_available():
            valid_img=valid_img.cuda()
            valid_label=valid_label.cuda()
        if hasattr(torch.cuda, 'empty_cache'):
	         torch.cuda.empty_cache()
        valid_out=net(valid_img)        # 前向传
        val_loss=criterion(valid_out,valid_label)#得到损失
        valid_loss += float(val_loss.data.item())
        _, valid_predicted = torch.max(valid_out.data, 1)
        valid_total += valid_label.size(0)
        valid_correct += (valid_predicted == valid_label).sum()
    print("********************************************")
    print(valid_total)
    valid_accurancy=valid_correct / valid_total
    V_acc_curve.append(valid_accurancy.data.cpu().numpy())
    V_loss_mean=valid_loss/len(valid_loader)
    V_loss_curve.append(V_loss_mean)
    print("The validation set accuracy is:", valid_accurancy)

    torch.save(net.state_dict(), "./weight/VGG19_CA_%d.pkl"% epoch)   #保存每一次epoch的模型权重

# ============================ 画图 ============================
#我这里迭代了50次，所以x的取值范围为(0，50)，然后再将每次相对应的准确率以及损失率附在x上
x1 = range(0,8)
y1 = T_loss_curve
y2 = T_acc_curve
y3 = V_acc_curve
y4 = V_loss_curve

#准确率损失变化曲线
plt.figure(1)
plt.subplot(2, 1, 1)
plt.plot(x1, y1, '.-',color='royalblue',label="Train_Loss")
plt.plot(x1, y4, '.-',color='darkorange',label="Valid_Loss")
plt.title('Loss vs. epoches')
plt.ylabel('Loss')

plt.subplot(2, 1, 2)
plt.plot(x1, y2, '.-',color='royalblue',label="Train_Accuracy")
plt.plot(x1, y3, '.-',color='darkorange',label="Valid_Accuracy")
plt.xlabel('accuracy vs. epoches')
plt.ylabel('accuracy')
plt.show()