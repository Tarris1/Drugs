import json
import datetime
import requests
import pubchempy as pcp
import urllib
from dateutil import parser
from Bio import Entrez
import xlsxwriter

class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def import_email():
	loc = "apidata.json"
	if os.path.exists(loc):
		with open(loc, 'r') as f:		
			data = json.load(f)
			email = data["email"]
		return email

def import_api_key():
	loc = "apidata.json"
	if os.path.exists(loc):
		with open(loc, 'r') as f:		
			data = json.load(f)
			api = data["api_key"]
		return api


def pubchem(compound, isCompound = True, report = False):

	def drug_form (compound, report = False):
		'''Prints data and returns it of a compound from pcp'''
		cid = compound.cid
		Entrez.email = import_email()
		x = Entrez.esummary(db="pccompound", id = cid) #Obtain data
		record = Entrez.read(x)
		#pharmaKeys = record[0].keys()
		#SynonymList, Id, MolecularFormula, MolecularWeight, HydrogenBondDonorCount, HydrogenBondAcceptorCount, PharmActionList,XLogP
		record = record[0]
		action = record['PharmActionList']
		weight = record['MolecularWeight']
		formula = record['MolecularFormula']
		donors = record['HydrogenBondDonorCount']
		acceptors = record['HydrogenBondAcceptorCount']
		XLogP = record['XLogP']
		names = record['SynonymList']
		rotatable = record['RotatableBondCount']
		'''weight = compound.molecular_weight
		formula = compound.molecular_formula
		names = compound.synonyms
		donors = compound.h_bond_donor_count
		acceptors = compound.h_bond_acceptor_count
		rotatable = compound.rotatable_bond_count
		XLogP = compound.xlogp'''
		if report == False:
			if len(names)>= 5: print("Names: " + str(names[0:5]))
			else: print("Names: " + str(names[0:len(names)]))
			print("Weight: " + str(weight))
			print("Formula: " + str(formula))
			print("Donors, acceptors and rotatables: " + str(donors) + ", " + str(acceptors) + ", " + str(rotatable))
			print("XLogP: " + str(XLogP))
			if len(action)>=10: print("Actions: " + str(action[0:10]))
			else: print("Actions: " + str(action))
		drug_data = {"weight":weight, "formula":formula, "names":names, "donors":donors, "acceptors":acceptors, "rotatable":rotatable, "XLogP": XLogP, 'action':action}
		return drug_data



	if report == True: print("Importing relevant data from the query {}".format(compound))
	info = ""
	x = pcp.get_compounds(compound, 'name')
	if len(x) > 0: #Checks if there is a compound with the name "compound"
		info = drug_form(x[0], report)
		return info
	else: 
		if report == False: print("No results have been found using get_compounds, proceeding with substance search...")
		x = pcp.get_substances(compound, 'name')
		if len(x) >0: #If a substance is found, do this...
			if report == False: 
				print("Substances found: " +  str(x))
				print("\nFinding all synonyms...")
			info = []
			for every in range(len(x)):
				if report == False: print(x[every].synonyms)
				info.append(x[every].synonyms)
			return info
		else: 
			if report == False: print("No drug information has been found")
			return info
	



