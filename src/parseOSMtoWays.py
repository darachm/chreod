#!/usr/bin/python3

import os
import xml.etree.ElementTree as ET

from pymongo import MongoClient
client = MongoClient() # this gets us a client to the mongodatabase
                       # make sure to start mongod somewhere, aim at
                       # some custom folder

if 0: # for debugging, this just drops the named database
  client.drop_database('test')

db = client.test # this creates the database
nodes = db.nodes # this creates the nodes collection
waysByNodes = db.waysByNodes # this creates a collection of ways
                             # as they are read in

if 0: # for loading
  db.nodes.create_index( 'id',unique=True )
  db.waysByNodes.create_index( 'id',unique=True )
  osmDir = './data/osm/'
  for osmFile in os.listdir(osmDir):
    if osmFile.endswith('.osm'):
      for event, elem in ET.iterparse(osmDir+osmFile):
        if elem.tag == 'node':
          for subelem in elem.findall('tag'):
            if subelem.attrib['k']=='highway':
              try:
                nodes.insert_one({'id':elem.attrib['id'],
                                  'lon':elem.attrib['lon'],
                                  'lat':elem.attrib['lat']})
              except:
                1
        if elem.tag == 'way':
          thisName = ''
          thisHighway = ''
          for z in elem.findall('tag'):
            if z.attrib['k']=='name':
              thisName = z.attrib['v']
            if z.attrib['k']=='highway':
              thisHighway = z.attrib['v']
          if thisHighway != '':
            wayNodes = []
            for z in elem.findall('nd'):
              wayNodes.append(z.attrib['ref'])
            try:
              waysByNodes.insert_one({'id':elem.attrib['id'],
                                      'ndz':wayNodes,
                                      'name':thisName,
                                      'highway':thisHighway})
            except:
              1
  
if 0: # for counts
  print(str(db.nodes.count())+" nodes")
  print(str(db.waysByNodes.count())+" ways")
#  print(db.ways.count())

if 0: # for printing
  for i in waysByNodes.find({'name':'Nassau Street'}):
    print(i)

if 1: # for updating nodes with streets
  for eachWayByNodes in waysByNodes.find({}):
    for eachNodeIDInWay in eachWayByNodes['ndz']:
      nodes.find_one_and_update({'id':eachNodeIDInWay},
        {'$set':{'wayParent':eachWayByNodes['name']}}) 
  for i in nodes.find({}):
    print(i)

#intersections = db.intersections
#db.intersections.create_index( 'id',unique=True )
#if 1: # for making intersections of ways
#  for i in #eachway:
#    #add to node's hash, key id and value name 
#  for i in #each node hash
#    #if it's intersecting with itself, then merge the two as a new
#    #  document with longer id1+id2
#    #if in multiple roads, then add the intersection to an array of
#    #  these for each way
#
#
#waysByNodes = db.waysByNodes
#db.waysByNodes.create_index( 'id',unique=True )
#if 1: # for making ways
#  for i in waysByNodes.find({'name':'Flushing Avenue'}):
#    
#        waysByNodes[elem.attrib['id']] = [elem.attrib['lon'],
#                                    elem.attrib['lat']]


#      f = open('./data/traces/'+
#               track.find(tgPre+'name').text+'.traces','w')
#      f.write('lat\tlon\tele\tspeed\ttime\n')
#      for trackSegment in track.iter(tgPre+'trkseg'):
#        for measuredPoint in trackSegment.getiterator(tgPre+'trkpt'):
#          f.write(measuredPoint.get('lat')+'\t'+
#                measuredPoint.get('lon')+'\t'+
#                measuredPoint.find(tgPre+'ele').text+'\t'+
#                measuredPoint.find(tgPre+'speed').text+'\t'+
#                measuredPoint.find(tgPre+'time').text+'\n'
#               )
#      f.close()
#
