import sys
sys.path.append('./data')
from sklearn import metrics
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from matplotlib import pyplot as plt
from dataset import M_Dataset
from torch.autograd import Variable
from sklearn.metrics import confusion_matrix
import seaborn as sn
from sklearn.metrics import precision_recall_curve,average_precision_score


# 创建一个类
class Detector(object):
    def __init__(self):
        super(Detector, self).__init__()
        self.classifier = nn.Sequential(*[
            nn.Linear(10436, 4096),
            nn.ReLU(inplace=True),
            nn.Linear(4096, 2)
            ])
        self.classifier.eval()
        if torch.cuda.is_available():
            self.classifier.cuda()

    def load_weights(self,weight_path):  #加载已训练好的模型权重
        self.classifier.load_state_dict(torch.load(weight_path))

    def roc(self,weight_path,dataset_path):                #ROC PR曲线绘制
        batchsize=1
        self.load_weights(weight_path=weight_path)
        test_data=M_Dataset(data_dir=dataset_path)  
        test_loader=DataLoader(dataset=test_data,batch_size=batchsize)   
        a,b=[],[]
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
            test_out=self.classifier(test_img)
            #b样本标签 a模型对样本属于正例的概率输出  ROC
            for j in range(batchsize):
                a=np.append(a,test_out.detach().cpu().numpy()[j][1])
            b=np.append(b,test_label.cpu().numpy())     
        precision, recall, thresholds = precision_recall_curve(b, a)
        aupr=average_precision_score(b, a)
        fpr, tpr, thresholds = metrics.roc_curve(b, a, pos_label=1)      
        auc = metrics.auc(fpr, tpr)

        plt.figure(1)   #画ROC曲线
        lw = 2
        plt.plot(fpr, tpr, color='darkorange',lw=lw, label='ROC curve (area = %0.4f)' % auc)
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlim([0.0, 1.0])
        plt.ylim([0.0, 1.05])
        plt.xlabel('False Positive Rate')
        plt.ylabel('True Positive Rate')
        plt.title('Receiver operating characteristic example')
        plt.legend(loc="lower right")
        plt.figure(2)    #画PR曲线
        plt.plot(recall, precision,  color='darkorange',lw = lw, label='PR curve (area = %0.4f)' % aupr)
        plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
        plt.xlabel('Recall')
        plt.ylabel('Precision')
        plt.title('Precision Recall Curve')
        plt.legend(loc="lower right")
        plt.show()

    def detect_dataset(self,weight_path,dataset_path):
        self.load_weights(weight_path=weight_path)
        test_data=M_Dataset(data_dir=dataset_path)
        test_loader=DataLoader(dataset=test_data,batch_size=1,shuffle=False)
        test_correct=0.
        test_total=0.
        predicted_list,label_list=[],[]
        a,b=[],[]
        for j,test_data in enumerate(test_loader):          
            test_img,test_label=test_data
            #print(valid_img.shape)
            test_img=test_img.to(torch.float32)
            test_img = Variable(test_img)
            test_label = Variable(test_label)     
            a=np.append(a,test_label.cpu().numpy())           #标签
            #print("原始标签：",valid_label)
            if torch.cuda.is_available():
                test_img=test_img.cuda()
                test_label=test_label.cuda()             
            if hasattr(torch.cuda, 'empty_cache'):
	            torch.cuda.empty_cache()
            test_out=self.classifier(test_img)    
            _, test_predicted = torch.max(test_out.data, 1)
            b=np.append(b,test_predicted.detach().cpu().numpy())       #模型预测
            #print("测试结果：",valid_predicted)
            test_total += test_label.size(0)
            test_correct += (test_predicted == test_label).sum()
            #混淆矩阵热力图
            predicted_list=np.append(predicted_list,test_predicted.cpu().numpy())
            label_list=np.append(label_list,test_label.cpu().numpy())

        print("*******************************************")
        print("测试集样本数量:",int(test_total))
        test_accurancy=test_correct / test_total
        print('模型识别准确率:%d %%' % (100*test_accurancy))

        sn.set(font_scale=1.5)  #画混淆矩阵热力图
        plt.figure(1)
        con=confusion_matrix(label_list,predicted_list)
        ax=sn.heatmap(con,annot=True,cmap='Oranges', fmt='g') 
        ax.set_xlabel('Predicted label')
        ax.set_ylabel('True label')
        plt.show()

if __name__=='__main__':
    detector=Detector()
    detector.detect_dataset('C:\\Users\Kristian\Desktop\Github\MED6_Anesthesia\python\library\MallampatiPaper\weight\VGG19_CA_7.pkl','C:\\Users\Kristian\Desktop\Github\MED6_Anesthesia\python\library\mallampati_datasets\\test_data')     #测试
    detector.roc('C:\\Users\Kristian\Desktop\Github\MED6_Anesthesia\python\library\MallampatiPaper\weight\VGG19_CA_7.pkl','C:\\Users\Kristian\Desktop\Github\MED6_Anesthesia\python\library\mallampati_datasets\\test_data')  #画ROC PR曲线