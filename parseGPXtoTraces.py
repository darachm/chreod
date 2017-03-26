#!/usr/bin/python3

import os
import xml.etree.ElementTree as ET

tgPre = "{http://www.topografix.com/GPX/1/0}"
gpxDir = "./data/gpx/"
for gpxFile in os.listdir(gpxDir):
  if gpxFile.endswith(".gpx"):
    gpxTree = ET.parse(gpxDir+gpxFile)
    gpxRoot = gpxTree.getroot()
    for track in gpxRoot.iter(tgPre+'trk'):
      f = open("./data/traces/"+
               track.find(tgPre+'name').text+'.tabd','w')
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

