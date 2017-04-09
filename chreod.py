#!/usr/bin/python3

import argparse # for arguments on the command line
import os # for opening and closing files
import xml.etree.ElementTree as ET # need this to read all this xml
import sys # for simply exiting

from pymongo import MongoClient # using mongoDB
client = MongoClient() # this gets us a client to the mongodatabase
                       # make sure to start mongod somewhere, aim at
                       # some custom folder

argparser = argparse.ArgumentParser(description='\
The chreod thingy. Takes maps, traces, and turns them into a \
database that we can use to start looking at travel times through \
network.')

argparser.add_argument('--parseOSM',dest='parseOSM',
  action='store_const',const=True,default=False,
  help='--parseOSM Read in ./data/osm files stick them in a mongodb,\
    but only if not already defined by OSM node/way ID.')
argparser.add_argument('--parseGPX',dest='parseGPX',
  action='store_const',const=True,default=False,
  help='--parseGPX Read in ./data/GPX files stick them in a mongodb,\
    but only if not already defined by traveler:date-time')
argparser.add_argument('--connectOSM',dest='connectOSM',
  action='store_const',const=True,default=False,
  help='--connectOSM This takes the OSM data, uses ways (later \
    proximity) to detect node connections, and labels network \
    segments.')
argparser.add_argument('--propogateLabels',dest='propogateLabels',
  action='store_const',const=True,default=False,
  help='--propogateLabels')
argparser.add_argument('--plotDiag',dest='plotDiagnostic',
  action='store_const',const=True, 
  default=False,help='should I make a diagnostic plot? nodes, groupd and colored by segments')
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
  if args.parseOSM:
    osmDir = './data/osm/'
    for osmFile in os.listdir(osmDir):
      if osmFile.endswith('.osm'):
        parseOSMtoMongoDB(osmDir+osmFile,nameOfDatabase)
  if args.connectOSM:
    connectOSM(nameOfDatabase)
  if args.propogateLabels:
    propogateLabels(nameOfDatabase)
# next plots points of each wayByNodes
  if args.plotDiagnostic:
    print("gonna try to plot diagnostic by label")
    allLabels = set()
    for eachNode in client[nameOfDatabase].nodes.find():
      allLabels.add(eachNode['label'])
#THIS IS SET TO DIAGNOSE
    for eachLabel in [15]:#range(16,16):#allLabels:
      for eachNode in client[nameOfDatabase].nodes.find({'label':eachLabel}):
        exs, why, nextNodez = [],[],[]
        try:
          exs.append(float(eachNode['lon']))
          why.append(float(eachNode['lat']))
#THIS IS BUSTED, I SHOULD LEARN NUMPY SO I CAN PLOT THESE
#LINE SEGMENTS BY COLOR TO DIAGNOSE WHT THE COLOR LABEL THING
#AIN'T WORKING
          for eachSubNodeID in eachNode['nextNode']:
            eachSubNodeID.find_one({'id',eachSubNodeID})
            nextNodez.append((eachSubNodeID['lon'],
              eachSubNodeID['lat']))
        except:
          None
        print(nextNodez)
      plt.plot(exs,why,marker='o')
    plt.show()

