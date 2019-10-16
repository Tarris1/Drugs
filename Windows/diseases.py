import os
#from time import sleep
import json
import datetime #For date-extraction in log function
import re
import drugsAPI3 as API


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

	print("\tYou will find all commands below:\n")
	print("\t add @<drug name> @<category> @<diseases> @<clinical>")
	print("\t find/search @<anything> - Returns a table of all matching results")
	print("\t show @<All/id> - Prints a table with all or a specific drug")
	print("\t edit @<drug ID> @<name/category/disease/clinical> @<clear/more>")
	print("\t remove/delete @<drug ID> - removes the drug from the database")
	print("\t pubchem @<drug name> - Searches the pubchem database, returns synonyms if a specific compound does not exist")
	print("\t pubmed @<query> @<#articles> - Searches pubmed for relevant articles, returns a list of these articles with year published, journal and DOI link")
	print("\t trial @<query> @<#trials> - Searches clinicaltrials.gov for relevant trials")
	print("\t news @<query> - Searches for relevant news")
	print("\t patent @<query> - Searches for relevant USPTO patents")
	print("\t report @<query> - Makes a JSON file with a collection of articles, chemistry, news and trials of a drug")
	print("\t print log - prints the log.")
	print("\t duplicates - finds the ids of any duplicate entry.")
	print("\t quit/exit - Program stops")
	print("\t Empty command clears the console\n")


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

def find_drug(data, id_list):
	'''Looks for the drug in the database. If prompt is find/search, it prints any drug that matches the search entry. If prompt is add, it checks if the particular drug exists and prints its contents if it exists'''

	prompt = data[0] #Command inserted
	if len(data)>1: ind = data[1]
	else: ind = prompt
	anything = 0
	if len(ind)>0:
		for a in id_list:
			a = str(a)
			if prompt == 'add': #See if drug exists in database
				name = drugs[a]['name'].lower()
				if ind in name and "+" not in name:
					drug_table(a)
					anything += 1
					return True
					break
			elif prompt == 'remove':
				if ind == a:
					drug_table(a)
					anything += 1
					return True
					break
			else: #Search using 'find', 'show' or '<anything>'
				contents = drugs[a]
				content = a + contents['name'] + contents['category'] + contents['clinical']+ contents['disease']+ contents['misc']
				content = content.lower()
				if ind in content:
					anything += 1
					drug_table(a)
			
		if anything == 0:
			if prompt == 'add' or prompt == 'remove': return False
			else: print("\nNo drug has been found.")
		else: print("\n{} Matching drugs have been found.\n".format(str(anything)))
	else: os.system('cls' if os.name=='nt' else 'clear') #os.system('clear') #does not work on windows


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
	new = input("\nEnter new {}: ".format(dataToEdit)) 
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

	exists = find_drug(data, id_list) #Checks if drug already exists
	if exists == False: print("Adding new drug, {}: {}...\n".format((length+1),data[1]))
	elif exists == True: print('\nERROR: Drug Already Exists!\n')
	if len(data) > 4 and exists == False:
		drug = data[1]
		category = data[2]
		disease = data[3]
		clinical = data[4]
		if len(data)>=6: misc = data[5].strip()
		newID = length+1
		drugs[str(newID)] = {'name' : drug, 'category': category, 'disease' : disease, 'clinical': clinical, 'misc' : misc}
		length = newID
	if len(data) == 2 and exists == False:
		drug = data[1]
		empty = ""; category = empty; disease = empty; clinical = empty
		misc = empty
		newID = length+1
		drugs[str(newID)]={'name' : drug, 'category': category, 'disease' : disease, 'clinical': clinical, 'misc' : misc}
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
    
def print_trial(data):
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
			API.trial_brief(trials)
			print("\n")

def print_show(data):
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


