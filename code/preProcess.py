# -*- coding: utf-8 -*-

'''
图像预处理：
  获取图像的hog特征，并存储称 label value value value 形式的文件
'''

import struct
import numpy as np
from PIL import Image
from skimage import feature as ft

# 数据存储路径
path = '../img/svm/'


def read_labels(filename):
    f = open(filename, 'rb')
    index = 0
    buf = f.read()
    f.close()

    magic, items = struct.unpack_from('>II', buf, index)
    index += struct.calcsize('>II')

    result = {}

    for i in range(items):
        value = struct.unpack_from('B', buf, index)[0]
        index += struct.calcsize('B')
        result[i] = value

    return result


def process(labels):
    result = {}

    filenames = ['mnist/train-images.idx3-ubyte',
                 'mnist/t10k-images.idx3-ubyte']

    for key, filename in enumerate(filenames):
        key = str(key)
        result[key] = []

        f = open(path + filename, 'rb')
        buf = f.read()
        index = 0
        f.close()
        magic, numImages, numRows, numColumns = struct.unpack_from('>IIII', buf, index)
        index += struct.calcsize('>IIII')
        # 将每张图片按照格式存储到对应位置
        for image in range(numImages):
            temp = [labels[key][image]]

            im = struct.unpack_from('>784B', buf, index)
            index += struct.calcsize('>784B')
            # 这里注意 Image对象的dtype是uint8，需要转换
            im = np.array(im, dtype='uint8')
            im = im.reshape(28, 28)
            im = Image.fromarray(im)
            # hog特征获取
            hog = ft.hog(im,
                         orientations=9,
                         pixels_per_cell=(8, 8),
                         cells_per_block=(3, 3),
                         block_norm='L1')
            # 保存结果
            temp.extend(hog)
            result[key].append(temp)

    return result


def save(result):
    for key in result:
        if key == '0':
            filename = 'data/train.txt'
        else:
            filename = 'data/test.txt'
        f = open(path + filename, 'w')
        for item in result[key]:
            temp = ' '.join(map(lambda x: str(x), item))
            f.write(temp + '\n')
        f.close()


if __name__ == '__main__':
    labels = {}
    print('标签读取中...')
    labels['0'] = read_labels(path + 'mnist/train-labels.idx1-ubyte')
    labels['1'] = read_labels(path + 'mnist/t10k-labels.idx1-ubyte')
    print('图像HOG特征计算中...')
    result = process(labels)
    print('结果保存中...')
    save(result)
    print('数据预处理完成！')

# ft.hog(img, orientations=9,pixels_per_cell=(8,8),cells_per_block=(3,3))
