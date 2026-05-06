import pandas as pd
import requests #请求网页数据
import random
import time
import os#提供通用的、基本的操作系统交互功能
import sys
import importlib
importlib.reload(sys)
import re


import jieba
import jieba.analyse
import os
import csv

#wordsByMyself=['灾害','地震','台风','海啸','旱涝','极端','恶劣','内涝','大风','沙尘','飓风','霜冻','水灾','风暴','泥石流','滑坡','凌冻','雪灾','旱灾','洪涝','暴雨','龙卷风','冰雹','洪灾','雨雪','冰冻','暴雪','冻害','干旱','旱情','强降雨','洪水','严寒','风沙','气候','天气','潮湿','水温','降温','寒冷','气温','降雨','温度','雨水','雨季','降水','阴雨','多雨','极寒','冬季','汛期','高湿','水情','水位','光照','缺水','高寒','寒潮','沉降','地下水','汛情','地表','蓄水']
wordsByMyself=['灾害','地震','台风','海啸','洪涝','旱涝','水灾','极端','暴雨','恶劣','内涝','大风','沙尘','冰雹','旱灾','飓风','霜冻','水灾','风暴','泥石流','滑坡',\
               '洪水','洪灾','干旱','暴雪','凌冻','雪灾','冰雪','气候','天气','自然','潮湿','水温','降温','寒冷','气温','降雨','温度','雨水','雨季','冰冻','早霜','低温','高温',\
               '雨雪','灾情','凝冻','水患','山洪','震灾','强震','风暴潮','天灾','倒春寒','冻雨','气候异常','少雨','强降雨','阴雨','大雪','反常','强降雨','暴风雪','干燥',\
               '缺水','淤积','空气污染','水质污染','雾霾','沙尘暴','冻害','虫灾','寒害','强风','自然灾害','大雾','雨天','冬季','严寒','炎热','高寒','冬天','大旱','晚霜','寒流',\
               '百年不遇','天旱','袭击','地理环境','天气状况','季节','风速','降水量','水位','夏季','盐度','湿度','含水量','水压','风沙','湿热','雨淋','雷击','冲毁','汛期',\
               '温湿度','相对湿度','冲刷','酷暑','光照','升温','过热','来水','水情','气象预报','水文','气象','咸潮','墒情','泥沙','积雪','水源','地下水','风潮','强热带',\
               '暖冬','热带风暴','暴风雨','厄尔尼诺']
#wordsByMyself=['节能','电能','能源','清洁','燃料','生态','节水','环境','绿色','转型','太阳能','升级','循环','改造','利用率','核电','风电','天然气','增效','燃油','效率','循环','再生',\
#              '高效','光伏','减排','降耗','光热','储能','新能源','资源化','废旧','再利用','废弃','排放','温室气体','污染治理','二氧化硫','环保治理','排污收费','排污','消耗',\
#              '回收率','能耗','损耗','燃气','煤层气','液化气','油气','清洁能源','煤炭','石油','光能','废热','零排放','技改','改建','扩能','效能','核能','火电','洁净',\
#              '节能环保','无污染','循环经济','燃煤','重油','柴油','蒸汽','烟煤','轻柴油','航油','燃料油','原油','汽油','大气质量','空气质量','能量','电网','电力','配电','化学能','环境友好',\
#              '环保型','煤化工','石油化工','石化','滴灌','节电','喷灌','环保','能效','节煤','提质增效','开源节流','风能','低耗']


csvf=open('C:/Users/王策建议/Desktop/企业物理风险研究复现材料/处理过程代码和日志文件/PhyClimt1.csv','w',encoding='utf-8',newline='')#请根据文件所在位置进行调整，下同
writer = csv.writer(csvf)
writer.writerow(('code', 'company', 'year', 'keyword', 'amt', 'word_sum'))

def word_by_myself():
    for i in range(len(wordsByMyself)):
        jieba.add_word(wordsByMyself[i])

#分词并进行词频统计
def cut_and_count(txt_path):
    with open(txt_path,encoding='utf-8') as f:
        text=f.read()
        words=jieba.lcut(text)

        stopwords={}.fromkeys([ line.rstrip() for line in open('stopwords.txt',encoding='utf-8') ])
        final= ""
        for word in words:
            if word not in stopwords:
                if (word !="。" and word != "，"):
                    final=final+" "+word

        all_words=[word for word in words if len(word)>1 and word not in stopwords]
       # print("总词数:",len(all_words))   #总词数计算


        counts={}
        for word in words:
            if len(word)==1:
                continue
            else:
                counts[word]=counts.get(word,0)+1
        for i in range(len(wordsByMyself)):
            if wordsByMyself[i] in counts:
                print(wordsByMyself[i]+':'+str(counts[wordsByMyself[i]]))
            else:
                print(wordsByMyself[i]+':0')
        return counts

file_list = os.listdir('D:/桌面载体/dealtxt1')#请根据TXT格式的企业年报文件所在位置进行调整
result={}
for f in file_list:
    file = 'D:/桌面载体/dealtxt1' + '/' + f #请根据TXT格式的企业年报文件所在位置进行调整
    text = open(file, encoding='utf-8').read()
    #cut_and_count(file)
    result.update(cut_and_count(file))
    word_sum=sum(result.values())
    print("总词数：", word_sum)
    for keyword in wordsByMyself:
        if keyword in result.keys():
            amt = result.get(keyword)
        else:
            amt = 0
        code = f.split("-")[0]  # 切片
        company = f.split("-")[1]
        year = f.split("-")[2][0:4]
        writer.writerow((code, company, year, keyword, amt, word_sum))
    result.clear()
csvf.close()