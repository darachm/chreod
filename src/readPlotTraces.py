#!/usr/bin/python3

import os
import numpy as np
import matplotlib.pyplot as plt





traceDir = "./data/traces/"
for traceFile in os.listdir(traceDir):
  if traceFile.endswith(".traces"):
    exs = []
    why = []
    f = open(traceDir+traceFile,'r')
    print(f.readline())
    for line in f:
      lineList = line.split()
      exs.append(float(lineList[1]))
      why.append(float(lineList[0]))
    plt.plot(exs,why)

plt.show()


