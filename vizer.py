#!/usr/bin/python3

import os # for opening and closing files
from pymongo import MongoClient # using mongoDB
client = MongoClient() # this gets us a client to the mongodatabase
                       # make sure to start mongod somewhere, aim at
                       # some custom folder
import numpy as np
import matplotlib.pyplot as plt

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


