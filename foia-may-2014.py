import os
import sys
import re
import csv
import json
import requests
from time import sleep
from bs4 import BeautifulSoup

def round_format(nom,denom):
	percent = 100* round(nom/denom, 2)
	return percent

file_ = '1033-program-foia-may-2014.csv'
d = dict()
with open(file_, 'r+') as f_ss:
	reader = csv.reader(f_ss, delimiter=',')
	for k, row in enumerate(reader):
		if k > 1:
			state_ = row[0]#stat
			county_ = row[1]# county
			if '' == county_:
				county_ = '-'
				#print 'missing county for: ', state_
			if ' ' == county_:
				county_ = '-'
				#print 'missing county for: ', state_
			nsn_ = row[2]#National Stock Number
			nsn_name_ = row[3]# name
			amount_ = row[4]#state

			row[5] #state
			cost_ = row[6] #state
			ship_date_ = row[7]#date
			state_key = state_
			county_key = county_
			nsn_key = nsn_

			if state_key in d:
				if county_key in d[state_key]:
					if str(nsn_key) in d[state_key][county_key]:
						node = d[state_key][county_key][str(nsn_key)]
						date_list = node['ship_date(s)']
						date_list.append(ship_date_) 
						node = {'amount': node['amount'] + int(amount_), 'cost($)': node['cost($)'] + float(cost_) * int(amount_), 'ship_date(s)': date_list}
					else:
						d[state_key][county_key][str(nsn_key)] = {'amount': int(amount_), 'cost($)': float(cost_) * int(amount_), 'ship_date(s)': [ship_date_]}
				else:
					d[state_key][county_key] = {str(nsn_key): {'amount': int(amount_), 'cost($)': float(cost_) * int(amount_), 'ship_date(s)': [ship_date_]}}
			else:
				d[state_key] = {county_key: {str(nsn_key): {'amount': int(amount_), 'cost($)': float(cost_) * int(amount_), 'ship_date(s)': [ship_date_]}}}


state_dict = dict()
out_state_dict = dict()
for state in d:
	tot_fed_cost_for_state = 0
	count_dict = dict()
	out_county_dict = dict()
	for county in  d[state]:
		item_node = d[state][county]
		item_keys = item_node.keys()

		item_dict = dict()
		item_unit_dict = dict()
		tot_fed_cost_for_county = 0
		for item_key in item_keys:
			tot_fed_cost_for_state += d[state][county][item_key]['cost($)']
			tot_fed_cost_for_county += d[state][county][item_key]['cost($)']

			if item_key in item_dict:
				item_dict[item_key] += d[state][county][item_key]['cost($)']
				item_unit_dict[item_key] += d[state][county][item_key]['amount']
			else:
				item_dict[item_key] = d[state][county][item_key]['cost($)']
				item_unit_dict[item_key] = d[state][county][item_key]['amount']

			if county in count_dict:
				count_dict[county] += d[state][county][item_key]['cost($)']
			else:
				count_dict[county] = d[state][county][item_key]['cost($)']


		for key, value in reversed(sorted(item_dict.iteritems(), key=lambda (k,v): (v,k))):
			title = 'N/A'
			if int(tot_fed_cost_for_county) == 0:
				percent = 'N/A'
			else:
				percent = round_format(value, tot_fed_cost_for_county)
				
			#print percent
	
			out_county_dict[county] = {'item': key, 'name': title, 'units': item_unit_dict[key], 'cost_sum': '${:,.2f}'.format(value), 'unit_cost':  '${:,.2f}'.format(value/item_unit_dict[key]), 'county_cost_sum': tot_fed_cost_for_county, 'percent_of_item_cost_for_county': percent }
			#print tot_fed_cost_for_county, 'percent_of_county': 100* round(value/tot_fed_cost_for_county, 2)
			#print 'Most Expesive Item Total Sum for ', county, ' in State ', state, ': ',key, '(',title ,') at', '${:,.2f}'.format(value), 'est. per unit cost: ', '${:,.2f}'.format(value/item_unit_dict[key])
			break

	for key, value in reversed(sorted(count_dict.iteritems(), key=lambda (k,v): (v,k))):
		out_state_dict[state] = {'counties_meta_data': out_county_dict, 'most_expensive_county': {'county': key, 'cost_sum': '${:,.2f}'.format(value)}, 'state_cost_sum': tot_fed_cost_for_state, 'percent_cost_of_state': round_format(value, tot_fed_cost_for_state)}
		#print 'Most Expesive County Total Sum for State: ', state, ': ',key, ' with ', '${:,.2f}'.format(value)
		break

		
	state_dict[state] = tot_fed_cost_for_state

out_state_sorted_list = []
for key, value in reversed(sorted(state_dict.iteritems(), key=lambda (k,v): (v,k))):
	out_state_sorted_list.append({key: out_state_dict[key]})
	#print 'State: ', key, 'Total Cost of Federal Military Surplus Allocation:', '${:,.2f}'.format(value)


cache_item_dict = dict()
size = 0
query_size = 0
for node in out_state_sorted_list:
	for key, value in node.iteritems():
		county_keys = node[key]['counties_meta_data'].keys()
		for county in county_keys:
			query = node[key]['counties_meta_data'][county]['item']
			if query not in cache_item_dict:
				url = 'http://www.armyproperty.com/nsn/%s/' % (query)
				r = requests.get(url)
				soup = BeautifulSoup(r.text)
				title_unfilt = list(soup.h2.stripped_strings)
				title = title_unfilt[0]

				if not title or title == '' or title == ' ':
					title = 'N/A'

				query_size += 1
				cache_item_dict[query] = title
			else:
				#print 'cache used'
				size += 1
				title = cache_item_dict[query]
			
			#print title
			node[key]['counties_meta_data'][county]['name'] = title

data = json.dumps({'2006-2014-foia-gov-surplus-mil': out_state_sorted_list})
f = open('2006-2014-foia-gov-surplus-mil.json', 'w+')
f.write(data)
f.close()
print 'Url Requests to Cache Used %s percent of time' % (round_format(query_size, size))