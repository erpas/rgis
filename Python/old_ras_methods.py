# -*- coding: utf-8 -*-

"""
    ras2mike - konwerter plików HEC-RAS GIS -> Mike 11
    
    Autor: Radoslaw Pasiok, radoslaw.pasiok@imgw.pl
    
    W narzędziach wykorzystano prace:
           - vector.py (Josh English)
           - Ramer-Douglas-Peucker simplification (Dmitri Lebedev)

    
    Ten plik jest częścią mikeToolBox.

    mikeToolBox jest wolnym oprogramowaniem; możesz go rozprowadzać 
    dalej i/lub modyfikować na warunkach Powszechnej Licencji Publicznej
    GNU, wydanej przez Fundację Wolnego Oprogramowania - według wersji 3
    tej Licencji lub (według twojego wyboru) którejś z późniejszych 
    wersji.

    mikeToolBox rozpowszechniany jest z nadzieją, iż będzie on
    użyteczny - jednak BEZ JAKIEJKOLWIEK GWARANCJI, nawet domyślnej
    gwarancji PRZYDATNOŚCI HANDLOWEJ albo PRZYDATNOŚCI DO OKREŚLONYCH
    ZASTOSOWAŃ. W celu uzyskania bliższych informacji sięgnij do
    Powszechnej Licencji Publicznej GNU.

    Z pewnością wraz z mikeToolBox otrzymałeś też egzemplarz
    Powszechnej Licencji Publicznej GNU (GNU General Public License);
    jeśli nie, odwiedź <http://www.gnu.org/licenses/>.
    
    
    This file is part of mikeToolBox.

    mikeToolBox is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    mikeToolBox is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with mikeToolBox.  If not, see <http://www.gnu.org/licenses/>.
    
"""

import arcpy
from os import path
import string
import datetime
from math import sqrt
from vector import *
from rdp import *
from simplifyXSecDef import *
from numpy import float as nfloat

time_format = "%Y-%m-%d %H:%M:%S"

debug = 1

def uniqKeepOrder(alist):
  """removes duplicates, keeps elements order
  """
  set = {}
  return [set.setdefault(e,e) for e in alist if e not in set]



def pullElems(l,s1,s2,withLast):
  r"""pullElems -- wydziela z listy elementy zawarte pomiedzy
  elementam rozpoczynajacym (s1) i konczacym (s2) - element konczacy
  moze zostac wlaczony do listy poprzez ustawienie argumentu
  withLast = True
  """
  newList = []
  points = []
  i = 0
  iS = []
  iE = []

  for line in l: # znajdz indeksy poczatku i konca potrzebnych danych
    if line.startswith(s1):
      iS.append(i)
    if line.startswith(s2):
      iE.append(i)
    i += 1

  i = 0 

  for ind in iS: # wytnij dane 
    if withLast:
      newList.append(l[iS[i]+1:iE[i]+1])
    else:
      newList.append(l[iS[i]+1:iE[i]])
    i += 1

  return newList



def afterColon(text):
  """Zwraca czesc stringa za dwukropkiem. Obcina poczatkowa i koncowa spacje.
  """
  return string.strip( string.split(text,":")[1] )



  
