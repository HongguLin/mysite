from django.db import models

from mongoengine import *
from mysite.settings import DBNAME
from pymongo import *

connect('ds161459.mlab.com:61459/patent -u Honggu -p 548712580')


class Patent(DynamicDocument):
	meta = {'collection': 'patent', 'strict': False}
	Qkey = StringField(required=True)
	Qimportance = StringField(required=True)
	#patent_document = EmbeddedDocumentField(Patent_document)

class Qrel(DynamicDocument):
	meta = {'collection': 'qrel', 'strict': False}
	PAC = StringField(required=True)






