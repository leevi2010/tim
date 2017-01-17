# -*- coding: utf-8 -*- 

import urllib
import codecs
import jieba
from urllib import request
from sqlalchemy import Column, String, create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.types import INTEGER,BIGINT,FLOAT,VARCHAR,TEXT,DATETIME
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import func, or_, not_

#建立数据库连接
engine = create_engine('mysql+mysqlconnector://root:cced121504@localhost:3306/tim')# 初始化数据库连接:
DBSession = sessionmaker(bind=engine)# 创建DBSession类型
session = DBSession()# 创建session对象:
BaseModel = declarative_base()# 创建对象的基类:

#打开json文件准备转换

class Relation(BaseModel):
	__tablename__ = 'relation'
	id = Column(INTEGER, primary_key=True)
	body = Column(VARCHAR(20))
	extension = Column(VARCHAR(20))
	befor = Column(FLOAT,default=0.0)
	after = Column(FLOAT,default=0.0)

def listen(message):
	sts = list(jieba.cut(message))
	#逐个词看是否是已知的，如果是位
	readMessage(sts)
	#说出这句话相关的概念
	answer = set([])
	for seg in sts:
		query = session.query(Relation).filter(Relation.body == seg).order_by(Relation.befor+Relation.after).limit(3)
		session.commit()
		for ex in query:
			answer.add(ex.extension)
	print (answer)

def readMessage (sts):
	point = 0
	sentence = []
	flag = ['.',' ','。','《','》','！','!',':','"',':',"'",';',""]
	for __c in sts[point:]:
		if __c not in flag:
			sentence.append(__c)
		else:
			point += 1
			readSentence(sentence)
			del sentence[:] #开始新的句子
	readSentence(sentence)
			
def readSentence(s):
	for bo in s:
		#print ('正在学习：',bo)
		for ex in s:
			dis = s.index(ex) - s.index(bo)
			#如果外延词出现在本体词后方，则增加后方权重
			if dis > 0: 
				updateRelation(bo,ex,0.0,1/dis)
			#如果外延词出现在本体词前方，则增加前方权重
			elif dis < 0:
				updateRelation(bo,ex,abs(1/dis),0.0)			
		
def updateRelation(bo,ex,be,af):
	query = session.query(Relation).filter(Relation.body == bo,Relation.extension == ex)
	if query.first() == None:
		relation = Relation(body = bo,extension = ex,befor = be,after = af)
		session.add(relation)
		session.commit()
		#print(bo,ex)
	else:
		query.update({
			Relation.befor : Relation.befor + be
		})
		query.update({
			Relation.after : Relation.after + af
		})
		session.commit()
		
with open('input.txt','r',encoding='utf8') as book:
	listen(book.read())

