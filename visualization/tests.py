from django.test import TestCase

from django.db import models

from mongoengine import *

from pymongo import *

from mongoengine.base.datastructures import BaseList, BaseDict

from nltk.tokenize import word_tokenize
from nltk.tokenize import RegexpTokenizer
from nltk.stem import PorterStemmer
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

connect('patent')


class Patent(DynamicDocument):
	meta = {'collection': 'patent', 'strict': False}
	Qkey = StringField(required=True)
	Qimportance = StringField(required=True)
	#patent_document = EmbeddedDocumentField(Patent_document)

class Qrel(DynamicDocument):
	meta = {'collection': 'qrel', 'strict': False}
	PAC = StringField(required=True)

def get_content(content):
	description = ""
	if isinstance(content, str):
		description += content
	elif isinstance(content, BaseList) or isinstance(content, list):
		for c in content:
			if isinstance(c,str):
				description += c
	else:
		print("bad format!")
	return description

def get_dict_abs(abs_dict):
	abstract = ""
	if "p" in abs_dict:
		if isinstance(abs_dict["p"], str):
			abstract = abs_dict["p"]
		elif isinstance(abs_dict["p"], BaseDict) and "content" in abs_dict["p"]:
			abstract += get_content(abs_dict["p"]["content"])
		elif isinstance(abs_dict["p"], BaseList) or isinstance(abs_dict["p"], list):
			#print(patent.patent_document["ucid"])
			for x in abs_dict["p"]:
				if isinstance(x, str):
					abstract += x
				elif isinstance(x, BaseDict) and "content" in x:
					abstract += get_content(x["content"])
				else:
					print("bad format!")
		else:
			print("bad format!")
	else:
		print("bad format!")
	return abstract



# Create your tests here.
def p2str(patent):
	description = ""
	abstract = ""

	if "description" in patent.patent_document:
		if patent.patent_document["description"]["lang"]=="EN":
			description_list = patent.patent_document["description"]["p"]

			if isinstance(description_list, BaseList):
				for des in description_list:
					if isinstance(des, str):
						description += des
					elif "content" in des:
						x = get_content(des["content"])
						if x != "":
							description += x
						else:
							print("bad format!")
							return patent.patent_document["ucid"]


			elif isinstance(description_list, BaseDict):
				if "pre" in description_list:
					if "content" in description_list["pre"]:
						x = get_content(description_list["pre"]["content"])
						if x != "":
							description += x
						else:
							print("bad format!")
							return patent.patent_document["ucid"]

				elif "content" in description_list:
					x = get_content(description_list["content"])
					if x != "":
						description += x
					else:
						print("bad format!")
						return patent.patent_document["ucid"]

				else:
					print("bad format!")
					return patent.patent_document["ucid"]

			elif isinstance(description_list, str):
				description += description_list
			else:
				print("bad format!")
				return patent.patent_document["ucid"]

	if "abstract" in patent.patent_document:
		if isinstance(patent.patent_document["abstract"], BaseList) or isinstance(patent.patent_document["abstract"], list):
			for x in patent.patent_document["abstract"]:
				if x["lang"]=="EN":
					y = get_dict_abs(x)
					if y != "":
						abstract += y
					else:
						print("bad format!")
						return patent.patent_document["ucid"]

		elif isinstance(patent.patent_document["abstract"], BaseDict):
			if patent.patent_document["abstract"]["lang"]=="EN":
				y = get_dict_abs(patent.patent_document["abstract"])
				if y != "":
					abstract += y
				else:
					print("bad format!")
					return patent.patent_document["ucid"]
		else:
			print("bad format!")
			return patent.patent_document["ucid"]
		
	#my_dict = {"description": description, "abstract": abstract}
	return "good"

bad_list = []
patents = Qrel.objects()
for p in patents:
	x = p2str(p)
	if x != "good":
		bad_list.append(x)

print(len(bad_list))
print(bad_list)



