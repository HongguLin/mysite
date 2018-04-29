from django.shortcuts import render
from django.template import RequestContext
from .models import Patent, Qrel

from django.http import HttpResponse

from mongoengine.base.datastructures import BaseList, BaseDict

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer
from nltk.corpus import stopwords

import json

import datetime

class Common:
	def __init__(self, UCID, common_abstract, common_description, r1, r2, r3):
		self.UCID = UCID
		self.common_abstract = common_abstract
		self.common_description = common_description
		self.r1 = r1
		self.r2 = r2
		self.r3 = r3
		
	def displayCommon(self):
		print("UCID:", self.UCID, " common_ipcr_level1:", self.r1, " common_ipcr_level2:", self.r2, " common_ipcr_level3:", self.r3, " common_abstract:", self.common_abstract, " common_description:", self.common_description)

def index(request):
	if request.method == 'POST':
		qkey = request.POST['Qkey']
		try:
			patents = Patent.objects(Qkey = request.POST.get('Qkey'))
			qrel = Qrel.objects(PAC = request.POST.get('Qkey'))[0]
			slist = get_patents_section(patents)
			return render(request, 'd3view.html', {'Patents': patents, 'Qrel':qrel, 'SecList':slist})
		except IndexError:
			return HttpResponse("no such item for Cursor instance!", content_type='text/plain')	

	if request.method == 'GET':
		return render(request, "index.html")

def doc_view(request):	
	id = eval("request." + request.method + "['ucid']")
	patent = Patent.objects(patent_document__ucid=id)[0]
	pac = patent.Qkey
	qrel = Qrel.objects(PAC = pac)[0]
	common = get_common(qrel, patent)
	return render(request, 'doc_view.html', {'Common': common, 'Patent':patent.patent_document, 'Qrel':qrel.patent_document, 'PAC':pac})


def patent_file(request):
	id = eval("request." + request.method + "['ucid']")
	patent = Patent.objects(patent_document__ucid=id)[0]
	return render(request, 'patentfile.html', {'Patent':patent.patent_document})



# IPC Vector:
## Section  Class  Subclass      Maingroup / Subgroup
##   1        2       1            1 or 2    1 or 2

### Level 1: Section + Class + Subclass
### Level 2: Section + Class + Subclass + Maingroup
### Level 3: Section + Class + Subclass + Maingroup + Subgroup

def get_patents_section(patents):
	slist = []
	for patent in patents:
		p_ipcr_list = patent.patent_document["bibliographic_data"]["technical_data"]["classifications_ipcr"]["classification_ipcr"]
		for j in p_ipcr_list:
			x = j["content"][0]
			if x not in slist:
				slist.append(x[0])
	return slist



def get_common_ipcr(qrel, patent):
	ipcr_list = qrel.patent_document["bibliographic_data"]["technical_data"]["classifications_ipcr"]["classification_ipcr"]
	c_list_1 = []
	c_list_2 = []
	c_list_3 = []
	for i in ipcr_list:
		x = i["content"].split()
		x1 = x[1].split("/")

		if x[0] not in c_list_1:
			c_list_1.append(x[0])
		if x[0]+x1[0] not in c_list_2:
			c_list_2.append(x[0]+x1[0])
		if x[0]+x[1] not in c_list_3:
			c_list_3.append(x[0]+x[1])	

	p_ipcr_list = patent.patent_document["bibliographic_data"]["technical_data"]["classifications_ipcr"]["classification_ipcr"]
	p_c_list_1 = []
	p_c_list_2 = []
	p_c_list_3 = []
	for j in p_ipcr_list:
		x = j["content"].split()
		x1 = x[1].split("/")

		if x[0] not in p_c_list_1:
			p_c_list_1.append(x[0])
		if x[0]+x1[0] not in p_c_list_2:
			p_c_list_2.append(x[0]+x1[0])
		if x[0]+x[1] not in p_c_list_3:
			p_c_list_3.append(x[0]+x[1])

	relate3 = list(set(c_list_3).intersection(set(p_c_list_3)))
	relate2 = list(set(c_list_2).intersection(set(p_c_list_2)))
	relate1 = list(set(c_list_1).intersection(set(p_c_list_1)))

	relate = {"r1":relate1, "r2":relate2, "r3":relate3}	
	return relate

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
						description += get_content(des["content"])

			elif isinstance(description_list, BaseDict):
				if "pre" in description_list:
					if "content" in description_list["pre"]:
						description += get_content(description_list["pre"]["content"])
				elif "content" in description_list:
					description += get_content(description_list["content"])
				else:
					print("bad format!")

			elif isinstance(description_list, str):
				description += description_list
				
			else:
				print("bad format!")

	if "abstract" in patent.patent_document:
		if isinstance(patent.patent_document["abstract"], BaseList) or isinstance(patent.patent_document["abstract"], list):
			for x in patent.patent_document["abstract"]:
				if x["lang"]=="EN":
					abstract += get_dict_abs(x)
		elif isinstance(patent.patent_document["abstract"], BaseDict):
			if patent.patent_document["abstract"]["lang"]=="EN":
				abstract += get_dict_abs(patent.patent_document["abstract"])
		else:
			print("bad format!")
		
	my_dict = {"description": description, "abstract": abstract}
	return my_dict

def preprocess(mystring):
	sr = stopwords.words('english')

	tokens = word_tokenize(mystring)
	tokens=[token.lower() for token in tokens if token.isalpha()]

	clean_tokens = []
	for t in tokens:
		stemmer = WordNetLemmatizer().lemmatize(t)
		if stemmer not in sr:
			clean_tokens.append(stemmer)
	return clean_tokens

def get_common(qrel, patent):
	qrel_dict = p2str(qrel)
	patent_dict = p2str(patent)

	clean_qrel_abstract = preprocess(qrel_dict['abstract'])
	clean_qrel_description = preprocess(qrel_dict['description'])

	clean_patent_abstract = preprocess(patent_dict['abstract'])
	clean_patent_description = preprocess(patent_dict['description'])

	# common_abstract and common_description are string, word seperate by "," or space
	common_abstract = list(set(clean_qrel_abstract).intersection(set(clean_patent_abstract)))
	common_description = list(set(clean_qrel_description).intersection(set(clean_patent_description)))
	common_ipcr = get_common_ipcr(qrel, patent)
	ucid = qrel.patent_document["ucid"]

	ca = ""
	for a in common_abstract:
		ca += a
		if a != common_abstract[-1]:
			ca += " "

	cd = ""
	for d in common_description:
		cd += d
		if d != common_description[-1]:
			cd += " "

	re1 = common_ipcr["r1"]
	re2 = common_ipcr["r2"]
	re3 = common_ipcr["r3"]

	r1 = ""
	r2 = ""
	r3 = ""

	for x1 in re1:
		r1 +=x1
		if r1 != re1[-1]:
			r1 += " "

	for x2 in re2:
		r2 +=x2
		if r2 != re2[-1]:
			r2 += " "

	for x3 in re3:
		r3 +=x3
		if r3 != re3[-1]:
			r3 += " "

	common = Common(ucid, ca, cd, r1, r2, r3)

	#common.displayCommon()
	return common










	

	
