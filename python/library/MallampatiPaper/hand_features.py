import sys
sys.path.append('./data')
import matplotlib.pyplot as plt
import cv2 as cv
from skimage import data
import numpy as np
import os

# ==================================HOG特征======================================
#灰度图像gamma校正
def gamma(img):
    #不同参数下的gamma校正
    # img1 = img.copy()
    # img2 = img.copy()
    # img1 = np.power( img1 / 255.0, 0.5 )
    # img2 = np.power( img2 / 255.0, 2.2 )
    return np.power( img / 255.0, 1 )    

#获取梯度值cell图像，梯度方向cell图像
def div( img, cell_x, cell_y, cell_w ):
    cell = np.zeros( shape = ( cell_x, cell_y, cell_w, cell_w ) )
    img_x = np.split( img, cell_x, axis = 0 )
    for i in range( cell_x ):
        img_y = np.split( img_x[i], cell_y, axis = 1 )
        for j in range( cell_y ):
            cell[i][j] = img_y [j]
    return cell

#获取梯度方向直方图图像，每个像素点有9个值
def get_bins( grad_cell, ang_cell ):
    bins = np.zeros( shape = ( grad_cell.shape[0], grad_cell.shape[1], 9 ) )
    for i in range( grad_cell.shape[0] ):
        for j in range( grad_cell.shape[1] ):
            binn = np.zeros(9)
            grad_list = np.int8( grad_cell[i,j].flatten() )#每个cell中的64个梯度值展平，并转为整数
            ang_list = ang_cell[i,j].flatten()#每个cell中的64个梯度方向展平)
            ang_list = np.int8( ang_list / 20.0 )#0-9
            ang_list[ ang_list >=9 ] = 0
            for m in range(len(ang_list)):
                binn[ang_list[m]] += int( grad_list[m] )#不同角度对应的梯度值相加，为直方图的幅值
            bins[i][j] = binn
    return bins

#计算图像HOG特征向量，长度为 36*13*13 = 6084   
def hog( img, cell_x, cell_y, cell_w ):
    height, width = img.shape
    gradient_values_x = cv.Sobel( img, cv.CV_64F, 1, 0, ksize = 5 )#x方向梯度
    gradient_values_y = cv.Sobel( img, cv.CV_64F, 0, 1, ksize = 5 )#y方向梯度
    gradient_magnitude = np.sqrt( np.power( gradient_values_x, 2 ) + np.power( gradient_values_y, 2 ) )
    gradient_angle = np.arctan2( gradient_values_x, gradient_values_y )
    gradient_angle[ gradient_angle > 0 ] *= 180 / 3.14
    gradient_angle[ gradient_angle < 0 ] = ( gradient_angle[ gradient_angle < 0 ] + 3.14 ) *180 / 3.14

    grad_cell = div( gradient_magnitude, cell_x, cell_y, cell_w )
    ang_cell = div( gradient_angle, cell_x, cell_y, cell_w )
    bins = get_bins ( grad_cell, ang_cell )
    feature = []
    for i in range( cell_x - 1 ):
        for j in range( cell_y - 1 ):
            tmp = []
            tmp.append( bins[i,j] )
            tmp.append( bins[i+1,j] )
            tmp.append( bins[i,j+1] )
            tmp.append( bins[i+1,j+1] )
            tmp -= np.mean( tmp )
            feature.append( tmp.flatten() )
    return np.array( feature ).flatten()
                
def HOG_feature(img_path):
    img = cv.imread( img_path, cv.IMREAD_GRAYSCALE )
    resizeimg = cv.resize( img, ( 224, 224 ), interpolation = cv.INTER_CUBIC )
    cell_w = 16
    cell_x = int( resizeimg.shape[0] / cell_w )#cell行数
    cell_y = int( resizeimg.shape[1] / cell_w )#cell列数
    gammaimg = gamma( resizeimg )*255    
    feature = hog( gammaimg, cell_x, cell_y, cell_w )
    feature = cv.normalize(feature,feature)
    return feature 


# ========================================LBP特征=========================================
def lbp_basic(img):
    basic_array = np.zeros(img.shape,np.uint8)
    for i in range(basic_array.shape[0]-1):
        for j in range(basic_array.shape[1]-1):
            basic_array[i,j] = bin_to_decimal(cal_basic_lbp(img,i,j))
    return basic_array

