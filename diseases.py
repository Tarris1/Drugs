import os
#from time import sleep
import json
import datetime #For date-extraction in log function
import re
import drugsAPI as API

#os.system('clear')

#Title Bar
class bcolors:
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

def import_data(loc):
	loc = "database.json"
	if os.path.exists(loc):
		with open(loc, 'r') as f:		
			database = json.load(f)
			
	else:
		database = {}
		database['log'] = []
		database['drugs'] = {}

	return database

def instructions():
	'''If command includes the word "help" - these instructions are printed'''

	print(bcolors.UNDERLINE+"\tYou will find all commands below:"+bcolors.ENDC+"\n")
	print("\t add @<drug name> @<category> @<diseases> @<clinical>")
	print("\t find/search @<anything> - Returns a table of all matching results")
	print("\t show @<All/id> - Prints a table with all or a specific drug")
	print("\t edit @<drug ID> @<name/category/disease/clinical> @<clear/more>")
	print("\t pubchem @<drug name> - Searches the pubchem database, returns synonyms if a specific compound does not exist")
	print("\t pubmed @<query> @<#articles> - Searches pubmed for relevant articles, returns a list of these articles with year published, journal and DOI link")
	print("\t trial @<query> @<#trials> - Searches clinicaltrials.gov for relevant trials")
	print("\t news @<query> - Searches for relevant news")
	print("\t patent @<query> - Searches for relevant USPTO patents")
	print("\t report @<query> - Makes a JSON file with a collection of articles, chemistry, news and trials of a drug")
	print("\t print log - prints the log.")
	print("\t quit/exit - Program stops\n")


def drug_table(id):
	'''Prints a table with overview of the drug'''
	to_edit = drugs[str(id)]
	drugName = to_edit['name']
	drugCategory = to_edit['category']
	drugDisease = to_edit['disease']
	drugClinical = to_edit['clinical']
	if drugClinical == "No".lower(): drugClinical = "Currently Marketed"
	print('\n*** Id: {}'.format(id))
	print('*** Drug: {}'.format(drugName))
	print('*** Category: {}'.format(drugCategory))
	print('*** Diseases: {}'.format(drugDisease))
	print('*** Clinical Status: {}'.format(drugClinical))
	if len(to_edit)>4:
		print('*** Misc.: {}'.format(to_edit['misc']))

def find_drug(x, length, id_list):
	'''Looks for the drug in the database. If prompt is find/search, it prints any drug that matches the search entry. If prompt is add, it checks if the particular drug exists and prints its contents if it exists'''

	data = x.split('@')
	prompt = data[0].strip() #Command inserted

#For command: find/search. If drug exists -> print table. Else -> print error
	if len(data)>1 and (prompt == 'find' or prompt == 'search'):
		ind = data[1].strip(); ind = ind.lower()
		anything = 0
		for a in id_list:
			contents = drugs[str(a)]
			content = str(a) + contents['name'] + contents['category'] + contents['clinical']+ contents['disease']+ contents['misc']; content = content.lower()
			if ind in content:
				#print('\nDrug exists, ID : {}'.format(a))
				anything += 1
				drug_table(a)
		if anything == 0:
			print("\nNo drug has been found.")

#For command: Add @<drug name> -> if the drug exists, stop the command and prompt its contents
	elif len(data)>1 and prompt == 'add':
		ind = data[1].strip(); ind = ind.lower()
		anything = 0
		for a in id_list:
			name = drugs[str(a)]['name'].lower()
			if ind in name and "+" not in name:
				drug_table(a)
				anything += 1
				return True
				break
		if anything == 0:
			return False


def edit_function(id_edit,  dataToEdit, change):
	'''Edits the data entry
	@Params. id_edit -> id of drug
	 	dataToEdit -> which datapoint to change
	 	change -> clear - removes existing data, more - adds to existing data '''
	for every in range(len(id_edit)):
		former_data = drugs[id_edit[every]][dataToEdit]
		former_ID = id_edit[every]
		former_drug = drugs[id_edit[every]]['name']
		print("\nID " + former_ID + ": " + former_drug + ", " + dataToEdit + ": " + former_data)
	new = raw_input("\nEnter new {}: ".format(dataToEdit)) 
	if len(new) >=1:
	#If a 3rd datapoint is added to edit, clear if rewrite - else add on top - 
		for every in range(len(id_edit)):
			if change == 'clear':	
				drugs[id_edit[every]][dataToEdit] = new
				drug_table(id_edit[every])
			elif change =='more': 
				former_data = drugs[id_edit[every]][dataToEdit]
				drugs[id_edit[every]][dataToEdit] = former_data+", " + new
				drug_table(id_edit[every])

def logging(x):
	'''Adds the command entered into the log with a datemarker
	@Params. x -> command entered'''

	date = datetime.datetime.now(); date = str(date)
	data = x.split('@')
	prompt = data[0].lower(); prompt = prompt.strip()
	new_log = {'date':date, 'entry':x, 'prompt': prompt}
	log.append(new_log)
	return new_log