def pubmed(x, n=10, report = False):


	##Retrieves details of an article from Pubmed's API
	def retrieve_article_info(article, details):
		

		articleTable = "\n"
		key = article.keys()
		articleYear = ""
		articleTitle = ""
		authorList = ""
		abstractText = ""
		DOI = ""
		journal = ""
		
		if "Abstract" in key:
			for p in range(len(details)):
				detail = details[p]
				if details[p] in key: stuff = article[details[p]]
				else: break
				if detail == "ArticleDate": #List of date info, index 0 contains date with year, month and day
					if len(stuff)>0:
						articleYear = str(stuff[0]["Year"])
				
				elif detail == "ArticleTitle":
					articleTitle = stuff

				elif detail == "Abstract": #List of abstracts
					abstracts = stuff['AbstractText']
					for i in range(len(abstracts)): 
						abstractText = abstractText+abstracts[i]+" "
					
				elif detail == "AuthorList": #List of authors
					for authors in range(len(stuff)):
						lastName = ""; foreName = ""
						authorKeys = stuff[authors].keys()
						if "LastName" in authorKeys: lastName = stuff[authors]['LastName']
						if "ForeName" in authorKeys: foreName = stuff[authors]['ForeName']
						elif "Initials" in authorKeys: foreName = stuff[authors]['Initials']
						authorList = authorList + lastName+ ", " + foreName
						if authors != len(stuff): authorList = authorList+ "; "
				elif detail == "Journal":
					journal = stuff['Title']

				elif detail == "ELocationID": #Extract doi-based link
					for aid in range(len(stuff)):
						eidtype = stuff[aid].attributes["EIdType"]
						if eidtype == "doi":
							DOI = "https://doi.org/" + stuff[aid]
		
		articleDict = {'title':articleTitle, 'authors':authorList, 'year':articleYear, 'abstract':abstractText, 'journal':journal, "doi":DOI}	
		return articleDict



	def search_pubmed(query, retmax, db = 'pubmed'):
		Entrez.email = import_email()
		handle = Entrez.esearch(db=db, 
				    sort='relevance', 
				    retmax=retmax,
				    retmode='xml', 
				    term=query)
		results = Entrez.read(handle)
		return results


	def fetch_details(id_list, db = 'pubmed'):
		ids = ','.join(id_list)
		Entrez.email = import_email()
		handle = Entrez.efetch(db=db,
				   retmode='xml',
				   id=ids)
		results = Entrez.read(handle)
		return results



	if report == True: print("Importing articles with the query {}...".format(x))
	details = ["ArticleDate", "AuthorList", "Journal", "ArticleTitle", "Abstract", "ELocationID"]
	results = search_pubmed(x, n)
	id_list = results['IdList']
	articles = []
	if len(id_list)>0:
		papers = fetch_details(id_list)
		articles = papers['PubmedArticle'] #List of articles
	num_articles = len(articles)
	article_info = []
	for article in range(num_articles):
		info = retrieve_article_info(articles[article]['MedlineCitation']['Article'], details)
		if report == False: print(str(article+1)+": " + info['title'] + "(" + info['year'] + ")" + " - " + info['journal'] + " - " + info['doi']+ "\n")
		article_info.append(info)
		
	if report == False: print("Number of articles found: " + str(num_articles))
	return article_info

def extract_values(obj, key):
    """Pull all values of specified key from nested JSON."""
    arr = []

    def extract(obj, arr, key):
        """Recursively search for values of key in JSON tree."""
        if isinstance(obj, dict):
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    extract(v, arr, key)
                elif k == key:
                    arr.append(v)
        elif isinstance(obj, list):
            for item in obj:
                extract(item, arr, key)
        return arr

    results = extract(obj, arr, key)
    return results

def trial(query, n=5, report = False):

	def extract_values(obj, key):
		"""Pull all values of specified key from nested JSON."""
		arr = []

		def extract(obj, arr, key):
		#"""Recursively search for values of key in JSON tree."""
			if isinstance(obj, dict):
			    for k, v in obj.items():
				if isinstance(v, (dict, list)):
				    extract(v, arr, key)
				elif k == key:
				    arr.append(v)
			elif isinstance(obj, list):
			    for item in obj:
				extract(item, arr, key)
			return arr

		results = extract(obj, arr, key)
		return results



	if report == True: print("Importing all relevant trials for query {}".format(query))
	data = query; data = data.lower()
	expr = data.strip()
	expr = expr.split(" ")
	query = ""
	for p in range(len(expr)):
		if p == 0: query = query+expr[p]
		else: query = query + "+" + expr[p]
	
	url = "https://clinicaltrials.gov/api/query/full_studies?expr="+query +"&min_rnk=1&max_rnk="+str(n)+"&fmt=json"
	response = urllib.urlopen(url)
	data = json.loads(response.read())

	extractables = ["OfficialTitle", "NCTId", "Condition", "ArmGroupDescription", "OrgFullName", "BriefSummary", "EnrollmentCount", "StartDate", "OverallStatus", "PrimaryOutcomeMeasure"]
	num_studies = data["FullStudiesResponse"]["NStudiesReturned"] #Number of trials found
	responseKey = data["FullStudiesResponse"].keys()
	if "FullStudies" in responseKey: studies = data["FullStudiesResponse"]["FullStudies"] #Extracts the studies from original json
	else: 
		print("No trial has been found")
	
	clinicData = []
	for clinic in range(num_studies):
		study = studies[clinic]["Study"]["ProtocolSection"]
		trial = []
		for z in range(len(extractables)):
			data = extractables[z]
			stuff = "NA"
			if data == "Condition": stuff = study["ConditionsModule"]["ConditionList"]["Condition"]
			elif data == "StartDate": #https://xlsxwriter.readthedocs.io/example_images.html
				stuff = extract_values(study, data)
				if len(stuff)>0: stuff[0] = str(parser.parse(stuff[0])) 
				#https://stackoverflow.com/questions/466345/converting-string-into-datetime - maybe timestring
			else: 
				values = extract_values(study, data)
				if len(values)>0: stuff = values
			trial.append(stuff)
	 
		zipped = dict(zip(extractables, trial))
		clinicData.append(zipped)

	return clinicData

