import xlrd
import json
import os
import inspect
from os.path import *
import sys
book_hash = {}
cache_name_hash = {}
census_name_to_code = {}
from flask import Flask
from flask import url_for
from flask import request
population_hash = {}

def read_census_data():
	global book_hash
	name_hash = {}
	for x in os.listdir("/Users/quinnjarrell/Desktop/Census Mapper/CensusData/")[1:]:
		book_hash[x]  = xlrd.open_workbook("/Users/quinnjarrell/Desktop/Census Mapper/CensusData/" + x)
		print x
		#print name_hash
		for i in range(len(book_hash[x].sheet_names())):
			sh = book_hash[x].sheet_by_index(i)
			for rownum in range(sh.ncols):
				val = sh.cell(0,rownum).value
				if val[len(val)-1] == 'D':
					#print val
					name_hash[val] = [x,i,rownum]
	print name_hash
	return name_hash
def print_col_vals(col):
	uni = unicode(col)
	path = cache_name_hash[uni]
	sh = book_hash[path[0]].sheet_by_index(path[1])
	loc_num = 0
	for i in sh.col(path[2]):
		loc = str(sh.cell(loc_num,0))
		#print loc[len(loc) - 3:] + " " + str(loc[len(loc) - 3:] == 'IL')
		if loc[len(loc) - 3:] == "IL'":
			print str(sh.cell(loc_num,0).value) + str( i.value)
		loc_num += 1
def track_population(col):
	global population_hash
	uni = unicode(col)
	path = cache_name_hash[uni]
	sh = book_hash[path[0]].sheet_by_index(path[1])
	loc_num = 0
	for i in sh.col(path[2]):
		loc = str(sh.cell(loc_num,0).value)
		#print loc[len(loc) - 2:] + " " + str(i.value)
		#print loc[len(loc) - 3:] + " " + str(loc[len(loc) - 3:] == 'IL')
		if loc[len(loc) - 2:] == "IL":
			name = "#" + str(loc[:len(loc)-4])
			population_hash[name] = i.value
		loc_num += 1
def slice_data(col):
	uni = unicode(col)
	path = cache_name_hash[uni]
	sh = book_hash[path[0]].sheet_by_index(path[1])
	finished_data = []
	loc_num = 0
	for i in sh.col(path[2]):
		loc = str(sh.cell(loc_num,0).value)
		result = loc[len(loc) - 2:] == "IL"
		print loc[len(loc) - 2:] + " " + str(i.value)
		if loc[len(loc) - 2:] == "IL":
			name = "#" + str(loc[:len(loc)-4])
			
			finished_data.append([name,int( i.value)])
		loc_num += 1
	return finished_data
def weight_data(data):
	max_val,min_val = 0,0
	new_max,new_min = 255,0
	scaled_data = []
	print data
	for i in data:
		if i[0] != '#Cook':
			if min_val == 0:
				if percapita:
					min_val = (i[1] / population_hash[i[0]]) * 1000
			if (i[1] / population_hash[i[0]]) * 1000 > max_val:
				if percapita:
					max_val = (i[1] / population_hash[i[0]]) * 1000
			if (i[1] / population_hash[i[0]]) * 1000 < min_val:
				if percapita:
					min_val = (i[1] / population_hash[i[0]]) * 1000
	if max_val > 0 and max_val != min_val:
		for i in data:
			if percapita:
				#print min_val
				#print max_val
				#print (i[1] / population_hash[i[0]]) * 1000
				#print get_new_range(min_val,max_val,0,255,(i[1] / population_hash[i[0]]) * 1000)
				scaled_data.append([i[0], round(get_new_range(min_val,max_val,0,255,(i[1] / population_hash[i[0]]) * 1000))])
			else:
				scaled_data.append([i[0], round(get_new_range(min_val,max_val,0,255,i[1]))])
	return scaled_data

def read_ref_data():
	global census_name_to_code
	book = xlrd.open_workbook('/Users/quinnjarrell/Desktop/Census Mapper/Ref/Mastdata.xls')
	for i in range(len(book.sheet_names())):
		sh = book.sheet_by_index(i)
		for rownum in range(sh.nrows - 1):
			val = str(sh.cell(rownum + 1,0).value)
			key = str(sh.cell(rownum + 1,1).value)
			census_name_to_code[key] = val


def get_new_range(old_min,old_max,new_min,new_max,old_val):
	return ((((new_max - new_min) * (old_val - old_min)) / (old_max - old_min)) + new_min) + 1
def publish_all_categories ():
	global percapita, cache_name_hash
	#cache_name_hash =  read_census_data()
	read_ref_data()
	track_population('POP010210D')
	percapita = True
	for i in census_name_to_code.keys():
		print census_name_to_code[i]
		data = slice_data(census_name_to_code[i])
		weighted = weight_data(data)
		print json.dumps(weighted)
		f = open('/Users/quinnjarrell/Desktop/Census Mapper/static/percapita/' + census_name_to_code[i] +'.json', 'w+')
		f.write(json.dumps(weighted))
		f.close()

html = ""
dir = os.path.abspath(inspect.getsourcefile(publish_all_categories))
dir =  str(os.path.dirname(dir))
print dir
interface = Flask(__name__,static_folder= dir + '/static')
def load_data():
	f = open('/Users/quinnjarrell/Desktop/Census Mapper/PythonData/census_name_to_code.data','r')
	census_name_to_code = pickle.load(f)
	f.close()
	f = open('/Users/quinnjarrell/Desktop/Census Mapper/PythonData/cache_name_hash.data','r')
	cache_name_hash = pickle.load(f)
	f.close
def dump_data():
	f = open('/Users/quinnjarrell/Desktop/Census Mapper/PythonData/cache_name_hash.data','w+')
	pickle.dump(cache_name_hash,f)
	f.close()
	f = open('/Users/quinnjarrell/Desktop/Census Mapper/PythonData/census_name_to_code.data','w+')
	pickle.dump(census_name_to_code,f)
	f.close()

@interface.route("/")
def index():

    return interface.send_static_file('Evolution.html')
@interface.route('/names.json')
def ColNames():
	return interface.send_static_file('CensusColNames.json')
@interface.route('/data/<file>')
def publish_static_json(file):
	return interface.send_static_file(file)
@interface.route('/data/percapita/<file>')
def publish_static_json_percapita(file):
	return interface.send_static_file('percapita/' + file)
if __name__ == "__main__":
	

	#publish_all_categories()
	interface.run(debug=True)
#print os.listdir("./Data/")[1:]