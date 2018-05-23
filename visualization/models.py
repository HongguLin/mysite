from django.db import models

from mongoengine import *
from mysite.settings import DBNAME
from pymongo import *

connect('patentvis', username='Honggu', password='548712580', host='@ds163779-a0.mlab.com', port=63779)

class Patent(DynamicDocument):
	meta = {'collection': 'patent', 'strict': False}
	Qkey = StringField(required=True)
	Qimportance = StringField(required=True)

class Qrel(DynamicDocument):
	meta = {'collection': 'qrel', 'strict': False}
	PAC = StringField(required=True)






