# -*- coding: utf-8 -*-
import numpy as np
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import scipy.signal as signal
import skimage.morphology as sm
from skimage import feature as ft
from sklearn.externals import joblib

'''数据聚合'''
def aggregat(arr):
    tmp = np.sort(arr)
    # print('before', len(tmp), tmp)
    ptr, result, helper = 0, [], [tmp[0]]
    for i in range(1, len(tmp)):
        if i == ptr: continue
        if tmp[i] - tmp[ptr] < 10: # 阈值为10
            helper.append(tmp[i])
        else:
            if len(helper) == 1:
                result.append(helper[0])
            else:
                result.append(int(np.mean(helper)))
            helper, ptr = [tmp[i]], i
    result.append(int(np.mean(helper)))
    # print('after', len(result), result)
    return result


'''生成高斯算子的函数'''
def func(x,y,sigma=1):
    return 100*(1/(2*np.pi*sigma))*np.exp(-((x-2)**2+(y-2)**2)/(2.0*sigma**2))


'''获取图像的边缘'''
def getImgBorder(filename):
    # 生成标准差为5的5*5高斯算子
    suanzi1 = np.fromfunction(func,(5,5),sigma=5)
    # Laplace扩展算子
    suanzi2 = np.array([[1, 1, 1],
                        [1,-8, 1],
                        [1, 1, 1]])
    # 打开图像并转化成灰度图像
    image = Image.open(filename).convert("L")
    image_array = np.array(Image.open(filename).convert("L"))
    # 利用生成的高斯算子与原图像进行卷积对图像进行平滑处理
    image_blur = signal.convolve2d(image_array, suanzi1, mode="same")
    # 膨胀操作，进一步去除噪声
    image_blur = sm.dilation(image_blur, sm.square(5))
    # 对平滑后的图像进行边缘检测
    image2 = signal.convolve2d(image_blur, suanzi2, mode="same")
    # 结果转化到0-255
    image2 = (image2/float(image2.max()))*255
    # 将大于灰度平均值的灰度值变成255（白色），便于观察边缘
    image2[image2>image2.mean()] = 255
    image2[image2<=image2.mean()] = 0
    # 原图颜色反转
    for i in range(image_array.shape[0]):
        for j in range(image_array.shape[1]):
            if image_array[i][j] < 160:
                image_array[i][j] = 255
            else:
                image_array[i][j] = 0
    image_array = sm.dilation(image_array, sm.square(3))
    # plt.imshow(image_array, cmap=cm.gray)
    # plt.show()
    # plt.imshow(image2, cmap=cm.gray)
    # plt.show()
    return Image.fromarray(image_array), image2
    # return image, image2


'''提取Y方向的切割边缘'''
def cutY(img):
    result = []
    flag = False
    H, W = img.shape
    for h in range(10, H - 12):
        imgTmp = img[h:h+2, 10:W-10]
        tmp = imgTmp[imgTmp > 125]
        prob = tmp.shape[0] / (imgTmp.shape[0] * imgTmp.shape[1])
        if flag is False and prob < 0.99:
            result.append(h)
            flag = True
        elif flag is True and prob == 1:
            result.append(h + 2)
            flag = False
    return aggregat(result)
    # return result


'''提取X方向的切割边缘'''
def cutX(img, Y):
    final = []
    H, W = img.shape
    h = 0
    while True:
        if h == len(Y): break
        result = []
        flag = False
        for w in range(10, W - 12):
            imgTmp = img[Y[h] - 1:Y[h+1] + 1, w:w+2]
            tmp = imgTmp[imgTmp > 125]
            prob = tmp.shape[0] / (imgTmp.shape[0] * imgTmp.shape[1])
            if flag is False and prob < 0.99:
                result.append(w - 1)
                flag = True
            elif flag is True and prob == 1:
                result.append(w + 2)
                flag = False
        h += 2
        final.append(aggregat(result))
    return final


'''获取矩形的四个顶点，顶点按 左上-右上-左下-右下 顺序存储'''
def getPoints(X, Y):
    points = []
    h = 0
    while True:
        if h == len(Y): break
        tmp, w = [], 0
        while True:
            ptr = int(h / 2)
            if w == len(X[ptr]): break
            # 按 左上-右上-左下-右下 顺序存储
            tmp.append([[X[ptr][w], Y[h]],
                        [X[ptr][w + 1], Y[h]],
                        [X[ptr][w], Y[h + 1]],
                        [X[ptr][w + 1], Y[h + 1]]])
            w += 2
        points.append(tmp)
        h += 2
    return points