def cal_basic_lbp(img,i,j):#比中心像素大的点赋值为1，比中心像素小的赋值为0，返回得到的二进制序列
    sum = []
    if img[i - 1, j ] > img[i, j]:
        sum.append(1)
    else:
        sum.append(0)
    if img[i - 1, j+1 ] > img[i, j]:
        sum.append(1)
    else:
        sum.append(0)
    if img[i , j + 1] > img[i, j]:
        sum.append(1)
    else:
        sum.append(0)
    if img[i + 1, j+1 ] > img[i, j]:
        sum.append(1)
    else:
        sum.append(0)
    if img[i + 1, j ] > img[i, j]:
        sum.append(1)
    else:
        sum.append(0)
    if img[i + 1, j - 1] > img[i, j]:
        sum.append(1)
    else:
        sum.append(0)
    if img[i , j - 1] > img[i, j]:
        sum.append(1)
    else:
        sum.append(0)
    if img[i - 1, j - 1] > img[i, j]:
        sum.append(1)
    else:
        sum.append(0)
    return sum

def bin_to_decimal(bin):#二进制转十进制
    res = 0
    bit_num = 0 #左移位数
    for i in bin[::-1]:
        res += i << bit_num   # 左移n位相当于乘以2的n次方
        bit_num += 1
    return res

def show_basic_hist(a): #LBP特征向量，长度为256    
    hist = cv.calcHist([a],[0],None,[256],[0,256])
    hist = cv.normalize(hist,hist)
    hist =hist.reshape(1,256)
    return hist

def LBP_feature(img_path):
    img = cv.imread(img_path)
    img1 = cv.cvtColor(img,cv.COLOR_BGR2GRAY)
    basic_array = lbp_basic(img1)
    feature=show_basic_hist(basic_array)
    return feature


# ==================================提取训练和测试数据的LBP HOG特征并保存=====================================
if __name__ == '__main__':
    split_dir=os.path.join(".","data","Aug_mouth")
    train_dir=os.path.join(split_dir,"Train_all")
    test_dir=os.path.join(split_dir,"test")  
    
    LBP,HOG,Lab=[],[],[]
    for root, dirs, _ in os.walk(train_dir): #提取训练数据的LBP HOG特征并保存进npy文件
            for sub_dir in dirs:        
                img_names = os.listdir(os.path.join(root, sub_dir))
                img_names = list(filter(lambda x: x.endswith('.jpg'), img_names))  
                for i in range(len(img_names)):
                    img_name = img_names[i]
                    img_path = os.path.join(root, sub_dir, img_name)
                    label = sub_dir
                    Lab=np.append(Lab,label)
                    L=LBP_feature(img_path)
                    LBP=np.append(LBP,L)
                    H=HOG_feature(img_path)
                    HOG=np.append(HOG,H)
    LBP=LBP.reshape(-1,256)   #(n,256)n为训练样本个数，256为LBP特征向量的长度
    HOG=HOG.reshape(-1,6084)  #(n,6084)n为训练样本个数，6084为HOG特征向量的长度
    print(LBP.shape,HOG.shape)
    np.save('./Train_LBP_futures' + '.npy', LBP)
    np.save('./Train_HOG_futures' + '.npy', HOG)
    np.save('./Train_Label' + '.npy', Lab)  #标签 


    LBP,HOG,Lab=[],[],[]
    for root, dirs, _ in os.walk(test_dir):   #提取测试数据的LBP HOG特征并保存进npy文件
            for sub_dir in dirs:           
                img_names = os.listdir(os.path.join(root, sub_dir))
                img_names = list(filter(lambda x: x.endswith('.jpg'), img_names))      
                for i in range(len(img_names)):
                    img_name = img_names[i]
                    img_path = os.path.join(root, sub_dir, img_name)
                    label = sub_dir
                    Lab=np.append(Lab,label)
                    L=LBP_feature(img_path)
                    LBP=np.append(LBP,L)
                    H=HOG_feature(img_path)
                    HOG=np.append(HOG,H)
    LBP=LBP.reshape(-1,256)
    HOG=HOG.reshape(-1,6084)
    print(LBP.shape,HOG.shape)
    np.save('./Test_LBP_futures' + '.npy', LBP)
    np.save('./Test_HOG_futures' + '.npy', HOG)
    np.save('./Test_Label' + '.npy', Lab)