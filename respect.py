#!/usr/bin/env python3
"""
RESPECT is a simple tool that ensures that boundaries are respected.
It doesn't care what the boundaries are, or what thy are for.

The idea of RESPECT is that there are items, and groups of items, and 
connections between items. And there are rules about items of which
group may be connected to items of which other group. Each item and
each group is represented by an arbitrary name.
"""
from argparse import ArgumentParser
import logging
import os
import sys
import csv

__author__ = 'Daniel Kinzler'
__version__ = '0.1'
__license__ = 'GPL 2+'

class respect:
	def readGraph( self, filename, exclude = [], require = None ):
		with open(filename) as csvfile:
			graph = {}
			reader = csv.reader(csvfile, delimiter=',')

			for row in reader:
				subj = row[0]
				obj = row[1]
				# todo: filter by tags
				
				if not subj in graph:
					graph[subj] = []
				
				graph[subj].append( obj )

			return graph;
			
	def inverseGraph (self, graph ):
		inverse = {}
		for subj in graph:
			for obj in graph[subj]:
				if not obj in inverse:
					inverse[obj] = []
					
				inverse[obj].append( subj )
		return inverse

	def load( self, relationsFile, membershipFile, rulesFile ):
		self.relations = self.readGraph( relationsFile )
		self.groups = self.readGraph( membershipFile )
		self.members = self.inverseGraph( self.groups )
		self.rules = self.readGraph( rulesFile )

		self.registerUngrouped()
		
	def registerUngrouped( self ):
		self.members['*'] = []
		for subj in self.relations:
			if not subj in self.groups:
				self.groups[subj] = [ '*' ]
				self.members['*'].append( subj )
			
			for obj in self.relations[subj]:
				if not obj in self.groups:
					self.groups[obj] = [ '*' ]
					self.members['*'].append( obj )

	def check( self, subj, obj ):
		if subj == obj:
			return []
		
		subjGroups = self.groups[subj]
		objGroups = self.groups[obj]
		
		violations = []
		for subjGroup in self.groups[subj]:
			for objGroup in self.groups[obj]:
				if subjGroup == objGroup:
					continue
				
				if not subjGroup in self.rules:
					violations.append( ( subjGroup, objGroup ) )
				elif not objGroup in self.rules[subjGroup]:
					violations.append( ( subjGroup, objGroup ) )
		
		return violations
		
	def listBadRelations( self ):
		for subj in self.relations:
			for obj in self.relations[subj]:
				bad = self.check( subj, obj )
				
				if bad:
					print( subj, obj, bad[0][0], bad[0][1] )
	
	def main( self, argv ):

		epilog = 'system (default) encoding: {}'.format(sys.getdefaultencoding())
		parser = ArgumentParser(
			usage='%(prog)s [options] <relations> <membership> <rules>',
			description=__doc__, epilog=epilog,
			prog=os.path.basename( sys.argv[0] )
		)

		parser.add_argument('--version', action='version', version=__version__)
		parser.add_argument('relations', action='store')
		parser.add_argument('membership', action='store')
		parser.add_argument('rules', action='store')
		
		args = parser.parse_args( argv[1:] )
		
		self.load( args.relations, args.membership, args.rules )
		
		self.listBadRelations()
	
if __name__ == '__main__':
	respect = respect()
	respect.main( sys.argv )
