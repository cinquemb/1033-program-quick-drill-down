import os
import sys
import re
import csv
import json
import requests
from time import sleep
from bs4 import BeautifulSoup

def round_format(nom,denom):

	try:
		if float(denom) > 0:
			percent = 100* round(float(nom)/float(denom), 2)
		else:
			percent = 0
	except Exception, e:
		percent = 0


	return percent

file_ = '1033-program-foia-may-2014.csv'
in_ = open('2006-2014-foia-gov-surplus-mil.json', 'r+')
raw_data_ = in_.read()
in_.close()

raw_data_json_ = json.loads(raw_data_)
cache_item_dict = dict()
size = 0
query_size = 0
data_size = 0
for node in raw_data_json_['2006-2014-foia-gov-surplus-mil']:
	for key, value in node.iteritems():
		county_keys = node[key]['counties_meta_data'].keys()
		for county in county_keys:
			query = node[key]['counties_meta_data'][county]['item']
			if query not in cache_item_dict:
				stripped_query = re.sub('-', '', query).replace(' ', '')

				url = 'http://www.justnsnparts.com/nsnpart/%s.aspx' % (stripped_query)
				url2 = 'http://www.govliquidation.com/nsn_info/%s/%s.html' % (stripped_query[:5], stripped_query)
				url3 = 'http://www.parttarget.com/formprocessor.aspx?formid=top_search_form&m=875&r=aHR0cDovL3d3dy5wYXJ0dGFyZ2V0LmNvbS9pbmRleC5hc3B4&userguid=BDEF4FE9-D508-4554-9D92-1170070BE59A&pagename=&searchtype=0&callid=a26d3a06-a428-43f8-8285-688f072bf444&asyncsearchurl=advancedsearchasync.aspx&searchtext=%s&originalsearchtext=&searchOption=sku' % (stripped_query)

				r = requests.get(url)
				
				soup = BeautifulSoup(r.text)

				try:
					table = soup.find_all('table', id='ctl00_ContentPlaceHolder1_ucNSNPartsListing_dlManufactureListing')[0]
					company = table.find_all('tr')[0].find_all('td')[0].find('a').string
					print 'Hit 1! ', stripped_query, 'Length of string: ', len(stripped_query)
					data_size += 1
					company_url = table.find_all('tr')[0].find_all('td')[0].find('a')['href']

					r1 = requests.get(company_url)
					soup1 = BeautifulSoup(r1.text)

					try:
						company_info = soup1.find_all("div", class_="para")[0].find_all('p')[0].get_text()
					except IndexError, e:
						company_info = 'N/A'

				except IndexError, e:
					#print 'check next query len: ',len(stripped_query[:5])
					r2 = requests.get(url2)
					soup2 = BeautifulSoup(r2.text)
					try:
						company = soup2.find_all('a', href=re.compile("JavaScript: runSearch\('company','"))[0].string
						print 'Hit 2! ', stripped_query, 'Length of string: ', len(stripped_query)
						company_info = 'N/A'
						data_size += 1
					except IndexError, e:

						#'Cookie: site_order=USER_ID=BDEF4FE9-D508-4554-9D92-1170070BE59A&GUID_TIME=20140821213321; PREF_LANG=; __utma=204617361.1398110140.1408671120.1408671120.1408671120.1; __utmb=204617361.8.10.1408671120; __utmc=204617361; __utmz=204617361.1408671120.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'

						cookies = {
							'site_order': 'USER_ID=BDEF4FE9-D508-4554-9D92-1170070BE59A&GUID_TIME=20140821213321',
							'PREF_LANG': '',
							'__utma': '204617361.1398110140.1408671120.1408671120.1408671120.1',
							'__utmb': '204617361.8.10.1408671120',
							'__utmc': '204617361',
							'__utmz': '04617361.1408671120.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none)'
						}
						headers = {
							'Host': 'www.parttarget.com',
							'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.9; rv:31.0) Gecko/20100101 Firefox/31.0',
							'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8'
						}

						r3 = requests.get(url3, headers=headers, cookies=cookies)
						soup3 = BeautifulSoup(r3.text)	

						try:
							company = soup3.find_all('table', class_="table-catalog table-part table-index-5 table-supplier")[0].find_all('td', class_="pos_3")[0].find('a').string
							print 'Hit 3! ', stripped_query, 'Length of string: ', len(stripped_query), 'company ', company
							company_info = 'N/A'
							data_size += 1
						except IndexError, e:
							if '403 - Forbidden: Access is denied.' in 	r3.text:
								print 'cookies are bad'	
							print 'error', r3.status_code
							print 'Miss! ', stripped_query, 'Length of string: ', len(stripped_query)
							company = 'N/A'
							company_info = 'N/A'
							#sys.exit()					

				size += 1

				cache_item_dict[query] = [company,company_info]
			else:
				#print 'cache used'
				query_size += 1
				size += 1
				company = cache_item_dict[query][0]
				if company != 'N/A':
					data_size += 1
				company_info = cache_item_dict[query][1]
			
			#print company
			#print company_url
			node[key]['counties_meta_data'][county]['item_manufacturer'] = company
			node[key]['counties_meta_data'][county]['item_manufacturer_meta_data'] = company_info

data = json.dumps(raw_data_json_)
f = open('2006-2014-foia-gov-surplus-mil.json', 'w+')
f.write(data)
f.close()
print 'Cache Used %s percent of time' % (round_format(query_size, size))
print 'Companies Found %s percent of time' % (round_format(data_size, size))