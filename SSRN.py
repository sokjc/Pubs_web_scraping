import requests, csv, sqlite3
from bs4 import BeautifulSoup

#Create a database for our search results
conn = sqlite3.connect("ssrn_results.db")
cursor = conn.cursor()

cursor.executescript('''
	DROP TABLE IF EXISTS ssrn_publication;
	CREATE TABLE IF NOT EXISTS ssrn_publication (
		pub_id TEXT PRIMARY KEY,
		title TEXT,
		abstract TEXT,
		pub_info TEXT 
		);
	DROP TABLE IF EXISTS ssrn_pub_author_link ;
	CREATE TABLE IF NOT EXISTS ssrn_pub_author_link (
		pub_id TEXT,
		author_id TEXT
		);
	DROP TABLE IF EXISTS ssrn_author;
	CREATE TABLE IF NOT EXISTS ssrn_author (
		author_id TEXT PRIMARY KEY,
		name TEXT,
		other TEXT
		);
	''')
conn.commit()


def ssrn_author_publications_search(page_of_search_results):

	soup = BeautifulSoup(page_of_search_results)
	
	ssrn_publication = []
	
	for result in soup.find_all(valign="top", width="96%"):
		for title_tag in result.find_all(target="_top"):
			
			#Publication Title
			title_raw = result.strong.string
			title_utf8 = title_raw.encode('utf-8')
			#print(title_utf8)
			
			#Publication ID
			pub_url = title_tag['href']
			#print(pub_url)
			pub_id = pub_url[23:]
			#print(pub_id)
			
			#Downloads the abstract from another page
			abstract = publication_abstract(pub_id)
			#print(abstract)
			
			#Publication (ie Journal) information
			if result.i is not None:
				pub_info = result.i.string
			elif result.i is None:
				pub_info = ""
				
			#Put into local SSRN DB
			cursor.execute('INSERT INTO ssrn_publication VALUES (?,?,?,?)', (pub_id, title_raw, abstract, pub_info))
			conn.commit()
			
		#Authors
		for authors in result.find_all("a", class_='textlink'):
			pair = {}
			author = authors.get_text()
			author_utf8 = author.encode('utf-8')
			author_id = authors['target']
			pair[pub_id]= author_id
			print(pair)
			cursor.execute('INSERT INTO ssrn_pub_author_link VALUES (?,?)', (pub_id, author_id))
			conn.commit()

def publication_abstract(publication_id):
	parameters = {'abstract_id':publication_id}
	r = requests.get('http://papers.ssrn.com/sol3/papers.cfm?', params=parameters)
	
	soup = BeautifulSoup(r.content)
	
	abstract_raw = soup.find(id="abstract").get_text()
	abstract_utf8 = abstract_raw.encode('utf-8')
	
	return abstract_raw

# Author detail function should go here.

def publications_search(name):
		parameters = {'txtKey_Words':'','srchCrit':'all', 'optionDateLimit':'0', 'txtAuthorsName':name, 'btnSearch':'Search', 'Form_Name':'Abstract_Search'}
		r = requests.post('http://papers.ssrn.com/sol3/results.cfm?npage=1&', params=parameters)
		
		soup = BeautifulSoup(r.content)
		
		#Parse out the number of pages.
		result = soup.find(attrs={'name':'iTotalResults', 'type':'hidden'})
		print(result)
		x = result['value']
		pages = float(x)
		
		#list_of_pages = [1]
		#list = [] for in in range(pages)
		
		for page in range(pages):
			parameters = {'txtKey_Words':'','srchCrit':'all', 'optionDateLimit':'0', 'txtAuthorsName':name, 'btnSearch':'Search', 'Form_Name':'Abstract_Search'}
			r = requests.post('http://papers.ssrn.com/sol3/results.cfm?npage=%str&' % page, params = parameters)
			each_page = r.content
			ssrn_author_publications_search(each_page)
	
publications_search("John Smith")
conn.commit()
conn.close()
