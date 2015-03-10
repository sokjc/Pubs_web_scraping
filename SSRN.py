import requests, csv
from bs4 import BeautifulSoup

def ssrn_author_publications_search(name):
	parameters = {'txtKey_Words':'','srchCrit':'all', 'optionDateLimit':'0', 'txtAuthorsName':name, 'btnSearch':'Search', 'Form_Name':'Abstract_Search'}
	r = requests.post('http://papers.ssrn.com/sol3/results.cfm?', params=parameters)
	
	soup = BeautifulSoup(r.content)
		
	for result in soup.find_all(valign="top", width="96%"):
		
		#Publication Title
		title_raw = result.strong.string
		title_utf8 = title_raw.encode('utf-8')
		
		#Extracts Unique identifier for publication
		for title_tag in result.find_all(target="_top"):
			pub_url = title_tag['href']
			print(pub_url)
			pub_id = pub_url[23:]
			print(pub_id)
			#Downloads the abstract from another page
			abstract = publication_abstract(pub_id)
			print(abstract)
		
		#Publication (ie Journal) information
		if result.i is not None:
			pub_info = result.i.string
		elif result.i is None:
			pub_info = ""
		#print(pub_info.decode('utf-8'))

		#Authors
		for authors in result.find_all("a"):
			pair = {}
			author = authors.get_text()
			author_utf8 = author.encode('utf-8')
			author_id = authors['target']
			pair[author_utf8]= author_id
			#print(pair)

def publication_abstract(publication_id):
	parameters = {'abstract_id':publication_id}
	r = requests.get('http://papers.ssrn.com/sol3/papers.cfm?', params=parameters)
	
	soup = BeautifulSoup(r.content)
	
	abstract_raw = soup.find(id="abstract").get_text()
	abstract_utf8 = abstract_raw.encode('utf-8')
	
	return abstract_utf8

ssrn_author_publications_search("John Smith")