class gisHeader:
  
  def __init__(self,headerLines):
    
    for row in headerLines[0]:
    
      if row.startswith("DTM TYPE:"):
        self.dtmType = afterColon(row)
      
      if row.startswith("DTM:"):
        self.dtm = afterColon(row)
      
      if row.startswith("STREAM LAYER:"):
        self.streamLayer = afterColon(row)
      
      if row.startswith("NUMBER OF REACHES:"):
        self.numReaches = afterColon(row)
        
      if row.startswith("CROSS-SECTION LAYER:"):
        self.xSecLayer = afterColon(row)
      
      if row.startswith("NUMBER OF CROSS-SECTIONS:"):
        self.numXSections = afterColon(row)
      
      if row.startswith("MAP PROJECTION:"):
        self.mapProjection = afterColon(row)

      if row.startswith("PROJECTION ZONE:"):
        self.projectionZone = afterColon(row)
        
      if row.startswith("DATUM:"):
        self.datum = afterColon(row)
      
      if row.startswith("VERTICAL DATUM:"):
        self.verticalDatum = afterColon(row)
      
      if row.startswith("XMIN:"):
        if string.strip(afterColon(row)):
          self.xMin = nfloat(afterColon(row))
        else:
          self.xMin = 0.
          
      if row.startswith("YMIN:"):
        if string.strip(afterColon(row)):
          self.yMin = nfloat(afterColon(row))
        else:
          self.yMin = 0.
            
      if row.startswith("XMAX:"):
        if string.strip(afterColon(row)):
          self.xMax = nfloat(afterColon(row))
        else:
          self.xMax = 1000000.
      
      if row.startswith("YMAX:"):
        if string.strip(afterColon(row)):
          self.yMax = nfloat(afterColon(row))
        else:
          self.yMax = 1000000.
      
      if row.startswith("UNITS:"):
        self.units = afterColon(row)
    
    self.numProfiles = 0
    self.profileNames = []
    
    if debug:
      
      arcpy.AddMessage("DTM TYPE: %s" % self.dtmType)
      arcpy.AddMessage("DTM: %s" % self.dtm)
      arcpy.AddMessage("STREAM LAYER: %s" % self.streamLayer)
      arcpy.AddMessage("NUMBER OF REACHES: %s" % self.numReaches)
      arcpy.AddMessage("CROSS-SECTION LAYER: %s" % self.xSecLayer)
      arcpy.AddMessage("NUMBER OF CROSS-SECTIONS: %s" % self.numXSections)
      arcpy.AddMessage("MAP PROJECTION: %s" % self.mapProjection)
      arcpy.AddMessage("PROJECTION ZONE: %s" % self.projectionZone)
      arcpy.AddMessage("DATUM: %s" % self.datum)
      arcpy.AddMessage("VERTICAL DATUM: %s" % self.verticalDatum)
      arcpy.AddMessage("XMIN: %s" % self.xMin)
      arcpy.AddMessage("YMIN: %s" % self.yMin)
      arcpy.AddMessage("XMAX: %s" % self.xMax)
      arcpy.AddMessage("YMAX: %s" % self.yMax)
      arcpy.AddMessage("UNITS: %s" % self.units)
    
  def getExportHeader(self):
    
    t = "\nBEGIN HEADER:\n"
    t += "  UNITS: %s\n" % self.units
    t += "  DTM TYPE: %s\n" % self.dtmType
    t += "  DTM: %s\n" % self.dtm
    t += "  STREAM LAYER: %s\n" % self.streamLayer
    t += "  CROSS-SECTION LAYER: %s\n" % self.xSecLayer
    t += "  MAP PROJECTION: %s\n" % self.mapProjection
    t += "  PROJECTION ZONE: %s\n" % self.projectionZone
    t += "  DATUM: %s\n" % self.datum
    t += "  VERTICAL DATUM: %s\n" % self.verticalDatum
    t += "  BEGIN SPATIALEXTENT:\n"
    t += "    XMIN: %.2f\n" % self.xMin
    t += "    YMIN: %.2f\n" % self.yMin
    t += "    XMAX: %.2f\n" % self.xMax
    t += "    YMAX: %.2f\n" % self.yMax
    t += "  END SPATIALEXTENT:\n"
    t += "  NUMBERS OF PROFILES: %s\n" % self.numProfiles
    t += "  PROFILE NAMES:\n"
    for pn in self.profileNames:
      t += "    %s\n" % pn
    t += "  NUMBER OF REACHES: %s\n" % self.numReaches
    t += "  NUMBER OF CROSS-SECTIONS: %s\n" % self.numXSections
    t += "END HEADER:\n"
    return t



class centerLinePoint:
  
  def __init__(self,x,y,z,id):
    self.x = x
    self.y = y
    self.z = z
    self.id = id
    self.userDefChainage = False
    self.chainage = 0
  
  def getRASEndpoint(self):
    if self.z is not None:
      return "  ENDPOINT:%.2f, %.2f, %.2f, %i\n" % (self.x,self.y,self.z,self.id)
    else:
      return "  ENDPOINT:%.2f, %.2f, %s, %i\n" % (self.x,self.y,self.z,self.id)
  
  def getMikePoint(self):
    return "      point = %i, %.2f, %.2f, %i, %.2f, %i\n" \
            % (self.id,self.x,self.y,self.userDefChainage,self.chainage,0)

  
  def getRASCenterlinePoint(self):
    t = "  %.2f, %.2f, " % (self.x,self.y,)
    
    if self.z is not None:
      t += "%.2f, " % self.z
    else:
      t += ", "
    
    if self.id is not None:
      t += "%i\n" % self.id
    else:
      t += "\n"
    
    return t


    
