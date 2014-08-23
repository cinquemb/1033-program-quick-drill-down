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
company_tot = 0
company_count = 0
for node in raw_data_json_['2006-2014-foia-gov-surplus-mil']:
	for key, value in node.iteritems():
		county_keys = node[key]['counties_meta_data'].keys()
		for county in county_keys:
			query = node[key]['counties_meta_data'][county]['item']

			if node[key]['counties_meta_data'][county]['item_manufacturer'] != 'N/A':
				company_count += 1
				company_tot += 1
			else:
				company_tot += 1

				
			if query not in cache_item_dict and node[key]['counties_meta_data'][county]['item_manufacturer'] == 'N/A':
				stripped_query = re.sub('-', '', query).replace(' ', '')

				url = 'http://www.justnsnparts.com/nsnpart/%s.aspx' % (stripped_query)
				url2 = 'http://www.govliquidation.com/nsn_info/%s/%s.html' % (stripped_query[:5], stripped_query)
				url3 = 'http://buyaircraftparts.com/nsn/%s' % (query)

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

						r3 = requests.get(url3)
						soup3 = BeautifulSoup(r3.text)
						try:
							node_ = soup3.find_all('a', href=re.compile("/manufacturers/[0-9]+"))[0].string
							node_url = 'http://buyaircraftparts.com/manufacturers/%s' % (node_)

							#print node_url
							#sys.exit()
							
							r3_n = requests.get(node_url)
							split_string = 'Cage Code %s | Buy Aircraft Parts' % (node_)
							company = BeautifulSoup(r3_n.text).title.string.split(split_string)[0]
							print company
							print 'Hit 3! ', stripped_query, 'Length of string: ', len(stripped_query)

							company_info = 'N/A'
							data_size += 1
						except IndexError, e:
							print 'Miss! ', stripped_query, 'Length of string: ', len(stripped_query)
							#print "{%s:''}" % (stripped_query)
							company = 'N/A'
							company_info = 'N/A'
			

				size += 1

				cache_item_dict[query] = [company,company_info]
			elif node[key]['counties_meta_data'][county]['item_manufacturer'] == 'N/A':
				#print 'cache used'
				query_size += 1
				size += 1
				company = cache_item_dict[query][0]
				if company != 'N/A':
					data_size += 1
				company_info = cache_item_dict[query][1]
			
			#print company
			#print company_url
			if node[key]['counties_meta_data'][county]['item_manufacturer'] == 'N/A':
				node[key]['counties_meta_data'][county]['item_manufacturer'] = company
			elif node[key]['counties_meta_data'][county]['item_manufacturer'][-2:] == '- ':
				node[key]['counties_meta_data'][county]['item_manufacturer'] = node[key]['counties_meta_data'][county]['item_manufacturer'][:-2]
			

			
			if node[key]['counties_meta_data'][county]['item_manufacturer_meta_data'] == 'N/A' and company_info:
				node[key]['counties_meta_data'][county]['item_manufacturer_meta_data'] = company_info
			

#data = json.dumps(raw_data_json_)
f = open('2006-2014-foia-gov-surplus-mil.json', 'w+')
f.write(data)
f.close()
print 'Cache Used %s percent of time' % (round_format(query_size, size))
print 'Companies Found %s percent of time' % (round_format(data_size, size))
print 'Companies Found %s percent of Total Items' % (round_format(company_count, company_tot))