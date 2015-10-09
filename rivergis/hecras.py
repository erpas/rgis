# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                                 : RiverGIS
Description                    : HEC-RAS tools for QGIS
Date                                 : January, 2015
copyright                        : (C) 2015 by RiverGIS Group
email                                : rpasiok@gmail.com

 ***************************************************************************/

/***************************************************************************
 *                                                                                                                                                 *
 *     This program is free software; you can redistribute it and/or modify    *
 *     it under the terms of the GNU General Public License as published by    *
 *     the Free Software Foundation; either version 2 of the License, or         *
 *     (at your option) any later version.                                                                     *
 *                                                                                                                                                 *
 ***************************************************************************/
"""

import os.path

class HecrasProject():
    '''A HEC-RAS project class'''
    def __init__(self,prjFile):
        prjTxt = open(prjFile,"r").readlines()
        self.dirname = os.path.dirname(prjFile)
        self.baseName = prjFile[:-3]
        self.geomFiles = []
        self.steadyFlowFiles = []
        self.unsteadyFlowFiles = []
        self.planFiles = []
        self.planHdfFiles = []
        for line in prjTxt:
            if 'Proj title=' in line:
                self.title = line.split("=")[1].strip()
            elif 'Geom File=' in line:
                self.geomFiles.append(line.split("=")[1].strip())
            elif 'Flow File=' in line:
                self.steadyFlowFiles.append(line.split("=")[1].strip())
            elif 'Unsteady File=' in line:
                self.unsteadyFlowFiles.append(line.split("=")[1].strip())
            elif 'Plan File=' in line:
                self.planFiles.append(line.split("=")[1].strip())
            elif 'Current Plan=' in line:
                self.curPlanId = line.split("=")[1].strip()

        # check which plans have a corresponding HDF file
        for p in self.planFiles:
            if os.path.exists(self.baseName+p+'.hdf'):
                self.planHdfFiles.append(p)


class HecrasPlan():
    '''A HEC-RAS plan class'''
    def __init__(self,prj,planId):
        self.hdf = None
        try:
            import h5py
        except:
            return # cannot continue w/o h5py package
        self.prj = prj # a HecrasProject class instance
        self.id = planId
        try:
            self.hdf = h5py.File(self.prj.baseName+self.id+'.hdf','r')
            attrs = self.hdf['/Plan Data/Plan Information'].attrs
            self.geom = attrs.get('Geometry Name')
            self.geomTitle = attrs.get('Geometry Title')
            self.file = attrs.get('Plan File')
            self.name = attrs.get('Plan Name')
            self.shortId = attrs.get('Plan ShortID')
            # check if the project folder was moved since computation time
            # i.e if project dirname differs from the path written to the attributes
            if not self.prj.dirname == os.path.dirname(self.geom):
                self.geom = os.path.join(self.prj.dirname,os.path.basename(self.geom))
                self.file = os.path.join(self.prj.dirname,os.path.basename(self.file))
        except:
            # HDF file cannot be opened - maybe we should load some details from txt
            self.hdf = None

        if not self.hdf:
            self.noHdf()
            # self.loadTxt()

    def noHdf(self):
        '''What to do if HDF cannot be opened'''
        pass

    def loadTxt(self):
        '''Loads some plan details from txt *.p** file'''
        planTxt = open(self.baseName+plan, "r").readlines()
        for line in planTxt:
            i = line.index('=') + 1
            if 'Flow File=' in line:
                if line[i:i+1] == 'f':
                    self.isSteady = True
                elif line[i:i+1] == 'u':
                    self.isSteady = False
                else:
                    self.isSteady = None

    def check2D(self):
        '''Checks if the plan is a 2D simulation'''
        self.is2D = None
        if not self.hdf:
            self.noHdf()
        else:
            try:
                self.flowAreas = self.hdf['/Geometry/2D Flow Areas/Names']
                self.is2D = len(self.flowAreas) > 0
            except KeyError:
                self.is2D = False

    def checkHasResults(self):
        '''Checks if the plan has some results and if it is a steady simulation'''
        try:
                res = self.hdf['/Results']
                self.hasResults = True
                if 'Steady' in res.keys():
                    self.isSteady = True
                elif 'Unsteady' in res.keys():
                    self.isSteady = False
        except KeyError:
                self.hasResults = False





