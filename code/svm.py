# -*- coding: utf-8 -*-

'''SVM作分类训练'''

from sklearn import svm
from sklearn.externals import joblib

path = '../img/svm/'


def getData(filename):
    X, y = [], []
    f = open(filename, 'r')
    for line in f.readlines():
        if line == '': continue
        items = line.split(' ')
        X.append(list(map(lambda x: float(x), items[1:])))
        y.append(int(items[0]))
    f.close()
    return X, y


# 开始训练
def train():
    print('读取数据...')
    X, y = getData(path + 'data/train.txt')
    clf = svm.LinearSVC()
    print('开始训练...')
    clf.fit(X, y)
    print('训练模型保存为 train_model.m')
    joblib.dump(clf, 'train_model.m')


def predict():
    X, y = getData(path + 'data/test.txt')
    clf = joblib.load('train_model.m')
    result = clf.predict(X)
    error = 0
    for k, v in enumerate(result):
        if v != y[k]: error += 1
    print('错误数：%s；错误率：%s' % (error, error / len(result)))


def start():
    chose = int(input('1：训练；2：预测：'))
    if chose == 1:
        train()
    elif chose == 2:
        predict()
    else:
        print('输入错误，程序退出')


if __name__ == '__main__':
    start()