def adding(x, data, length, id_list):
	'''Adds new drug if the drug cannot be find using the find_drug function.
	@params. x = command, data = splitted x, length+1 = index of new drug'''

	exists = find_drug(x, length, id_list) #Checks if drug already exists
	if exists == False: print("Adding new drug, {}: {}...\n".format((length+1),data[1]))
	elif exists == True: print('\nERROR: Drug Already Exists!\n')
	if len(data) > 4 and exists == False:
		drug = data[1]
		category = data[2]
		disease = data[3]
		clinical = data[4]
		if len(data)>=6: misc = data[5].strip()
		newID = length+1
		drugs[str(newID)] = {'name' : drug, 'category': category, 					'disease' : disease, 'clinical': clinical, 'misc' : misc}
		length = newID
	if len(data) == 2 and exists == False:
		drug = data[1]
		empty = ""; category = empty; disease = empty; clinical = empty
		misc = empty
		newID = length+1
		drugs[str(newID)]={'name' : drug, 'category': category, 					'disease' : disease, 'clinical': clinical, 'misc' : misc}
		length = newID
	return length

def convert_data():
	'''If I want to convert the JSON to a different structure, make the function here'''
	print("No data conversion function exists")

		
			
def find_highest_ID(data):
	ids = data.keys()
	newID = []
	for a in ids: newID.append(int(a))
	return max(newID)




def main():

	length = find_highest_ID(drugs)
	print("\n\t"+bcolors.HEADER+"Welcome to the drug database, please enter help for instructions\n" + bcolors.ENDC)
	print("There are currently " + str(length) + " drugs in this database.\n")	

	x = 'command'
	command = 0
	entry = "< "
	id_list = drugs.keys()
	while command <= 2:
		x = raw_input(entry)
		data = x.split('@') #Data is split into parts
		for p in range(len(data)): data[p] = data[p].strip(); data[p] = data[p].lower()
		if x == 'quit' or x == 'exit':
			exit()
		elif 'add' in x:
			misc = ''
			length = adding(x, data, length, id_list)
			id_list.append(length)
			logging (x)
			command-=1
		elif 'show' in x:
			if len(data)>1:
				showing = data[1]
				if showing == 'All'.lower():
					for i in range(1,length+1):
						drug_table(i)
				else:
					drugID = data[1].split(',')
					for p in range(len(drugID)): #Multiple show
						drugID[p] = drugID[p].strip()		
						try: 
							i = int(drugID[p])
							if i <= len(drugs): drug_table(i)
							else: print("There is no drug with that id ({})".format(i))
						except ValueError: print(drugID[p] + " is not an appropriate marker")
			logging(x)		
			command-=1
		elif 'help' in x:
			instructions()
			logging(x)
			command-=1
		elif 'edit' in x:
			command -=1
			editing = ['category', 'disease', 'name', 'clinical', 'misc']
			if len(data) >= 3:
				id_edit = data[1]
				dataToEdit = data[2]
				change = 'more'
				if len(data) == 4: change = data[3].lower()
				if dataToEdit in editing:
					id_edit = id_edit.strip().split(', ')
					for p in range(len(id_edit)): 
						id_edit[p] = str(re.search(r'\d+', id_edit[p]).group())	#Remove all non-integers from the data		
					edit_function(id_edit, dataToEdit, change) #Change: clear/more
			logging(x)
		
		elif 'find' in x or 'search' in x:
			command -= 1
			if len(data)>=2:
				print('Searching for "{}"...'.format(data[1]))
				find_drug(x, length, id_list)
				logging(x)
		
		elif 'pubchem' in x:
			command -= 1
			if len(data)>=2:
				print('Searching for "{}"..'.format(data[1]))
				API.pubchem(data[1].strip())
				logging(x)

		elif 'pubmed' in x:
			command -= 1
			if len(data)>=2:
				print('Searching for "{}" on pubmed...'.format(data[1]))
				query = data[1].strip()
				if len(data) == 2: API.pubmed(query)
				elif len(data) >= 3:
					num_articles = int(data[2].strip())
					API.pubmed(query, n = num_articles)
				logging(x)
			
		elif 'trial' in x:
			command -= 1
			if len(data)>=2:
				print('Searching for "{}" on clinicaltrials.gov...'.format(data[1]))
				if len(data)==2: 
					trials = API.trial(data[1])
					API.trial_brief(trials)
					print("\n")
				elif len(data) >= 3:
					num_trials = int(data[2].strip())
					#print(num_trials)
					trials = API.trial(data[1], n=num_trials)
					trial_brief(trials)
					print("\n")
					
		elif 'news' in x:
			command -= 1
			if len(data)>=2:
				print('Searching for news on "{}"'.format(data[1]))
				API.print_news(data[1])
				print("\n")

		elif 'patent' in x:
			command -= 1
			if len(data)>=2:
				print('Searching for patents on "{}"'.format(data[1]))
				API.print_patents(data[1])
				print("\n")
		

		elif 'report' in x:
			command -= 1
			if len(data)>=2:
				print('Generating Excel report on "{}"'.format(data[1]))
				now = datetime.datetime.now()
				report_json = API.report(data[1], articles=50, trials = 100)
				API.pdf_report(data[1], report_json )
				then = datetime.datetime.now()
				report_time = then-now
				seconds = report_time.total_seconds()
				print("\nReport took {} seconds".format(seconds))
			

		elif 'save' in x:
			command -= 1
			database['drugs'] = drugs
			database['log'] = log
			with open('database.json','w') as outfile:
				json.dump(database, outfile)
			logging(x)
			print("Saving changes...")


		elif 'print log' in x:
			command -= 1		
			p = logging(x)
			print(log)
		
		
		elif 'ids' in x:
			command -= 1
			find_highest_ID(database)		

		else:
			print("This is not a valid function")
			print("Write 'help' for an overview of valid functions")
			

		command+=1


if __name__ == '__main__':

	loc = "database.json"
	database = import_data(loc)
	drugs = database['drugs']
	log = database['log']
	main()


