#!/usr/bin/python3

import argparse # for arguments on the command line
import os # for opening and closing files
import xml.etree.ElementTree as ET # need this to read all this xml

from pymongo import MongoClient # using mongoDB
client = MongoClient() # this gets us a client to the mongodatabase
                       # make sure to start mongod somewhere, aim at
                       # some custom folder

argparser = argparse.ArgumentParser(description='the chreod thingy')
argparser.add_argument('--parseOSM',dest='runMode',
  action='store_const',const='parseOSM', 
  default='help',help='parse OSM to mongodb')
argparser.add_argument('--plotWayNodes',dest='runMode',
  action='store_const',const='plotWayNodes', 
  default='help',help='parse OSM to mongodb')
argparser.add_argument('--dropDB',dest='dropDB',
  action='store_const',const=True, 
  default=False,help='should I drop test database?')
args = argparser.parse_args()
#if bool(args.runMode=='help') and not args.dropDB:
#  argparser.print_help()

import numpy as np
import matplotlib.pyplot as plt

if args.dropDB: # for debugging, this just drops the named database, 
# here that's test
  client.drop_database('test')
  print('Dropped db test')

def main():
  nameOfDatabase = 'test'
  if args.runMode == 'parseOSM':
    osmDir = './data/osm/'
    for osmFile in os.listdir(osmDir):
      if osmFile.endswith('.osm'):
        parseOSMtoMongoDB(osmDir+osmFile,nameOfDatabase)
# next plots points of each wayByNodes
  if args.runMode == 'plotWayNodes':
    for eachWay in client[nameOfDatabase].namedWays.find():
      exs, why = [],[]
      try:
        for eachNodeID in eachWay['ndz']:
          for eachNodeInWay in client[nameOfDatabase].nodes.find({'id':eachNodeID}):
            exs.append(float(eachNodeInWay['lon']))
            why.append(float(eachNodeInWay['lat']))
      except:
        None
      plt.plot(exs,why,marker='o')
    plt.show()

def parseOSMtoMongoDB(osmFilePath,databaseName): 
# this function should take a path to an osm, read it all in, 
# store it as collections, and return the names of those?
  db = client[databaseName] # this creates the database
  nodes = db.nodes # this opens the nodes collection
  waysByNodes = db.waysByNodes # this opens a collection of ways
    # as they are read in
  db.nodes.create_index( 'id',unique=True )
  db.waysByNodes.create_index( 'id',unique=True )
  for event, elem in ET.iterparse(osmFilePath):
    if elem.tag == 'node':
      for subelem in elem.findall('tag'):
        if subelem.attrib['k']=='highway':
          try:
            nodes.insert_one({'id':elem.attrib['id'],
              'lon':float(elem.attrib['lon']),
              'lat':float(elem.attrib['lat'])})
          except:
            1
    if elem.tag == 'way':
      thisName, thisHighway = '',''
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
            'ndz':wayNodes,'name':thisName,'highway':thisHighway})
        except:
          1
# now we've got our two collections open, how many do we have?
  print("Read in "+str(db.nodes.count())+" nodes and "+
    str(db.waysByNodes.count())+" ways")
# test just to see if we got one, and only one
  for i in waysByNodes.find({'name':'Navy Street'}):
    #print(i)
    None
# give each node the name of the way it's a member of
  for eachWayByNodes in waysByNodes.find({}):
    for eachNodeIDInWay in eachWayByNodes['ndz']:
      nodes.find_one_and_update({'id':eachNodeIDInWay},
        {'$push':{'wayParent':eachWayByNodes['name']}}) 
# the below is just to make a unique set of names, but that might
# be problematic, because what if there's some kind of loop, how
# do a preserve order around curves?
  for eachNode in nodes.find({}):
    try:
      eachNode['uniqueWayParents'] = set(eachNode['wayParent'])
    except:
      None
  namedWays = db.namedWays # this opens a collection of named ways
  db.namedWays.create_index( 'name',unique=True )
  for eachNode in nodes.find():
    try:
      for eachParentWay in set(eachNode['wayParent']):
        namedWays.find_one_and_update({'name':eachParentWay},
          {'$push':{'ndz':eachNode['id']}},upsert=True) 
    except:
      None
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
### } parseOSM

# for this one, wait and figure out how to do numpy
tagPre = "{http://www.topografix.com/GPX/1/0}"
gpxDir = "./data/gpx/"
#parseGPX(gpxDir,tagPre)
def parseGPX(gpxDir,tagPre):
  for gpxFile in os.listdir(gpxDir):
    if gpxFile.endswith(".gpx"):
      gpxTree = ET.parse(gpxDir+gpxFile)
      gpxRoot = gpxTree.getroot()
      for track in gpxRoot.iter(tagPre+'trk'):
#        f = open("./data/traces/"+
#                 track.find(tagPre+'name').text+'.traces','w')
#        f.write('lat\tlon\tele\tspeed\ttime\n')
        for trackSegment in track.iter(tagPre+'trkseg'):
          for measuredPoint in trackSegment.getiterator(tagPre+'trkpt'):
            f.write(measuredPoint.get('lat')+'\t'+
                  measuredPoint.get('lon')+'\t'+
                  measuredPoint.find(tagPre+'ele').text+'\t'+
                  measuredPoint.find(tagPre+'speed').text+'\t'+
                  measuredPoint.find(tagPre+'time').text+'\n'
                 )
        f.close()

  

if __name__ == '__main__': # bit from stackoverflow answer
  main()
