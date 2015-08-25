# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RiverGIS
Description          : HEC-RAS tools for QGIS
Date                 : January, 2015
copyright            : (C) 2015 by RiverGIS Group
email                : rpasiok@gmail.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""

def getListSlicesBetween(l,s1,s2,withLast):
  r"""getListSlicesBetween -- from list of strings l gets slices between pair of items starting from s1 and s2.
  Slices will contain the ending item starting from s2 if argument withLast is set to True.
  Returns a list: [slices, starting_indices, ending_indices]. Example:
  A = ['Points:',
  '123, 456',
  ....
  '987,654'
  'Lines:',
  '123 456, 789 987, ....']

  getListSlicesBetween(A,'Poin', 'Lin', False)
  ['123, 456',
  ....
  '987,654']
  """
  slices = []
  i = 0
  iS = [] # starting indices
  iE = []
  for line in l: # find starting and ending indices
    if line.startswith(s1):
      iS.append(i)
    if line.startswith(s2):
      iE.append(i)
    i += 1
  i = 0
  for ind in iS: # get the slices
    if withLast:
      slices.append(l[iS[i]+1:iE[i]+1])
    else:
      slices.append(l[iS[i]+1:iE[i]])
    i += 1
  return [slices, iS, iE]


def getLayerExtent(layer, buf=0, hecras=0):
  pExt = layer.extent()
  xmin = pExt.xMinimum()
  xmax = pExt.xMaximum()
  ymin = pExt.yMinimum()
  ymax = pExt.yMaximum()
  if hecras:
    pExtStr = '%.2f, %.2f, %.2f, %.2f' % (xmin-buf, xmax+buf, ymax+buf, ymin-buf)
  else:
    pExtStr = '%.2f, %.2f, %.2f, %.2f' % (xmin-buf, xmax+buf, ymin-buf, ymax+buf)
  return pExtStr

def mylog(logFileName, t1, t2=None, t3=None, t4=None):
  logFile = open(logFileName, "a")
  t = str(time.strftime(timeFormat, time.localtime()))
  if debug:
    t += "\n\t%s" % str(t1)
    if t2:
      t += "\n\t%s" %  str(t2)
      if t3:
        t += "\n\t%s" % str(t3)
        if t4:
          t += "\n\t%s" % str(t4)
    logFile.write( str(t) + "\n")
    logFile.close()

def checkIfRasterSumIsZero(file):
  print 'checking sum ', file
  sum = -1
  infor = processing.runalg("grass:r.info",file,False,False,False,False,False,False,False,False,False,None,None)
  ht = open(infor['html'], "r").readlines()
  for line in ht:
    if line.startswith(' |   Range of data:'):
      sum = float(line.split('max =')[1].split('|')[0])

  if sum < 0.01:
    return True
  else:
    return False