'''对每个字符进行精确定框'''
def cellCut(img):
    result = []
    flag = False
    H, W = img.shape
    for h in range(H):
        imgTmp = img[h]
        tmp = imgTmp[imgTmp < 125]
        # print(tmp)
        # print(imgTmp)
        prob = tmp.shape[0] / imgTmp.shape[0]
        if prob != 1 and flag is False:
            result.append(h)
            flag = True
        elif prob == 1 and flag is True:
            result.append(h)
            flag = False
    # print(result)
    return result


'''图像切割'''
def imgCut(img, points):
    images = []
    for raw in points:
        tmp = []
        for col in raw:
            # (left, upper, right, lower)
            box = (col[0][0], col[0][1], col[1][0], col[2][1])
            # 图像切割
            image = img.crop(box)
            # 进一步精化处理
            smallY = cellCut(np.array(image))
            gap = col[2][1] - col[0][1]
            if len(smallY) == 1:
                if smallY[0] > gap / 2:
                    col[2][1] -= gap - smallY[0]
                    col[3][1] -= gap - smallY[0]
                else:
                    col[0][1] += smallY[0]
                    col[1][1] += smallY[0]
            else:
                col[0][1] += smallY[0]
                col[1][1] += smallY[0]
                col[2][1] -= gap - smallY[1]
                col[3][1] -= gap - smallY[1]
            box = (col[0][0], col[0][1], col[1][0], col[2][1])
            image = img.crop(box).resize((28, 24))
            imgHelp = Image.new('L', (28, 28), 0)
            imgHelp.paste(image, (0, 2))
            # plt.imshow(imgHelp, cmap=cm.gray)
            # plt.show()
            tmp.append(imgHelp)
        images.append(tmp)
    return images


'''提取hog特征'''
def getHog(img):
    return ft.hog(img,
                  orientations=9,
                  pixels_per_cell=(8, 8),
                  cells_per_block=(3, 3),
                  block_norm='L1')


'''显示切割边缘图'''
def showBorder():
    img1, img2 = getImgBorder('../img/testData/target_2.png')
    Y = cutY(img2)
    X = cutX(img2, Y)

    points = getPoints(X, Y)

    # 显示图像
    plt.imshow(img1, cmap=cm.gray)
    for raw in points:
        for col in raw:
            box = (col[0][0], col[0][1], col[1][0], col[2][1])
            smallImg = img1.crop(box)
            smallY = cellCut(np.array(smallImg))
            gap = col[2][1] - col[0][1]
            if len(smallY) == 1:
                if smallY[0] > gap / 2:
                    col[2][1] -= gap - smallY[0]
                    col[3][1] -= gap - smallY[0]
                else:
                    col[0][1] += smallY[0]
                    col[1][1] += smallY[0]
            else:
                col[0][1] += smallY[0]
                col[1][1] += smallY[0]
                col[2][1] -= gap - smallY[1]
                col[3][1] -= gap - smallY[1]

            plt.plot([col[0][0], col[1][0]], [col[0][1], col[1][1]], 'r-')
            plt.plot([col[0][0], col[2][0]], [col[0][1], col[2][1]], 'r-')
            plt.plot([col[3][0], col[1][0]], [col[3][1], col[1][1]], 'r-')
            plt.plot([col[3][0], col[2][0]], [col[3][1], col[2][1]], 'r-')
    plt.show()


'''开始图像数字识别'''
def start():
    img1, img2 = getImgBorder('../img/testData/target_2.png')
    Y = cutY(img2)
    X = cutX(img2, Y)

    points = getPoints(X, Y)
    images = imgCut(img1, points)
    # 载入 svm 训练模型
    clf = joblib.load('train_model.m')
    result = []
    for raw in images:
        tmp = ''
        for image in raw:
            value = clf.predict(getHog(image))
            tmp += str(value[0])
            print('预测值：', value[0])
            plt.imshow(image, cmap=cm.gray)
            plt.title(u'预测值：' + str(value[0]))
            plt.show()
        result.append(tmp)
    print('识别值为', result)


if __name__ == '__main__':
    showBorder()
    start()
    