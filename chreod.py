#!/usr/bin/python3

import os # for opening and closing files
import xml.etree.ElementTree as ET # need this to read all this xml

from pymongo import MongoClient # using mongoDB
client = MongoClient() # this gets us a client to the mongodatabase
                       # make sure to start mongod somewhere, aim at
                       # some custom folder
if 0: # for debugging, this just drops the named database, here
      # that's test
  client.drop_database('test')

# read in command line arguments
# 

import numpy as np
import matplotlib.pyplot as plt

def main():
  nameOfDatabase = 'test'
  if 1:
    osmDir = './data/osm/'
    for osmFile in os.listdir(osmDir):
      if osmFile.endswith('.osm'):
        parseOSMtoMongoDB(osmDir+osmFile,nameOfDatabase)
# next plots points of each wayByNodes
  if 0:
    for eachWay in client[nameOfDatabase].waysByNodes.find():
      exs, why = [],[]
      for eachNodeID in eachWay['ndz']:
        for eachNodeInWay in client[nameOfDatabase].nodes.find({'id':eachNodeID}):
          exs.append(float(eachNodeInWay['lon']))
          why.append(float(eachNodeInWay['lat']))
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
    print(i)
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
      print(eachNode['uniqueWayParents'])
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

def parseGPX():
  tgPre = "{http://www.topografix.com/GPX/1/0}"
  gpxDir = "./data/gpx/"
  for gpxFile in os.listdir(gpxDir):
    if gpxFile.endswith(".gpx"):
      gpxTree = ET.parse(gpxDir+gpxFile)
      gpxRoot = gpxTree.getroot()
      for track in gpxRoot.iter(tgPre+'trk'):
        f = open("./data/traces/"+
                 track.find(tgPre+'name').text+'.traces','w')
        f.write('lat\tlon\tele\tspeed\ttime\n')
        for trackSegment in track.iter(tgPre+'trkseg'):
          for measuredPoint in trackSegment.getiterator(tgPre+'trkpt'):
            f.write(measuredPoint.get('lat')+'\t'+
                  measuredPoint.get('lon')+'\t'+
                  measuredPoint.find(tgPre+'ele').text+'\t'+
                  measuredPoint.find(tgPre+'speed').text+'\t'+
                  measuredPoint.find(tgPre+'time').text+'\n'
                 )
        f.close()


def plotTraces():
  import numpy as np
  import matplotlib.pyplot as plt
#  traceDir = "./data/traces/"
#  for traceFile in os.listdir(traceDir):
#    if traceFile.endswith(".traces"):
#      exs = []
#      why = []
#      f = open(traceDir+traceFile,'r')
#      print(f.readline())
#      for line in f:
#        lineList = line.split()
#        exs.append(float(lineList[1]))
#        why.append(float(lineList[0]))
#      plt.plot(exs,why)
#  plt.show()
  

if __name__ == '__main__': # bit from stackoverflow answer
  main()
