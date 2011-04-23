#!/usr/bin/env python
# encoding: utf-8

"""
mr_status.py

Created by Christopher Keller on 2011-03-30.
Copyright (c) 2011 3fficiency. All rights reserved.
"""

__author__  = [ 'Christopher Keller' ]
__version__ = '0.1'

DB_SCHEMA = 'nventio'
DB_CONFIG = '../common/db.cnf'

import MySQLdb
import sys
from mapreduce import *
	
def connectDB():
	try:
		db = MySQLdb.connect(read_default_file=DB_CONFIG)
	except MySQLdb.Error, e:
		print """Error %d: %s""" % (e.args[0], e.args[1])
		sys.exit (1)
	return db
		
def process():
	db = connectDB()
	c = db.cursor()
	
	if (opt.verbose):
		print """SELECT completed_status FROM status"""

	c.execute("""DELETE FROM histogram""")
	result = c.fetchall()
	
	c.execute("""SELECT user_id,date,completed_status FROM status""")	
	result = c.fetchall()
	for record in result:
		i={}
		i[record[1]]=record[2]
		histogram = map_reduce(i,mapper,reducer)
		for word in histogram:
			SQL = """INSERT INTO histogram(user_id,date,word,frequency) VALUES (%s,%s,%s,%s)"""
			c.execute(SQL,(record[0],record[1],word[0],word[1]))
	c.close()
	db.commit()
	db.close()
			
def main(opt,args):
	"""The main() function that contains our use cases."""
	process()

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
	main(opt,args)