def trial_brief(trials):
	num_articles = len(trials)
	for trial in range(num_articles):
		print("\n")
		print("Trial " + str(trial+1) + ": "+ trials[trial]["OfficialTitle"][0])
		print("NCT ID: " + trials[trial]["NCTId"][0])
		print("Conditions: " + trials[trial]["Condition"][0])
		print("Primary Outcome: " + trials[trial]["PrimaryOutcomeMeasure"][0])
		print("Summary: " + trials[trial]["BriefSummary"][0])
		if len(trials[trial]["StartDate"])>0: print("Start Date: " + trials[trial]["StartDate"][0])
		print("Enrollment: " + trials[trial]["EnrollmentCount"][0])
		print("Organization: " + trials[trial]["OrgFullName"][0])
		print("Arms: ")
		for p in trials[trial]["ArmGroupDescription"]: print p,



def article_dict(drugName, report = False):

	def find_articles (query, api, days=14):
		'''Prints relevant articles from 2 weeks ago until today'''
		print("Importing all news articles for the last {} days relevant to the query {}".format(str(days), query))
		date = datetime.date.today()
		date = date-datetime.timedelta(days=days) 
		url = ('https://newsapi.org/v2/everything?q='+query+'&'
		       'from='+str(date)+'&'
		       'sortBy=popularity&'+
		       'apiKey='+api)
		response = requests.get(url)
		response = response.json()
		return response


	api = import_api_key()
	response = find_articles(drugName, api)
	num_articles = response['totalResults']
	articles = response['articles']
	article_list = []
	for article in articles:
		#published_date = ""
		title = article['title']
		url = article['url']
		source = article['source']['name']#str(article['source']['name'])
		published_date = article['publishedAt']
		article_info = {'title':title, 'url':url, 'source':source, 'published_date':published_date}
		article_list.append(article_info)

	if report == True: print("Number of articles found: " + str(num_articles))
	return article_list

def print_news(drugName, n=10):
	'''Prints a summary of recent news articles'''
	article_list = article_dict(drugName) #Import articles
	num_articles = len(article_list) #Number of articles found
	print("{} articles have been found on {}".format(num_articles, drugName))
	if num_articles < n: n = num_articles
	for i in range(n):
		article = article_list[i]
		articleKeys = article.keys()
		print("\n"+"Article " + str(i+1)+": ")
		for key in articleKeys:
			print(key+": " + article[key])

def find_patents(query, n=100, report = False):
	if report == True: print("Importing all relevant patents to the query {}".format(query))
	url = "https://developer.uspto.gov/ibd-api/v1/patent/application?searchText="+query+"&start=0&rows="+str(n)
	response = requests.get(url, allow_redirects=True, verify=False)
	response = response.json()
	patents = response['response']
	num_patents = patents['numFound']
	if num_patents > n: num_patents = n
	if num_patents>0: patent_data = patents['docs']
	else: patent_data = ""

	return patent_data
	
