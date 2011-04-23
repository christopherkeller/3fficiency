#!/usr/bin/env python
# encoding: utf-8

"""
edge.py
# http://www.codeproject.com/KB/database/Modeling_DAGs_on_SQL_DBs.aspx

Created by Christopher Keller on 2011-04-12.
Copyright (c) 2011 3fficiency. All rights reserved.
"""
__author__  = [ 'Christopher Keller' ]
__version__ = '0.1'


import sys
from edge_api import *
import csv
def process(filename):
	db = connectDB()
	c = db.cursor()

	# Assume filename is in the following format: startVertext, endVertex, graphTag
	data = csv.reader(open(filename,"rb"))
	for line in data:
			insertEdge(line[0],line[1],line[2],c)
			
	c.close()
	db.commit()
	db.close()
			
def main(opt,args):
	"""The main() function that contains our use cases."""
	process(args[0])

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
