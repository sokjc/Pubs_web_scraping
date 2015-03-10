import requests, csv
from bs4 import BeautifulSoup

def ssrn_author_publications_search(name):
	parameters = {'txtKey_Words':'','srchCrit':'all', 'optionDateLimit':'0', 'txtAuthorsName':name, 'btnSearch':'Search', 'Form_Name':'Abstract_Search'}
	r = requests.post('http://papers.ssrn.com/sol3/results.cfm?', params=parameters)
	
	soup = BeautifulSoup(r.content)
		
	for result in soup.find_all(valign="top", width="96%"):
		
		#Publication Title
		title = result.strong.string
		
		#Publication (ie Journal) information
		if result.i is not None:
			pub_info = result.i.string
		elif result.i is None:
			pub_info = ""
		print(pub_info.decode('utf-8'))

		#Authors
		for authors in result.find_all("a"):
			author = authors.get_text()
			print(author)
		
		
ssrn_author_publications_search("John Smith")