class cutLinePoint:
  
  def __init__(self,x,y):
    self.x = x
    self.y = y
  
  def getPoint(self):
    return "      %.2f, %.2f\n" % (self.x,self.y)


    
class surfaceLinePoint:
  
  def __init__(self,x,y,z,m=None,frac=None,code=None):
    self.x = x
    self.y = y
    self.z = z
    self.m = m
    self.frac = frac
    self.code = code
  
  def getPoint(self):
    return "      %.2f, %.2f, %.2f\n" % (self.x,self.y,self.z)
  
  def getMikePoint(self):
    return "  %.2f   %.2f   1.000     %s     0     0.000     0\n" \
    % (self.m,self.z,(self.code if self.code else "<#0>"))


class reach:
    
  def __init__(self,streamId,reachId,fromPt,toPt,centerLine=[]):
      
    self.streamId = streamId
    self.reachId = reachId
    self.fromPt = fromPt
    self.toPt = toPt
    self.centerLine = centerLine
    
    
    
class xSection:
    
  def __init__(self,streamId,reachId,station):
      
    self.streamId = streamId
    self.reachId = reachId
    self.station = station
    self.nodeName = ""
    self.bankPositions = None
    self.reachLengths = ""
    self.nValues = ""
    self.leveePositions = ""
    self.ineffectivePositions = ""
    self.blockedPositions = ""
    self.cutLine = None
    self.cutLineLength = None
    self.surfaceLine = None
    
    
    
