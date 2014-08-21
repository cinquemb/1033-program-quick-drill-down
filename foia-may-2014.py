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

a = dict()
fips_file_ = 'fips_numbers.csv'
with open(fips_file_, 'r+') as a_ss:
	reader = csv.reader(a_ss, delimiter=',')
	for k, row in enumerate(reader):
		if k > 1:
			state_ = row[0]
			fips_ = int(row[1] + row[2])
			#print fips_
			county_ = row[3].split(' County')[0].upper()
			if ' CITY' in county_:
				county_ = county_.split(' CITY')[0]

			if '.' in county_:
				county_ = re.sub('.', '', county_)

			
			key = state_ + '-' + county_
			a[key] = fips_

			#print 'key: ', key, 'fips: ',fips_

print 'Done Importing Fips Numbers'
voter_file = 'US-presidential-election-results-by-county-2012.csv'
c = dict()
with open(voter_file, 'r+') as v_ss:
	reader = csv.reader(v_ss, delimiter=',')
	for k, row in enumerate(reader):
		if k > 1:
			state_ = row[0]
			fips_ = int(row[3])
			total_votes_ = row[10]
			total_votes_dem_ =row[19]
			total_votes_repub_ = row[31]
			total_votes_lib_ind_ = row[43]

			#print 'State: ', state_, 'County: ',county_, 'Total Votes: ', total_votes_, 'Total Dem', total_votes_dem_, 'Total Rep', total_votes_repub_, 'Total Ind/Lib: ', total_votes_lib_ind_


			c[fips_] = {'total_votes': int(total_votes_), 'percent_dem': round_format(total_votes_dem_,total_votes_), 'percent_repub': round_format(total_votes_repub_,total_votes_), 'percent_ind_lib': round_format(total_votes_lib_ind_,total_votes_)}
			#print c[state_][county_]

print 'Done analyzing voter breakdown, starting Military Surplus Mine'

hit_count = 0
total = 0
d = dict()
temp_dict_count = dict()
with open(file_, 'r+') as f_ss:
	reader = csv.reader(f_ss, delimiter=',')
	for k, row in enumerate(reader):
		if k > 1:
			state_ = row[0]#stat
			county_ = row[1]# county
			#print county_
			if '' == county_:
				county_ = ''
				#print 'missing county for: ', state_
			if ' ' == county_:
				county_ = ''

			if '.' in county_:
				print county_

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

			match_key_fips_ = state_ + '-' + county_

			if match_key_fips_ in a and match_key_fips_ not in temp_dict_count:
				hit_count += 1
				total += 1


			if match_key_fips_ not in temp_dict_count:
				total += 1
				temp_dict_count[match_key_fips_] = 0
			else:
				temp_dict_count[match_key_fips_] += 1

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

percent_hit = round_format(hit_count,total)
print 'County FIPS Hit Percent found in FOIA 1033 data: %' +  str(percent_hit)

#sys.exit()
hit_count = 0
total = 0

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
				
			fips_key_ = state + '-' + county

			#print fips_key_

			if fips_key_ not in a:
				total += 1
				p_v_b = 'N/A'
			else:
				if a[fips_key_] not in c:
					p_v_b = 'N/A'
				else:
					hit_count += 1
					p_v_b = c[int(a[fips_key_])]
				
				total += 1

			out_county_dict[county] = {'item': key, 'name': title, 'units': item_unit_dict[key], 'cost_sum': '${:,.2f}'.format(value), 'unit_cost':  '${:,.2f}'.format(value/item_unit_dict[key]), 'county_cost_sum': tot_fed_cost_for_county, 'percent_of_item_cost_for_county': percent, 'political_voter_breakdown': p_v_b }

			break


	for key, value in reversed(sorted(count_dict.iteritems(), key=lambda (k,v): (v,k))):
		out_state_dict[state] = {'counties_meta_data': out_county_dict, 'most_expensive_county': {'county': key, 'cost_sum': '${:,.2f}'.format(value)}, 'state_cost_sum': tot_fed_cost_for_state, 'percent_cost_of_state': round_format(value, tot_fed_cost_for_state)}
		break

		
	state_dict[state] = tot_fed_cost_for_state

percent_hit = round_format(hit_count,total)
print 'County FIPS Hit Percent found in FOIA 1033 data in Top Counties: %' +  str(percent_hit)

out_state_sorted_list = []
for key, value in reversed(sorted(state_dict.iteritems(), key=lambda (k,v): (v,k))):
	out_state_sorted_list.append({key: out_state_dict[key]})

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