#!/usr/bin/env python

# C.Keller - 03/26/2011
#
#
__author__  = [ 'Christopher Keller' ]
__version__ = '0.1'

DB_SCHEMA = 'nventio'
DB_CONFIG = './db.cnf'

import MySQLdb
import itertools
import string
import sys

def map_reduce(i,mapper,reducer):
	intermediate = []
	for (key,value) in i.items():
		intermediate.extend(mapper(key,value))
	groups = {}
	for key, group in itertools.groupby(sorted(intermediate), lambda x: x[0]):
		groups[key] = list([y for x, y in group])
	return [reducer(intermediate_key,groups[intermediate_key]) for intermediate_key in groups]

def remove_punctuation(s):
	return s.translate(string.maketrans("",""),string.punctuation)

def mapper(input_key,input_value):
	return [(word,1) for word in remove_punctuation(input_value.lower()).split()]
    
def reducer(intermediate_key,intermediate_value_list):
	return (intermediate_key,sum(intermediate_value_list))

def returnCount(wordList,term):
	for word in wordList:
		if word[0] == term:
			return "%s occurs %d times" % (word[0],word[1])
			
def connectDB():
	try:
		db = MySQLdb.connect(read_default_file=DB_CONFIG)
	except MySQLdb.Error, e:
		print """Error %d: %s""" % (e.args[0], e.args[1])
		sys.exit (1)
	return db.cursor()
		
def process(args):
	c = connectDB()
	
	if (opt.verbose):
		print """SELECT completed_status FROM status WHERE user_id = (SELECT id FROM user WHERE user_name='%s')""" % args[0]
	if args[0] == "all":
		c.execute("""SELECT completed_status FROM status""")
	else:
		c.execute("""SELECT completed_status FROM status WHERE user_id = (SELECT id FROM user WHERE user_name='%s')""" % args[0])
	result = c.fetchall()
	i={}
	count=0
	for record in result:
		i[count]=record[0]
		count = count + 1

	if len(args) < 2:
		print sorted(map_reduce(i,mapper,reducer),key=lambda x: x[1],reverse=True)
	else:
		print returnCount(sorted(map_reduce(i,mapper,reducer),key=lambda x: x[1],reverse=True),args[1])

			
def main(opt,args):
	"""The main() function that contains our use cases."""
	process(args)

if __name__ == "__main__":
	"""Parse command line options"""
	from optparse import OptionParser, make_option
	option_list = [
		make_option("-v", dest="verbose", help="verbose output",action="store_true"),
		make_option("-u", dest="infile", help="input nbe file to parse", action="store", type="string"),
		]
	usage = """usage: %prog [options] username term"""
	parser = OptionParser(usage,option_list=option_list)
	(opt, args) = parser.parse_args()
	if len(args) < 1:
		parser.error("incorrect number of arguments")
	main(opt,args)