def print_patents(drugName, n = 10):
	'''Prints patent information'''
	patents = find_patents(drugName)
	num_patents = len(patents)
	
	if num_patents < n: n = num_patents
	print("{} patents have been found on {}".format(num_patents, drugName))
	for i in range(n):
		patent = patents[i]
		patentKeys = patent.keys()
		print("\n"+bcolors.HEADER+"Patent " + str(i+1)+ ": "+bcolors.ENDC)
		for key in patentKeys:
			print(bcolors.UNDERLINE+key+": "+bcolors.ENDC)# + patent[key])
			if type(patent[key]) is list:
				for x in patent[key]:
					print(x)
			else:
				print(patent[key])




def report(drugName, articles=10, trials = 10):
	'''Puts together a report with a collection of articles, trials and the chemistry of a particular drug'''
	articles = pubmed(drugName, n=articles, report = True) #Contains title, authors, years, journal, abstract and doi (if they exist)
	chemistry = pubchem (drugName, report = True) #Contains a set of chemistry info and synonyms related to drug
	trials = trial(drugName, n=trials, report = True)
	news = article_dict(drugName, report = True)
	patents = find_patents(drugName, report = True)
	drug_report = {'articles':articles, 'chemistry':chemistry, 'trials':trials, 'news':news, 'patents':patents}
	return drug_report
	
def pdf_report (drugName, drug_report):
	#drug_report contains 'articles', 'chemistry', 'trials', 'news' and 'patents'
	workbook = xlsxwriter.Workbook(drugName+".xlsx")
	reportKeys = drug_report.keys()
	len_report = len(reportKeys)
	for a in range(len_report):
		dataType = reportKeys[a]
		print("Adding {} to excel sheet...".format(dataType))
		#worksheet = workbook.add_worksheet(dataType)
		data = drug_report[dataType] #Extract the relevant data
		row = 0 #Starting row
		col = 0
		if dataType == "chemistry" and type(data) is not str: #If its chemistry -> dictionary, NOT a list
			worksheet = workbook.add_worksheet(dataType)
			dataKeys = data.keys() #Extract the keys of the chemistry dictionary
			for key in dataKeys: #Go through each of the keys, extract the data and write them into excel worksheet
				entry = data[key]
				worksheet.write(row,col,key)
				if str(type(entry))=="<class 'Bio.Entrez.Parser.ListElement'>": #makes a data entry for every datapoint if its a list					
					for p in range(len(entry)):
						worksheet.write(row+1+p,col,str(entry[p]))
				else: worksheet.write(row+1, col, str(entry))
				col+=1
		else:
			worksheet = workbook.add_worksheet(dataType)
			max_key = 0
			num_data = len(data) #Amount of data points in the lists
			for i in range(num_data): #Extract the largest entry's keys and n number
				num_key = len(data[i].keys()) #extract the number of keys in the data
				if num_key > max_key: #Check if its larger than previous
					max_key = num_key
					mainCol = data[i].keys()
					data_n = i
			for entry in data: #Go through each data point in the data extracted
				col = 0 #Start with column 0 for each entry
				entryKeys = entry.keys() #Extract the keys
				for key in entryKeys: #Go through each key
					if row == data_n: worksheet.write(0, col, key) #only add the headers of the longest entry
					if key in mainCol: colKey = mainCol.index(key) #Find the right index
					else: colKey = len(mainCol) #Otherwise add it to the last column
					entry_point = entry[key] #Extract the specific data 
				
					if type(entry_point) != list and type(entry_point) != dict and type(entry_point)!= int: entry_point = entry_point.encode('ascii', 'ignore').decode('ascii') #If the datapoint is not a list and it is not a dictionary, decode it.
					elif type(entry_point)==list: #if the type is a list, decode each entry
						length = len(entry_point)
						if length >1:
							new_string = ""
							for l in range(len(entry_point)):
								entry_point[l] = entry_point[l].encode('ascii', 'ignore').decode('ascii')
								if l != length-1: new_string = new_string+entry_point[l]+", "
								else: new_string = new_string+entry_point[l]
							entry_point = new_string
						else: 
							entry_point[0].encode('ascii', 'ignore').decode('ascii')							
							entry_point = entry_point[0]
					if type(entry_point) != int: entry_point = entry_point.encode('ascii', 'ignore').decode('ascii')					
					entry_point = str(entry_point)
					worksheet.write(row+1, colKey, entry_point)
					col += 1
				row += 1
	workbook.close()





	
