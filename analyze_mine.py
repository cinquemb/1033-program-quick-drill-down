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
cache_item_dict_node = dict()

for node in raw_data_json_['2006-2014-foia-gov-surplus-mil']:
	for key, value in node.iteritems():
		county_keys = node[key]['counties_meta_data'].keys()
		for county in county_keys:
			query = node[key]['counties_meta_data'][county]['item']

			if node[key]['counties_meta_data'][county]['item_manufacturer'] != 'N/A':
				company = node[key]['counties_meta_data'][county]['item_manufacturer'].lower().rstrip()
				cost = float(re.sub(',', '', node[key]['counties_meta_data'][county]['cost_sum'][1:]))

				if company in cache_item_dict:
					cache_item_dict[company] += cost

					items = cache_item_dict_node[company]
					if node[key]['counties_meta_data'][county]['item'] not in items:
						items.append(node[key]['counties_meta_data'][county]['item'])
					cache_item_dict_node[company] = items
				else:
					cache_item_dict[company] = cost
					cache_item_dict_node[company] = [node[key]['counties_meta_data'][county]['item']]

out_state_sorted_list =[]
for key, value in reversed(sorted(cache_item_dict.iteritems(), key=lambda (k,v): (v,k))):
	out_state_sorted_list.append({key: '${:,.2f}'.format(value)})
	print '~ %s: %s, items: %s\n' % (key ,'${:,.2f}'.format(value), cache_item_dict_node[key])
