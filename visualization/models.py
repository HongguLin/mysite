from django.db import models

from mongoengine import *
from mysite.settings import DBNAME
from pymongo import *

connect('patent', username='Honggu', password='548712580', host='@ds161459.mlab.com:61459')



class Patent(DynamicDocument):
	meta = {'collection': 'patent', 'strict': False}
	Qkey = StringField(required=True)
	Qimportance = StringField(required=True)
	#patent_document = EmbeddedDocumentField(Patent_document)

class Qrel(DynamicDocument):
	meta = {'collection': 'qrel', 'strict': False}
	PAC = StringField(required=True)






