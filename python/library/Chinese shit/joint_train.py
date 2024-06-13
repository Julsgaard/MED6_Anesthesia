import sys
sys.path.append('./data')
import os
import random
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import torch.optim as optim
from dataset import M_Dataset
from torch.autograd import Variable


#宏定义一些数据，如epoch数，batchsize等
MAX_EPOCH=9
BATCH_SIZE=16
LR=0.00001
log_interval=3
val_interval=1

# ============================ step 1/5 数据 ============================
split_dir=os.path.join(".","data","Aug_mouth")
train_dir=os.path.join(split_dir,"Trian_all")   #Trian_all所有的训练数据
test_dir=os.path.join(split_dir,"test")   #测试数据

train_data=M_Dataset(data_dir=train_dir)
test_data=M_Dataset(data_dir=test_dir)
train_loader=DataLoader(dataset=train_data,batch_size=BATCH_SIZE,shuffle=False)
test_loader=DataLoader(dataset=test_data,batch_size=BATCH_SIZE)

# ============================ step 2/5 模型 ============================
classifier = nn.Sequential(*[
            nn.Linear(10436, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, 2)
            ])                      #分类器即VGG19_CA的最后两个全连接层
if torch.cuda.is_available():
    classifier.cuda()
# ============================ step 3/5 损失函数 ============================
criterion=nn.CrossEntropyLoss()
# ============================ step 4/5 优化器 ============================
optimizer=optim.Adam(classifier.parameters(),lr=LR,  weight_decay=0.001,betas=(0.9, 0.99))
# ============================ step 5/5 训练 ============================
classifier.train()

for epoch in range(MAX_EPOCH):
    correct=0.
    test_correct=0.
    total=0.
    test_total=0.
    train_loss = 0.0
    test_loss = 0.0
    for i,data in enumerate(train_loader):
        img,label=data
        img=img.to(torch.float32)   #torch.nn.Linear支持的是float32格式的数据
        img = Variable(img)
        label = Variable(label)
        if torch.cuda.is_available():
            img=img.cuda()
            label=label.cuda()
        out=classifier(img)       
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
        correct += (predicted == label).sum()
    print("============================================")
    accurancy=correct / total
    print('第%d个epoch的训练集识别准确率为：%d%%' % (epoch + 1, 100*accurancy))

    classifier.eval()
    for i,test_data in enumerate(test_loader):
        test_img,test_label=test_data
        test_img=test_img.to(torch.float32)
        test_img = Variable(test_img)
        test_label = Variable(test_label)
        if torch.cuda.is_available():
            test_img=test_img.cuda()
            test_label=test_label.cuda()      
        if hasattr(torch.cuda, 'empty_cache'):
	         torch.cuda.empty_cache()
        test_out=classifier(test_img)
        val_loss=criterion(test_out,test_label)#得到损失
        test_loss += float(val_loss.data.item())
        _, test_predicted = torch.max(test_out.data, 1)
        test_total += test_label.size(0)
        test_correct += (test_predicted == test_label).sum()
    print("*******************************************")
    #print(test_total)
    test_accurancy=test_correct / test_total
    print("测试集准确率为:",test_accurancy)

torch.save(classifier.state_dict(), "./weight/JHDM_%d.pkl"% epoch) #保留epoch=8时的模型权重JHDM_8.pkl

