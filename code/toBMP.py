# -*- coding: utf-8 -*-

'''将mnist的图像存储为bmp格式'''

import struct
import numpy as np
import  matplotlib.pyplot as plt
from PIL import Image

path = '../img/svm/'
filenames = [ 'mnist/train-images.idx3-ubyte',
              'mnist/t10k-images.idx3-ubyte' ]
savenames = [ 'train/%s.bmp',
             'test/%s.bmp' ]

for key, filename in enumerate(filenames):
  #二进制的形式读入
  filename = path + filename
  binfile=open(filename,'rb')
  buf=binfile.read()
  index=0
  magic,numImages,numRows,numColumns=struct.unpack_from('>IIII',buf,index)
  index+=struct.calcsize('>IIII')
  #将每张图片按照格式存储到对应位置
  for image in range(0,numImages):
      im=struct.unpack_from('>784B',buf,index)
      index+=struct.calcsize('>784B')
     #这里注意 Image对象的dtype是uint8，需要转换
      im=np.array(im,dtype='uint8')
      im=im.reshape(28,28)
      im=Image.fromarray(im)
      savePath = path + savenames[key]
      im.save( savePath % image,'bmp')