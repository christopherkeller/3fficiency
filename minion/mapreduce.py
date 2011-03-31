#!/usr/bin/env python
# encoding: utf-8
"""
mapreduce.py

Created by Christopher Keller on 2011-03-30.
Copyright (c) 2011 3fficiency. All rights reserved.
"""

import sys
import os
import itertools
import string

def map_reduce(i,mapper,reducer):
	intermediate = []
	groups = {}
	
	for (key,value) in i.items():
		intermediate.extend(mapper(key,value))	
	
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



