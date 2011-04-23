#!/usr/bin/env python
# encoding: utf-8

"""
edge_api.py
# http://www.codeproject.com/KB/database/Modeling_DAGs_on_SQL_DBs.aspx

Created by Christopher Keller on 2011-04-18.
Copyright (c) 2011 3fficiency. All rights reserved.
"""
__author__  = [ 'Christopher Keller' ]
__version__ = '0.1'

DB_CONFIG = '../common/db.cnf'

import MySQLdb

def connectDB():
	try:
		db = MySQLdb.connect(read_default_file=DB_CONFIG)
	except MySQLdb.Error, e:
		print """Error %d: %s""" % (e.args[0], e.args[1])
		sys.exit (1)
	return db

def insertEdge(StartVertexId, EndVertexId, source, c):

	c.execute("""SELECT id FROM graph WHERE start_vertex='%s' AND end_vertex='%s' and hops = 0""" % (StartVertexId,EndVertexId))
	if c.fetchone():
		print """NO-OP: duplicate insert"""
		return 0
	if StartVertexId == EndVertexId:
		print """ERROR: circular dependency"""
		return 0
	c.execute("""SELECT id FROM graph WHERE start_vertex=end_vertex AND end_vertex=start_vertex""")
	if c.fetchone():
		print """ERROR: circular dependency"""
		return 0

	# Actual insert
	SQL = """INSERT INTO graph (start_vertex,end_vertex,hops,source) VALUES (%s,%s,%s,%s)"""
	c.execute(SQL,(StartVertexId,EndVertexId,0,source))
	c.execute("""UPDATE graph SET entry_edge_id=%s,direct_edge_id=%s,exit_edge_id=%s
		WHERE id=%s""" % (c.lastrowid,c.lastrowid,c.lastrowid,c.lastrowid))
	
	# StartVertexId's incoming edges to EndVertexId
	c.execute("""SELECT id,start_vertex,hops FROM graph WHERE end_vertex='%s'""" % (StartVertexId))	
	result = c.fetchall()
	for record in result:
		SQL = """INSERT INTO graph (entry_edge_id,direct_edge_id,exit_edge_id,start_vertex,end_vertex,hops,source)
			VALUES (%s,%s,%s,%s,%s,%s,%s)"""
		c.execute(SQL,(record[0],record[0],record[0],record[1],EndVertexId,record[2]+1,source))
	
	# StartVertexId to EndVertexId's outgoing edges
	c.execute("""SELECT id,end_vertex,hops FROM graph WHERE start_vertex='%s'""" % (EndVertexId))
	result = c.fetchall()
	for record in result:
		SQL = """INSERT INTO graph (entry_edge_id,direct_edge_id,exit_edge_id,start_vertex,end_vertex,hops,source)
			VALUES (%s,%s,%s,%s,%s,%s,%s)"""
		c.execute(SQL,(record[0],record[0],record[0],StartVertexId,record[1],record[2]+1,source))	

	# StartVertexId's incoming edges to end vertex of EndVertexId's outgoing eges
	c.execute("""SELECT a.id,b.id,a.start_vertex,b.end_vertex,a.hops,b.hops FROM graph a CROSS JOIN graph b
		WHERE a.end_vertex='%s' AND b.start_vertex='%s'""" % (StartVertexId, EndVertexId))

	result = c.fetchall()
	for record in result:
		SQL = """INSERT INTO graph (entry_edge_id,direct_edge_id,exit_edge_id,start_vertex,end_vertex,hops,source)
			VALUES (%s,%s,%s,%s,%s,%s,%s)"""
		c.execute(SQL,(record[0],id,record[1],record[2],record[3],record[4]+record[5]+1,source))	
	
	return 1

def deleteEdge(VertexId, c):
	pass