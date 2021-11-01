# prediction file
from numpy import *
import pickle
import csv
import jieba


with open('stopwords_dict.pkl', 'rb') as tf:
    stopwords_dict = pickle.load(tf)


def jieba_text(text, way=False):
    """
    sample formatting
    :param text: the original input sentence
    :param way: jieba cut model
    :return:
    """
    text_jieba = jieba.cut(text, way)
    text_str = []
    for word in text_jieba:
        if word not in stopwords_dict:
            text_str.append(word)
    return text_str


def setOfWords2Vec(vocabList, inputSet):
    """
    文本词向量。词库中每一个词看成一个特征，文本中就该词，该词特征就是1，没有就是0
    :param vocabList:
    :param inputSet:
    :return:
    """
    returnVec = [0] * len(vocabList)
    for word in inputSet:
        if word in vocabList:
            returnVec[vocabList.index(word)] = 1
    return returnVec


def trainNB0(trainMatrix, trainCategory):
    numTrainDocs = len(trainMatrix)
    numWords = len(trainMatrix[0])
    pAbusive = sum(trainCategory) / float(numTrainDocs)
    p0Num = ones(numWords) #防止某个类别计算出的几率为0，致使最后相乘都为0，因此初始词都赋值1，分母赋值为2.
    p1Num = ones(numWords)
    p0Denom = 2
    p1Denom = 2
    for i in range(numTrainDocs):
        if trainCategory[i] == 1:
            p1Num += trainMatrix[i]
            p1Denom += sum(trainMatrix[i])
        else:
            p0Num += trainMatrix[i]
            p0Denom += sum(trainMatrix[i])
    p1Vect = log(p1Num / p1Denom)  #这里使用了Log函数，方便计算，由于最后是比较大小，全部对结果没有影响。
    p0Vect = log(p0Num / p0Denom)
    return p0Vect, p1Vect, pAbusive


def classifyNB(vec2Classify,p0Vec,p1Vec,pClass1): #比较几率大小进行判断，
    p1 = sum(vec2Classify*p1Vec)+log(pClass1)
    p0 = sum(vec2Classify*p0Vec)+log(1-pClass1)
    if p1>p0:
        return 1
    else:
        return 0


def load_data(files, column):
    """
    load the training data
    :param files:
    :param column:
    :return:
    """
    train_data = []
    train_label = []
    for file_read in files:
        with open(f"datasets/"+file_read, 'r', encoding='gbk') as f:
            train = csv.reader(f)
            header = next(train)
            for words in train:
                train_data.append(jieba_text(words[0]))
                train_label.append(int(words[column]))
    return train_data, train_label


def createVocabList(dataSet):
    """
    建立词库 这里就是直接把全部词去重后，看成词库
    :param dataSet:
    :return:
    """
    vocabSet = set([])
    for document in dataSet:
        vocabSet = vocabSet | set(document)
    return list(vocabSet)


def train_model(files, column):
    listOPosts, listClasses = load_data(files,column)
    myVocabList = createVocabList(listOPosts)
    trainMat = []
    for postinDoc in listOPosts:
        trainMat.append(setOfWords2Vec(myVocabList, postinDoc))
    p1V, p0V, pAb = trainNB0(array(trainMat), array(listClasses))
    return [myVocabList, p1V, p0V, pAb]


files = ['training_0.csv', 'training_1.csv']
column = 1
model = train_model(files, column)

files = ['training_1.csv']
column = 2
model2 = train_model(files, column)