class rasGis:
  
  def __init__(self, filename):
  
    self.filename = filename
    self.linesDirty = open(self.filename, 'r')
    
    # all lines of the import file, stripped
    self.lines = [line.strip() for line in self.linesDirty]
    # lines of HEADER section
    self.headerLines = pullElems(self.lines, "BEGIN HEADER:", "END HEADER:", 0)
    # lines of the whole STREAM-NETWORK section
    self.streamNetworkSection = pullElems(self.lines, "BEGIN STREAM NETWORK:", "END STREAM NETWORK:", 0)
    # lines of the CROSS-SECTIONS section
    self.xSectionsSection = pullElems(self.lines, "BEGIN CROSS-SECTIONS:", "END CROSS-SECTIONS:", 0)
    # a list of reaches lines
    self.streamNetworkItems = pullElems(self.streamNetworkSection[0], "REACH:", "END:", 1)
    # a list of cross-sections lines
    self.xSectionsItems = pullElems(self.xSectionsSection[0], "CROSS-SECTION:", "END:", 1)
    # reaches endpoints 
    self.endpoints = []

    # list of reaches
    self.reaches = []

    # list of cross-sections
    self.xSections = []
    
    # HEADER ATTR EXTRACTION ---------------------------
    self.header = gisHeader(self.headerLines)

    
    # STREAM-NETWORK EXTRACTION ------------------------
    
    # endpoints
    streamEndPointsLines = pullElems(self.lines, "BEGIN STREAM NETWORK:", "REACH:", 0)[0]
    maxPointId = 0
    
    for line in streamEndPointsLines:
      
      if not line.startswith("ENDPOINT"): # continue to next if it doesnt start with "ENDPOINT"
        continue
      
      # make a list of point attributes, if an attr is empty, insert a None
      newEndPt = [(el if string.strip(el) is not "" else None) for el in string.split(afterColon(line),",")]
      
      # if an attribute is not empty, convert it to float
      x,y,z,id =  [(nfloat(el) if el is not None else None) for el in newEndPt]
      
      if not id:
        
        print "\n\n\n\n Endpoint has no Id - check the input file \n\n\n\n\n"
      
      else: 
        
        # add a new point class instance to current center line
        self.endpoints.append(centerLinePoint(x,y,z,int(id)))
      
    for pt in self.endpoints:
      maxPointId = max(maxPointId, pt.id)
    
    
    for stream in self.streamNetworkItems:
      
      # centerline of a stream
      centerLine = []
      centerLineItems = pullElems(stream, "CENTERLINE:", "END:", 0)[0]
      
      for row in centerLineItems:
        
        # make a list of point attributes, if an attr is empty, insert a None
        # print row
        pt = [(el if string.strip(el) is not "" else None) for el in string.split(row,",")]
        
        # if an attribute is not empty, convert it to float
        x,y,z,id =  [(nfloat(el) if el is not None else None) for el in pt]
        
        if not id:
        
          id = maxPointId
          maxPointId += 1
        
        # add a new point class instance to current center line
        # centerLine.append(centerLinePoint(x,y,z,(int(id) if id is not None else None)))
        centerLine.append(centerLinePoint(x,y,z,int(id)))
      
      for row in stream:
      
        if row.startswith("STREAM ID:"):
          streamId = afterColon(row)
        
        if row.startswith("REACH ID:"):
          reachId = afterColon(row)
        
        if row.startswith("FROM POINT:"):
          fromPt = centerLine[0]
          fromPt.id = int( string.split(row,":")[1] )
          
        if row.startswith("TO POINT:"):
          toPt = centerLine[-1]
          toPt.id = int( string.split(row,":")[1] )
      
      self.reaches.append(reach(streamId,reachId,fromPt,toPt,centerLine))
      
      del streamId, reachId, fromPt, toPt, centerLine


    # CROSS-SECTION EXTRACTION ------------------------
    
    for xs in self.xSectionsItems:

      nValues = pullElems(xs, "NVALUES:", "LEVEE POSITIONS:", 0)
      leveePositions = pullElems(xs, "LEVEE POSITIONS:", "INEFFECTIVE POSITIONS:", 0)
      ineffectivePositions = pullElems(xs, "INEFFECTIVE POSITIONS:", "BLOCKED POSITIONS:", 0)
      blockedPositions = pullElems(xs, "BLOCKED POSITIONS:", "CUT LINE:", 0)
      
      # if debug:
        # info = "XS:\n\n%s\n\n" % (xs)
        # arcpy.AddMessage(info)

      
      for line in xs:
      
        if line.startswith("STREAM ID:"):
          streamId = afterColon(line)
        
        if line.startswith("REACH ID:"):
          reachId = afterColon(line)
        
        if line.startswith("STATION:"):
          # arcpy.AddMessage(line)
          st = afterColon(line)
          # arcpy.AddMessage(st)
          # jesli znajdziesz jakas liczbe w notacji naukowej, zamien ja na float
          station = nfloat(st)
          # arcpy.AddMessage(station)
          
        if line.startswith("NODE NAME:"):
          nodeName = afterColon(line)
          
        if line.startswith("BANK POSITIONS:"):
          a = string.strip( string.split(afterColon(line),",")[0] )
          b = string.strip( string.split(afterColon(line),",")[1] )
          if not a == "" and not b == "":
            bankPositions = [nfloat(string.strip(el)) for el in string.split(afterColon(line),",")]
          else:
            t = "\n\nPrzekroj %s - %s - %.3f nie ma okreslonych brzegow - popraw to!\n\n" % (streamId, reachId, station)
            arcpy.AddMessage(t)
            raise SystemExit(0)
            
        if line.startswith("REACH LENGTHS:"):
          reachLengths = line
      
      tempXs = xSection(streamId,reachId,station)
      tempXs.nodeName = nodeName
      tempXs.bankPositions = bankPositions
      tempXs.reachLengths = reachLengths
      tempXs.nValues = nValues
      
      if debug:
        info = "Rozpoznaje: StreamId: %s, reachId: %s, station: %s" % (streamId,reachId,station)
        arcpy.AddMessage(info)
      
      # levees
      
      LP = []
      
      if debug:
        info = str(leveePositions[0])
        arcpy.AddMessage(info)
      
         
      if len(leveePositions[0]) > 0: # jesli sa waly
        
        for row in leveePositions[0]:
  
          LPtemp = [nfloat(string.strip(el)) for el in string.split(row,",")]
          LPtemp[0] = str(int(LPtemp[0]))
          LP.append(LPtemp)
        
      tempXs.leveePositions = LP
      
      tempXs.ineffectivePositions = ineffectivePositions
      tempXs.blockedPositions = blockedPositions
      
      # cut line
      
      cutLine = []
      cutLineItems = pullElems(xs, "CUT LINE:", "SURFACE LINE:", 0)
      
      if debug:
        info = "Robie cutline\n\n" + str(cutLineItems)
        arcpy.AddMessage(info)
        
      for row in cutLineItems[0]:
        
        # read point 2d coordinates
        x,y = [nfloat(string.strip(el)) for el in string.split(row,",")]
        
        # add a new point class instance to current cut line
        cutLine.append(cutLinePoint(x,y))
      
      cutLineLengths = []
      check = 0 
      # calculate length of the cutLine
      for pt in cutLine:
        
        if check == 0:
          
          # x0, y0 = [pt.x, pt.y]
          
          pt0 = Vector(pt.x, pt.y)
          check = 1 # after the forst point
          continue # to the next pt
        
        pt1 = Vector(pt.x, pt.y)
        
        # x1, y1 = [pt.x, pt.y]
        # l = sqrt( (x1-x0)**2 + (y1-y0)**2 )
        
        cutLineLengths.append( (pt0-pt1).mag() )
        # cutLineLengths.append( l )
        
        pt0 = Vector(pt.x, pt.y)
        # x0, y0 = [pt.x, pt.y]
      
      cutLineLength = sum(cutLineLengths)
      
      
      # surface line
      
      surfaceLine = []
      surfaceLineItems = pullElems(xs, "SURFACE LINE:", "END:", 0)
      x0, y0 = [None, None] # wsp poprzedniego punktu w przekroju
      
      for row in surfaceLineItems[0]:
      
        x,y,z = [nfloat(string.strip(el)) for el in string.split(row,",")]
        code = None
        
        # calculate m of the point (a 2-dimensional X)
        if [x0,x0] == [None, None]: # this is the first point of the section
          m = 0.
          x0,y0 = [x,y]
        
        else: # second and farther points

          m += (Vector(x,y) - Vector(x0,y0)).mag()
          x0,y0 = [x,y]
        
        frac = m / cutLineLength
        surfaceLine.append(surfaceLinePoint(x,y,z,m,frac,code))
      
      # locate bank and levees
      
      # find indexes
      leftBankInd = None
      rightBankInd = None
      leftLeveeInd = None
      rightLeveeInd = None
      
      leftBankInd = ((i for i in xrange(len(surfaceLine)) if surfaceLine[i].frac >= bankPositions[0])).next()
      rightBankInd = ((i for i in xrange(len(surfaceLine)) if surfaceLine[i].frac >= bankPositions[1])).next()
    
      for levee in tempXs.leveePositions:
        leveeInd = ((i for i in xrange(len(surfaceLine)) if surfaceLine[i].frac >= levee[1])).next()
        if leveeInd <= leftBankInd:
          leftLeveeInd = leveeInd
        elif leveeInd >= rightBankInd:
          rightLeveeInd = leveeInd
      
      # if there is no left or right levee, set the markers to first and last point of the surfaceLine
      if leftLeveeInd == None:
        leftLeveeInd = 0
      if rightLeveeInd == None:
        rightLeveeInd = -1
      
      
      surfaceLine[leftBankInd].code = "<#8>"
      surfaceLine[rightBankInd].code = "<#16>"
      surfaceLine[leftLeveeInd].code = "<#1>"
      surfaceLine[rightLeveeInd].code = "<#4>"
      
      
      tempXs.cutLine = cutLine
      tempXs.cutLineLength = cutLineLength
      tempXs.surfaceLine = surfaceLine
    
      self.xSections.append(tempXs)
      
      del streamId, reachId, station, nodeName, reachLengths, nValues # bankPositions
      del leveePositions, ineffectivePositions, blockedPositions, cutLine, cutLineLengths # surfaceLine
  
  
  def getRASExportStreamNetwork(self):
    
    t = "\nBEGINSTREAMNETWORK:\n\n"
    pList = []
    endPointList = []
    
    for r in self.reaches:
      pList.append(r.fromPt)
      pList.append(r.toPt)
    
    # sortuj punkty po id
    pList = sorted(pList, key=lambda list: list.id)
    
    for pt in pList:
      endPointList.append( pt.getRASEndpoint() )
      # print pt.getRASEndpoint()

    # usun duplikaty punktow
    endPointList = uniqKeepOrder( endPointList )
    
    for el in endPointList:
      t += el
    
    t += "\n"
    
    # reaches
    for r in self.reaches:
      #print r.centerLine[0].id
      
      t += "REACH:\n"
      t += "  STREAM ID: %s\n" % r.streamId
      t += "  REACH ID: %s\n" % r.reachId
      t += "  FROM POINT: %i\n" % r.fromPt.id
      t += "  TO POINT: %i\n" % r.toPt.id
      t += "  CENTERLINE:\n"
      for pt in r.centerLine[1:-1]:
        t += pt.getRASCenterlinePoint()
        
      t += "END:\n"
    
    t += "\nENDSTREAMNETWORK:\n"
    return t

    
  def getRASExportXSections(self):
    
    t = ""
    for xs in self.xSections:
    
      t += "\nBEGIN CROSS-SECTIONS:\n\n"
      t += "  CROSS-SECTION:\n"
      t += "    STREAM ID:%s\n" % xs.streamId
      t += "    REACH ID:%s\n" % xs.reachId
      t += "    STATION:%s\n" % xs.station
      t += "    NODE NAME:%s\n" % xs.nodeName
      t += "    BANK POSITIONS: %.5f, %.5f\n" % (xs.bankPositions[0], xs.bankPositions[1])
      t += "    LEVEE POSITIONS:\n"
      for el in xs.leveePositions:
        t += "      %s, %.5f, %.2f\n" % (el[0], el[1], el[2])

      t += "    CUT LINE:\n"
      
      for pt in xs.cutLine:
        t += "      %.2f, %.2f\n" % (pt.x, pt.y)
            
      t += "    SURFACE LINE:\n"
      
      for pt in xs.surfaceLine:
        t += "    %.2f, %.2f, %.2f, %.2f, %.5f, %s\n" % (pt.x, pt.y, pt.z, pt.m, pt.m/xs.cutLineLength, pt.code)
        #t += "      %.2f, %.2f, %.2f\n" % (pt.x, pt.y, pt.z)
      
      t += "END:\n"
    
    t += "END CROSS-SECTIONS:\n"
    
    return t
    
    
  def getMikeNetwork(self, plik):
    
    t = ""
    today = datetime.datetime.now().strftime(time_format)
    
    t += "// Created     : " + today + "\n"
    t += "// DLL id      : C:\\Program Files (x86)\\DHI\\2011\\Bin\\pfs2004.dll\n"
    t += "// PFS version : Jan  6 2011 20:45:15\n"
    t += "// HEC-RAS GIS -> Mike11 converter by Radoslaw Pasiok\n"
    t += "// email: radoslaw.pasiok@imgw.pl\n\n"

    t += "[MIKE_11_Network_editor]\n"
    t += "   [FORMAT_VERSION]\n"
    t += "      verno = 115\n"
    t += "   EndSect  // FORMAT_VERSION\n\n"

    t += "   [DATA_AREA]\n"
    t += "      x0 = %.2f \n" % self.header.xMin
    t += "      y0 = %.2f \n" % self.header.yMin
    t += "      x1 = %.2f \n" % self.header.xMax
    t += "      y1 = %.2f \n" % self.header.yMax
    t += "      projection = 'NON-UTM'\n"
    t += "   EndSect  // DATA_AREA\n\n"
    
    t += "   [POINTS]\n"
    
    for reach in self.reaches:
      
      for pt in reach.centerLine:
      
        t += pt.getMikePoint()
        
        
    t += "   EndSect  // POINTS\n\n"
    
    t += "   [BRANCHES]\n"
    
    for r in self.reaches:
      
      t += "      [branch]\n"
      #t += "        definitions = 'Warta', 'Warta', 461553, 462428, 1, 10000, 0"
      t += "        definitions = \'%s\', \'%s\', %.2f, %.2f, %i, 10000, 0\n" % (r.reachId, r.reachId, 0, 0, 1)
      t += "        connections = '', -1e-155, '', -1e-155\n        points = "
      
      for pt in reversed(r.centerLine):
      # for pt in r.centerLine:
          
        t += "%i, " % pt.id
      
      t = t[:-2] + "\n"
      t += "      EndSect  // branch\n\n"
     


    t += "   EndSect  // BRANCHES\n\n"
    
    t += "   [STRUCTURE_MODULE]\n"
    t += "      Structure_Version = 1, 1\n"
    t += "      [CROSSSECTIONS]\n"
    t += "         CrossSectionDataBridge = \'xns11\'\n"
    t += "         CrossSectionFile = |.\\%s.xns11|\n" % plik
    t += "      EndSect  // CROSSSECTIONS\n"



    t += "   EndSect  // STRUCTURE_MODULE\n\n"
    
    t += "EndSect  // MIKE_11_Network_editor"
    return t
    
    

  def getMikeRawdata(self):

    rawdata = ""
    
    for xs in self.xSections:
      
      t = "%s\n" % xs.reachId
      t += "%s\n" % xs.reachId #xs.streamId
      t += "               %.2f\n" % xs.station
      t += "COORDINATES\n    %i  %.2f  %.2f  %.2f  %.2f\n" \
          % (2,xs.cutLine[0].x, xs.cutLine[0].y, xs.cutLine[-1].x, xs.cutLine[-1].y)

      t += "FLOW DIRECTION\n    1\n"
      t += "PROTECT DATA\n    0\n"
      t += "DATUM\n    0.0\n"
      t += "RADIUS TYPE\n    0\n"
      t += "DIVIDE X-Section\n    0\n"
      t += "SECTION ID\n    %s\n" % xs.nodeName
      t += "INTERPOLATED\n    0\n"
      t += "ANGLE\n    0.00 0\n"
      t += "RESISTANCE NUMBERS\n   0  0     1.000     1.000     1.000    1.000    1.000\n"
      t += "PROFILE        %i\n" % len(xs.surfaceLine)

      for pt in xs.surfaceLine:
      
        t += pt.getMikePoint()

      t += "LEVEL PARAMS\n   0  0    0.000  0    0.000  100\n*******************************\n"
      
      rawdata += t
      
    return rawdata


  def getMikeSim(self,plik):

    sim = '''// Created     : 2012-01-9 8:38:5
// DLL id      : C:\\Program Files (x86)\\DHI\\2011\\Bin\\pfs2004.dll
// PFS version : Jan  6 2011 20:45:15

[Run11]
   format_version = 107, 'MIKEZero, 2011'
   Comment = ''
   [Models]
      hd = true, false
      ad = false
      st = false
      wq = false, 1, 0
      rr = false
      ff = false
      da = false
      ice = false
      SimMode = 0
      QSS = 0
   EndSect  // Models

   [Input]\n'''
   
    sim += "      nwk = |.\\" + plik + ".nwk11|\n"
      
    sim += '''      xs = ||
      bnd = ||
      rr = ||
      hd = ||
      ad = ||
      wq = ||
      st = ||
      ff = ||
      rhd = ||
      rrr = ||
      da = ||
      ice = ||
   EndSect  // Input

   [Simulation]
      [Simulation_Period]
         start = 1990, 1, 1, 12, 0, 0
         end = 1990, 2, 1, 12, 0, 0
         TimeStepType = 0
         timestep = 30
         timestepunit = 2
         dtFileName = ||
         dtItemName = ''
         dtItemNo = 0
         ddtMin = 1
         ddtMax = 30
         idtMinMaxUnit = 2
         ddtChangeRatio = 1.3
         bDelB_BFlag = true
         dDelB_BVal = 0.01
         dDelB_BLim = 0.01
         bDelQFlag = false
         dDelQVal = 1
         bDelQ_QFlag = true
         dDelQ_QVal = 0.01
         dDelQ_QLim = 0.01
         bDelhFlag = false
         dDelhVal = 0.01
         bDelh_hFlag = true
         dDelh_hVal = 0.01
         dDelh_hLim = 0.01
         bCourantFlagHD = false
         dCourantValHD = 10
         bCourantFlagAD = true
         dCourantValAD = 1
         ST_timestep_multiplier = 1
         RR_timestep_multiplier = 1
      EndSect  // Simulation_Period

      [Initial_Conditions]
         hd = 0, ||, false, 1990, 1, 1, 12, 0, 0
         ad = 0, ||, false, 1990, 1, 1, 12, 0, 0
         st = 0, ||, false, 1990, 1, 1, 12, 0, 0
         rr = 0, ||, false, 1990, 1, 1, 12, 0, 0
      EndSect  // Initial_Conditions

   EndSect  // Simulation

   [Results]
      hd = ||, '', 1, 0
      ad = ||, '', 1, 0
      st = ||, '', 1, 0
      rr = ||, '', 1, 0
   EndSect  // Results

EndSect  // Run11'''
    return sim
    