def remove_drug(data, id_list):
	exists = find_drug(data, id_list)
	if exists == True:
		to_delete = input("Are you sure you want to remove this drug from the database? ")
		if to_delete in ["yes", "y"]:
			drugs.pop(data[1])
			print("The drug #{} has been removed".format(data[1])) 
	else: print("There is no drug with that ID.")

def find_duplicates(drugs):
	drug_ids = list(drugs.keys())
	for drug in drug_ids:
		name = drugs[drug]["name"]
		subNames = name.split(",")
		for drug_two in drug_ids:
			if drug_two is not drug: #Checks if its the same id
				name_two = drugs[drug_two]["name"]
				for z in subNames:
					if z in name_two: 
						subNameTwo = name_two.split(",")
						for a in subNameTwo:
							if subNames[0] == a:
								print("{}:{}".format(drug, drug_two))


def main():
	length = find_highest_ID(drugs)
	print("\n\tWelcome to the drug database, please enter help for instructions\n")
	print("There are currently " + str(length) + " drugs in this database.\n")	

	x = 'command'
	command = 0
	entry = "< "
	id_list = list(drugs.keys())
	while command <= 2:
		x = input(entry)
		data = x.split('@') #Data is split into parts
		for p in range(len(data)): data[p] = data[p].strip(); data[p] = data[p].lower()
		if data[0] == 'quit' or x == 'exit': exit()
		elif data[0] == 'add':
			misc = ''
			length = adding(data, length, id_list)
			id_list.append(length)
			logging (x)
		elif data[0] == 'show':
			print_show(data)
			logging(x)
		elif data[0] == 'help':
			instructions()
			logging(x)
		elif data[0] == 'edit':
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
		elif data[0] == 'find' or data[0] == 'search':
			if len(data)>=2:
				print('Searching for "{}"...'.format(data[1]))
				find_drug(data, id_list)
				logging(x)
		elif data[0] == 'pubchem':
			if len(data)>=2:
				print('Searching for "{}"..'.format(data[1]))
				API.pubchem(data[1].strip())
				logging(x)

		elif data[0] == 'pubmed':
			if len(data)>=2:
				print('Searching for "{}" on pubmed...'.format(data[1]))
				query = data[1].strip()
				if len(data) == 2: API.pubmed(query)
				elif len(data) >= 3:
					num_articles = int(data[2].strip())
					API.pubmed(query, n = num_articles)
				logging(x)
			
		elif data[0] == 'trial': print_trial(data)
					
		elif data[0] == 'news':
			if len(data)>=2:
				print('Searching for news on "{}"'.format(data[1]))
				API.print_news(data[1])
				print("\n")

		elif data[0] == 'patent':
			if len(data)>=2:
				print('Searching for patents on "{}"'.format(data[1]))
				API.print_patents(data[1])
				print("\n")
		

		elif data[0] == 'report':
			if len(data)>=2:
				print('Generating Excel report on "{}"'.format(data[1]))
				now = datetime.datetime.now()
				report_json = API.report(data[1], articles=50, trials = 100)
				API.pdf_report(data[1], report_json )
				then = datetime.datetime.now()
				report_time = then-now
				seconds = report_time.total_seconds()
				print("\nReport took {} seconds".format(seconds))
			
		elif data[0] == 'save':
			database['drugs'] = drugs
			database['log'] = log
			with open('database.json','w') as outfile:
				json.dump(database, outfile)
			logging(x)
			print("Saving changes...")
		
		elif data[0] == 'remove' or data[0] == "delete": remove_drug(data, id_list)

		elif data[0] == 'duplicates': find_duplicates(drugs)

		elif data[0] == 'print log': print(log)
		
		elif data[0] == 'ids': print(find_highest_ID(drugs)) #Prints out the highest ID

		else: find_drug(data, id_list)
		#print("This is not a valid function.\nWrite 'help' for an overview of valid functions.")
                


if __name__ == '__main__':

	loc = "database.json" #Location in the current directory of the database
	database = import_data(loc) #Loads the data
	drugs = database['drugs'] #Separates the log and drug database
	log = database['log']
	main()