###DOES THIS ACTUALLY OVERWRITE THE DATABASE?
###REWRITE TO USE BULK INSERTS
def parseOSMtoMongoDB(osmFilePath,databaseName): 
    # this function should take a path to an osm, read it all in, 
    # store it as collections, and return the names of those?
  db = client[databaseName] # this accesses the database
  nodes = db.nodes # this opens the nodes collection, new if not there
  ways = db.ways # this opens a collection of ways, new if not there,
    # as they are read in
  db.nodes.create_index('id',unique=True) # this makes an index
  db.ways.create_index('id',unique=True) # so that it's unique by id
  print("Parsing OSM XML to nodes and ways")
  for event, elem in ET.iterparse(osmFilePath): # open xml as iter
    if elem.tag == 'node': # we only want the nodes...
      for subelem in elem.findall('tag'): # ...that are tagged...
        if subelem.attrib['k']=='highway': # ...as highway nodes.
          try: # this is to catch any weird errors, nodes w/ lat lon
            nodes.insert_one({'id':elem.attrib['id'],
              'lon':float(elem.attrib['lon']),
              'lat':float(elem.attrib['lat']),
              'label':None,'labelPropogated':False,
              'nextNode':[],'prevNode':[]})
          except:
            1
    if elem.tag == 'way': # next, ways
      thisName, thisHighway = '','' # make these blank
      for z in elem.findall('tag'): # for all tags...
        if z.attrib['k']=='name': # grab the way name
          thisName = z.attrib['v']
        if z.attrib['k']=='highway': # and if it's a highway
          thisHighway = z.attrib['v']
      if thisHighway != '': # if it's a highway
        wayNodes = [] # init
        for z in elem.findall('nd'): # for all nodes in the way,
          # and that's in order of the document
          wayNodes.append(z.attrib['ref']) # append in order
          nodes.find_one_and_update({'id':z.attrib['ref']},
            {'$push':{'parentWays':elem.attrib['id']}}) 
        try: # to catch things without defined hash
          ways.insert_one({'id':elem.attrib['id'],'label':None,
            'childNodes':wayNodes,
            'name':thisName,'highway':thisHighway})
        except:
          1
  print("Read in "+str(db.nodes.count())+" nodes and "+ 
    str(db.ways.count())+" ways") # now we've got our two 
      # collections open, how many do we have?

def connectOSM(databaseName): 
    # this function should connect all the nodes
  db = client[databaseName] # this accesses the database
  nodes = db.nodes # this opens the nodes collection
  ways = db.ways # this opens a collection of ways
#TEST IF THEY EXIST
  print("Connecting all nodes in ways")
  for eachWay in ways.find({}):
    if len(eachWay['childNodes']) > 1:
      for listIndex in range(0,len(eachWay['childNodes'])):
        if listIndex == 0:
#IMPLEMENT SOME WAY OF UNIQUIFYING THESE, SO NO REDUNDANCY OF NEXT OR PREVIOUS NODES
          nodes.find_one_and_update(
            {'id': eachWay['childNodes'][listIndex]},
            {'$push':
              {'nextNode':eachWay['childNodes'][listIndex+1]}
            }) 
        elif listIndex == len(eachWay['childNodes'])-1:
          nodes.find_one_and_update(
            {'id': eachWay['childNodes'][listIndex]},
            {'$push':
              {'prevNode':eachWay['childNodes'][listIndex-1]}
            }) 
        else:
          nodes.find_one_and_update(
            {'id': eachWay['childNodes'][listIndex]},
            {'$push':
              {'nextNode':eachWay['childNodes'][listIndex+1]},
            }) 
          nodes.find_one_and_update(
            {'id': eachWay['childNodes'][listIndex]},
            {'$push':
              {'prevNode':eachWay['childNodes'][listIndex-1]},
            }) 


def propogateLabels(databaseName): 
    # this function propogate labels
  db = client[databaseName] # this accesses the database
  nodes = db.nodes # this opens the nodes collection
  ways = db.ways # this opens a collection of ways
#TEST IF THEY EXIST
  print("Propogating labels between nodes in database, to identify\
    connected components")
  nodes.update_many({},{'$set':{'label':None}})
#  for eachNode in nodes.find():
#    print(eachNode['label'])
  counter = 1
  for eachNode in nodes.find():
    try:
      if nodes.find_one({'id':eachNode['id']})['label'] != None:
        continue 
    except:
      continue
    currentLabel = counter#eachNode['id']
    counter += 1
    nodes.update_one({'id':eachNode['id']},
      {'$set':{'label':currentLabel}})
    labelingQueue = [eachNode['id']]
    while len(labelingQueue) > 0:
#      print(labelingQueue)
      currentNodeID = nodes.find_one({'id':labelingQueue.pop()})['id']
      neighborIDList = nodes.find_one({'id':currentNodeID})['nextNode']+nodes.find_one({'id':currentNodeID})['prevNode']
#      print(neighborIDList)
      for neighborNodeID in set(neighborIDList):
        try:
          if nodes.find_one({'id':neighborNodeID})['label'] == None:
            nodes.update_one({'id':neighborNodeID},
              {'$set':{'label':currentLabel}})
            labelingQueue.append(neighborNodeID)
          else:
            continue
        except:
          continue
#      print()
#  for eachNode in nodes.find():
#    print(eachNode['label'])#['id']+" "+eachNode['label'])
      
  
    
# make sure to convert lat lon to meters when done, updating all OSM
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
