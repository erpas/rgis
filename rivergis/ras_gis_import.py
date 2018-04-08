# -*- coding: utf-8 -*-

"""
/***************************************************************************
Name                 : RiverGIS
Description          : HEC-RAS tools for QGIS
Date                 : December, 2015
copyright            : (C) 2015 by RiverGIS Group
email                : rpasiok@gmail.com, damnback333@gmail.com
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
from builtins import object

from qgis.core import QgsUnitTypes


class RasGisImport(object):
    """
    Exporting model to RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.header = HeaderBuilder(rgis)
        self.network = NetworkBuilder(rgis)
        self.xsections = XSBuilder(rgis)
        self.bridges = BridgesBuilder(rgis)
        self.inline_str = InlineStrBuilder(rgis)
        self.lateral_str = LateralStrBuilder(rgis)
        self.levees = LeveesBuilder(rgis)
        self.ineff_areas = IneffAreasBuilder(rgis)
        self.blocked_obs = BlockedObsBuilder(rgis)
        self.storage_areas = StorageAreasBuilder(rgis)
        self.sa_connections = SAConnectionsBuilder(rgis)

    def check_components(self):
        schema = self.rgis.rdb.SCHEMA
        tabs = self.rgis.rdb.register
        attrs = self.__dict__
        for key in attrs:
            obj = attrs[key]
            if hasattr(obj, 'components') is True:
                for elem in obj.components:
                    if elem not in tabs:
                        msg = 'WARNING! Nonexistent "{0}" table. This part of SDF file will be omitted.'.format(elem)
                        self.rgis.addInfo(msg)
                    else:
                        self.check_SRID(schema, elem, 'geom', 'Manning', 'SAVolume')
            else:
                pass

    def check_SRID(self, schema, table, geom, *no_geom):
        if table in no_geom:
            return
        else:
            pass
        qry = '''SELECT Find_SRID('{0}', '{1}', '{2}');'''
        qry = qry.format(schema, table, geom)
        srid = self.rgis.rdb.run_query(qry, fetch=True)[0][0]
        crs = int(self.rgis.crs.postgisSrid())
        if srid != crs:
            msg = 'WARNING! Differences between "{0}" table SRID ({1}) and project CRS ({2}).'.format(table, srid, crs)
            self.rgis.addInfo(msg)
        else:
            pass
        return srid

    @staticmethod
    def unpack_wkt(wkt):
        if wkt.startswith('POINT'):
            sidx = 6
            eidx = -1
        elif wkt.startswith('LINESTRING'):
            sidx = 11
            eidx = -1
        elif wkt.startswith('POLYGON'):
            sidx = 9
            eidx = -2
        else:
            raise ValueError('Inappropriate WKT geometry type. WKT must be POINT, LINESTRING or POLYGON.')
        pnts = (p.split() for p in wkt[sidx:eidx].split(','))
        return pnts

    def gis_import_file(self):
        imp = self.header.build_header()
        imp += self.network.build_network()
        imp += self.xsections.build_cross_sections()
        imp += self.bridges.build_bridges()
        imp += self.inline_str.build_inline_str()
        imp += self.lateral_str.build_lateral_str()
        imp += self.levees.build_levees()
        imp += self.ineff_areas.build_ineff_areas()
        imp += self.blocked_obs.build_blocked_obs()
        imp += self.storage_areas.build_storage_areas()
        imp += self.sa_connections.build_sa_connections()
        return imp


class HeaderBuilder(object):
    """
    Return header of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.dbname = rgis.rdb.dbname
        self.host = rgis.rdb.host
        self.schema = rgis.rdb.SCHEMA
        self.srid = rgis.rdb.SRID

    def number_of_reaches(self):
        qry = 'SELECT COUNT("ReachID") FROM "{0}"."StreamCenterlines";'
        qry = qry.format(self.schema)
        nor = int(self.rgis.rdb.run_query(qry, fetch=True)[0][0])
        if self.rgis.DEBUG:
            self.rgis.addInfo('Nr of reaches: {0:d}'.format(nor))
        return nor

    def number_of_xsections(self):
        qry = 'SELECT COUNT("XsecID") FROM "{0}"."XSCutLines";'
        qry = qry.format(self.schema)
        nox = int(self.rgis.rdb.run_query(qry, fetch=True)[0][0])
        if self.rgis.DEBUG:
            self.rgis.addInfo('Nr of cross-sections: {0:d}'.format(nox))
        return nox

    def spatial_extent(self):
        qry = 'SELECT ST_Extent(geom) FROM "{0}"."XSCutLines";'
        qry = qry.format(self.schema)
        box = self.rgis.rdb.run_query(qry, fetch=True)[0][0]
        box_min = box[box.index('(')+1:box.index(',')].split()
        box_max = box[box.index(',')+1:box.index(')')].split()
        ext = 'XMIN: {0}\n      YMIN: {1}\n      XMAX: {2}\n      YMAX: {3}\n   '
        se = ext.format(box_min[0], box_min[1], box_max[0], box_max[1])
        if self.rgis.DEBUG:
            self.rgis.addInfo(se)
        return se

    def spatial_unit(self):
        u = self.rgis.crs.mapUnits()
        su = QgsUnitTypes.toString(u).upper()
        return su

    def build_header(self):
        hdr = '''#This file is generated by RiverGIS, a QGIS plugin (http://rivergis.com)
BEGIN HEADER:
   DTM TYPE: GRID
   DTM:
   STREAM LAYER: {0}@{1}/{2}/StreamCenterlines
   NUMBER OF REACHES: {3:d}
   CROSS-SECTION LAYER: {0}@{1}/{2}/XSCutLines
   NUMBER OF CROSS-SECTIONS: {4:d}
   MAP PROJECTION:
   PROJECTION ZONE:
   DATUM:
   VERTICAL DATUM:
   BEGIN SPATIAL EXTENT:
      {5}END SPATIAL EXTENT:
      UNITS: {6}
END HEADER:

'''
        nor = self.number_of_reaches()
        nox = self.number_of_xsections()
        se = self.spatial_extent()
        su = self.spatial_unit()
        hdr = hdr.format(self.dbname, self.host, self.schema, nor, nox, se, su)
        return hdr


class NetworkBuilder(object):
    """
    Return STREAM NETWORK part of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.schema = rgis.rdb.SCHEMA
        self.components = ['NodesTable', 'StreamCenterlines']

    def get_nodes(self):
        qry = 'SELECT "NodeID", "X", "Y" FROM "{0}"."NodesTable";'
        qry = qry.format(self.schema)
        nodes = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if nodes is None:
            return []
        else:
            return nodes

    def get_reaches(self):
        qry = '''
SELECT
    "ReachID",
    "RiverCode",
    "ReachCode",
    "FromNode",
    "ToNode",
    ST_AsText(geom) AS wkt
FROM
    "{0}"."StreamCenterlines"
WHERE
    "ReachCode" IS NOT NULL;
'''
        qry = qry.format(self.schema)
        reaches = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if reaches is None:
            return []
        else:
            return reaches

    def build_network(self):
        net_all = 'BEGIN STREAM NETWORK:\n'
        net_node = '   ENDPOINT: {0:f}, {1:f}, 0, {2}\n'
        net_reach = '''
   REACH:
      STREAM ID: {0}
      REACH ID: {1}
      FROM POINT: {2}
      TO POINT: {3}
      CENTERLINE:
{4}   END:
'''
        net_centerline = '         {0}, {1}, None\n'
        net_end = '\nEND STREAM NETWORK:\n\n'
        nodes = self.get_nodes()
        reaches = self.get_reaches()
        for node in nodes:
            net_all += net_node.format(node['X'], node['Y'], node['NodeID'])
        for reach in reaches:
            centerlines = ''
            pnts = RasGisImport.unpack_wkt(reach['wkt'])
            for pt in pnts:
                x, y = pt
                centerlines += net_centerline.format(x, y)
            net_all += net_reach.format(reach['RiverCode'], reach['ReachCode'], reach['FromNode'], reach['ToNode'], centerlines)
        net_all += net_end
        return net_all


class XSBuilder(object):
    """
     Return CROSS SECTIONS part of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.schema = rgis.rdb.SCHEMA
        self.components = ['XSCutLines', 'Manning', 'LeveePoints', 'IneffLines', 'BlockLines', 'XSSurface']

    def get_xsections(self):
        qry = '''
SELECT
    "XsecID",
    "RiverCode",
    "ReachCode",
    "Station",
    "LeftBank",
    "RightBank",
    "LLength",
    "ChLength",
    "RLength",
    ST_AsText(geom) AS wkt
FROM
    "{0}"."XSCutLines"
ORDER BY
    "RiverCode",
    "Station";
'''
        qry = qry.format(self.schema)
        xsections = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if xsections is None:
            return []
        else:
            return xsections

    def get_nvalues(self, xs_id):
        qry = 'SELECT "Fraction", "N_Value" FROM "{0}"."Manning" WHERE "XsecID" = {1};'
        qry = qry.format(self.schema, xs_id)
        nvalues = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if nvalues is None:
            return []
        else:
            return nvalues

    def get_levee_points(self, xs_id):
        qry = 'SELECT "LeveeID", "Fraction", "Elevation" FROM "{0}"."LeveePoints" WHERE "XsecID" = {1};'
        qry = qry.format(self.schema, xs_id)
        levee_points = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if levee_points is None:
            return []
        else:
            return levee_points

    def get_ineffs(self, xs_id):
        qry = 'SELECT "IneffID", "FromFract", "ToFract", "Elevation" FROM "{0}"."IneffLines" WHERE "XsecID" = {1};'
        qry = qry.format(self.schema, xs_id)
        ineffs = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if ineffs is None:
            return []
        else:
            return ineffs

    def get_blocks(self, xs_id):
        qry = 'SELECT "BlockID", "FromFract", "ToFract", "Elevation" FROM "{0}"."BlockLines" WHERE "XsecID" = {1};'
        qry = qry.format(self.schema, xs_id)
        blocks = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if blocks is None:
            return []
        else:
            return blocks

    def get_surf(self, xs_id):
        qry = 'SELECT ST_X(geom) AS x, ST_Y(geom) AS y, "Elevation" FROM "{0}"."XSSurface" WHERE "XsecID" = {1} ORDER BY "Station";'
        qry = qry.format(self.schema, xs_id)
        surfs = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if surfs is None:
            return []
        else:
            return surfs

    def build_cross_sections(self):
        xsec_all = 'BEGIN CROSS-SECTIONS:\n'
        xsec_nval = '         {0}, {1}\n'
        xsec_levee_points = '         {0}, {1}, {2}\n'
        xsec_ineff = '         {0}, {1}, {2}, {3}\n'
        xsec_block = '         {0}, {1}, {2}, {3}\n'
        xsec_cut = '         {0}, {1}\n'
        xsec_surf = '         {0}, {1}, {2}\n'
        xsec_cross = '''
   CROSS-SECTION:
      STREAM ID:{6}
      REACH ID:{7}
      STATION:{8}
      NODE NAME:
      BANK POSITIONS: {9}, {10}
      REACH LENGTHS: {11}, {12}, {13}
      NVALUES:
{0}   LEVEE POSITIONS:
{1}   INEFFECTIVE POSITIONS:
{2}   BLOCKED POSITIONS:
{3}   CUT LINE:
{4}   SURFACE LINE:
{5}   END:
'''
        xsec_end = '\nEND CROSS-SECTIONS:\n\n'
        for cs in self.get_xsections():
            xs_id = cs['XsecID']
            attrs = cs[1:-1]
            nvalues = ''
            levee_points = ''
            ineffs = ''
            blocks = ''
            cuts = ''
            surfs = ''
            for n in self.get_nvalues(xs_id):
                nvalues += xsec_nval.format(n['Fraction'], n['N_Value'])
            for l in self.get_levee_points(xs_id):
                levee_points += xsec_levee_points.format(l['LeveeID'], l['Fraction'], l['Elevation'])
            for i in self.get_ineffs(xs_id):
                ineffs += xsec_ineff.format(i['IneffID'], i['FromFract'], i['ToFract'], i['Elevation'])
            for b in self.get_blocks(xs_id):
                blocks += xsec_block.format(b['BlockID'], b['FromFract'], b['ToFract'], b['Elevation'])
            pnts = RasGisImport.unpack_wkt(cs['wkt'])
            for pt in pnts:
                x, y = pt
                cuts += xsec_cut.format(x, y)
            for s in self.get_surf(xs_id):
                surfs += xsec_surf.format(s['x'], s['y'], s['Elevation'])
            xsec_all += xsec_cross.format(nvalues, levee_points, ineffs, blocks, cuts, surfs, *attrs)
        xsec_all += xsec_end
        return xsec_all


class BridgesBuilder(object):
    """
    Return BRIDGES part of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.schema = rgis.rdb.SCHEMA
        self.components = ['Bridges', 'BRSurface']

    def get_bridges(self):
        qry = '''
SELECT
    "BridgeID",
    "RiverCode",
    "ReachCode",
    "Station",
    "USDistance",
    "TopWidth",
    "NodeName",
    ST_AsText(geom) AS wkt
FROM
    "{0}"."Bridges";
'''
        qry = qry.format(self.schema)
        bridges = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if bridges is None:
            return []
        else:
            return bridges

    def get_surf(self, br_id):
        qry = 'SELECT ST_X(geom) AS x, ST_Y(geom) AS y, "Elevation" FROM "{0}"."BRSurface" WHERE "BridgeID" = {1} ORDER BY "Station";'
        qry = qry.format(self.schema, br_id)
        surfs = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if surfs is None:
            return []
        else:
            return surfs

    def build_bridges(self):
        bridges_all = 'BEGIN BRIDGES/CULVERTS:\n'
        bridge_cut = '         {0}, {1}\n'
        bridge_surf = '         {0}, {1}, {2}\n'
        bridge_object = '''
   BRIDGE/CULVERT:
      STREAM ID: {0}
      REACH ID: {1}
      STATION: {2}
      NODE NAME: {3}
      US DISTANCE: {4}
      TOP WIDTH: {5}
      CUT LINE:
{6}   SURFACE LINE:
{7}   END:
'''
        bridges_end = '\nEND BRIDGES/CULVERTS:\n\n'
        for br in self.get_bridges():
            br_id = br['BridgeID']
            cuts = ''
            surfs = ''
            pnts = RasGisImport.unpack_wkt(br['wkt'])
            for pt in pnts:
                x, y = pt
                cuts += bridge_cut.format(x, y)
            for s in self.get_surf(br_id):
                surfs += bridge_surf.format(s['x'], s['y'], s['Elevation'])
            bridges_all += bridge_object.format(br['RiverCode'], br['ReachCode'], br['Station'], br['NodeName'], br['USDistance'], br['TopWidth'], cuts, surfs)
        bridges_all += bridges_end
        return bridges_all


class InlineStrBuilder(object):
    """
    Return INLINE STRUCTURES part of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.schema = rgis.rdb.SCHEMA
        self.components = ['InlineStructures', 'ISSurface']

    def get_inline_str(self):
        qry = '''
SELECT
    "InlineSID",
    "RiverCode",
    "ReachCode",
    "Station",
    "USDistance",
    "TopWidth",
    "NodeName",
    ST_AsText(geom) AS wkt
FROM
    "{0}"."InlineStructures";
'''
        qry = qry.format(self.schema)
        inline_str = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if inline_str is None:
            return []
        else:
            return inline_str

    def get_surf(self, ins_id):
        qry = 'SELECT ST_X(geom) AS x, ST_Y(geom) AS y, "Elevation" FROM "{0}"."ISSurface" WHERE "InlineSID" = {1} ORDER BY "Station";'
        qry = qry.format(self.schema, ins_id)
        surfs = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if surfs is None:
            return []
        else:
            return surfs

    def build_inline_str(self):
        inline_str_all = 'BEGIN INLINE STRUCTURES:\n'
        inline_str_cut = '         {0}, {1}\n'
        inline_str_surf = '         {0}, {1}, {2}\n'
        inline_str_object = '''
   INLINE STRUCTURE:
      STREAM ID: {0}
      REACH ID: {1}
      STATION: {2}
      NODE NAME: {3}
      US DISTANCE: {4}
      TOP WIDTH: {5}
      CUT LINE:
{6}   SURFACE LINE:
{7}   END:
'''
        inline_str_end = '\nEND INLINE STRUCTURES:\n\n'
        for ins in self.get_inline_str():
            ins_id = ins['InlineSID']
            cuts = ''
            surfs = ''
            pnts = RasGisImport.unpack_wkt(ins['wkt'])
            for pt in pnts:
                x, y = pt
                cuts += inline_str_cut.format(x, y)
            for s in self.get_surf(ins_id):
                surfs += inline_str_surf.format(s['x'], s['y'], s['Elevation'])
            inline_str_all += inline_str_object.format(ins['RiverCode'], ins['ReachCode'], ins['Station'], ins['NodeName'], ins['USDistance'], ins['TopWidth'], cuts, surfs)
        inline_str_all += inline_str_end
        return inline_str_all


class LateralStrBuilder(object):
    """
    Return LATERAL STRUCTURES part of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.schema = rgis.rdb.SCHEMA
        self.components = ['LateralStructures', 'LSSurface']

    def get_lateral_str(self):
        qry = '''
SELECT
    "LateralSID",
    "RiverCode",
    "ReachCode",
    "Station",
    "USDistance",
    "TopWidth",
    "NodeName",
    ST_AsText(geom) AS wkt
FROM
    "{0}"."LateralStructures";
'''
        qry = qry.format(self.schema)
        lateral_str = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if lateral_str is None:
            return []
        else:
            return lateral_str

    def get_surf(self, ls_id):
        qry = 'SELECT ST_X(geom) AS x, ST_Y(geom) AS y, "Elevation" FROM "{0}"."LSSurface" WHERE "LateralSID" = {1} ORDER BY "Station";'
        qry = qry.format(self.schema, ls_id)
        surfs = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if surfs is None:
            return []
        else:
            return surfs

    def build_lateral_str(self):
        lateral_str_all = 'BEGIN LATERAL STRUCTURES:\n'
        lateral_str_cut = '         {0}, {1}\n'
        lateral_str_surf = '         {0}, {1}, {2}\n'
        lateral_str_object = '''
   LATERAL STRUCTURE:
      STREAM ID: {0}
      REACH ID: {1}
      STATION: {2}
      NODE NAME: {3}
      US DISTANCE: {4}
      TOP WIDTH: {5}
      CUT LINE:
{6}   SURFACE LINE:
{7}   END:
'''
        lateral_str_end = '\nEND LATERAL STRUCTURES:\n\n'
        for ls in self.get_lateral_str():
            ls_id = ls['LateralSID']
            cuts = ''
            surfs = ''
            pnts = RasGisImport.unpack_wkt(ls['wkt'])
            for pt in pnts:
                x, y = pt
                cuts += lateral_str_cut.format(x, y)
            for s in self.get_surf(ls_id):
                surfs += lateral_str_surf.format(s['x'], s['y'], s['Elevation'])
            lateral_str_all += lateral_str_object.format(ls['RiverCode'], ls['ReachCode'], ls['Station'], ls['NodeName'], ls['USDistance'], ls['TopWidth'], cuts, surfs)
        lateral_str_all += lateral_str_end
        return lateral_str_all


class LeveesBuilder(object):
    """
     Return LEVEES part of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.schema = rgis.rdb.SCHEMA
        self.components = ['LeveeAlignment']

    def get_levees(self):
        qry = 'SELECT "LeveeID", ST_AsText(geom) AS wkt FROM "{0}"."LeveeAlignment";'
        qry = qry.format(self.schema)
        levees = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if levees is None:
            return []
        else:
            return levees

    def build_levees(self):
        levees_all = 'BEGIN LEVEES:\n'
        levee_object = '''
   LEVEE ID: {0}
      SURFACE LINE:
{1}   END:
'''
        levees_surf = '         {0}, {1}, None\n'
        levees_end = '\nEND LEVEES:\n\n'
        for l in self.get_levees():
            surfs = ''
            levee_id = l['LeveeID']
            pnts = RasGisImport.unpack_wkt(l['wkt'])
            for pt in pnts:
                x, y = pt
                surfs += levees_surf.format(x, y)
            levees_all += levee_object.format(levee_id, surfs)
        levees_all += levees_end
        return levees_all


class IneffAreasBuilder(object):
    """
     Return Ineffective Areas part of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.schema = rgis.rdb.SCHEMA
        self.components = ['IneffAreas']

    def get_ineffective_areas(self):
        qry = 'SELECT "IneffID", ST_AsText(geom) AS wkt FROM "{0}"."IneffAreas";'
        qry = qry.format(self.schema)
        ineff_areas = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if ineff_areas is None:
            return []
        else:
            return ineff_areas

    def build_ineff_areas(self):
        ineff_all = 'BEGIN INEFFECTIVE AREAS:\n'
        ineff_poly = '''
   INEFFECTIVE ID: {0}
      POLYGON:
{1}   END:
'''
        ineff_vertex = '         {0}, {1}\n'
        ineff_end = '\nEND INEFFECTIVE AREAS:\n\n'
        for i in self.get_ineffective_areas():
            vertices = ''
            ineff_id = i['IneffID']
            pnts = RasGisImport.unpack_wkt(i['wkt'])
            for pt in pnts:
                x, y = pt
                vertices += ineff_vertex.format(x, y)
            ineff_all += ineff_poly.format(ineff_id, vertices)
        ineff_all += ineff_end
        return ineff_all


class BlockedObsBuilder(object):
    """
     Return Blocked Obstructions part of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.schema = rgis.rdb.SCHEMA
        self.components = ['BlockedObs']

    def get_blocked_obstructions(self):
        qry = 'SELECT "BlockID", ST_AsText(geom) AS wkt FROM "{0}"."BlockedObs";'
        qry = qry.format(self.schema)
        block_obs = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if block_obs is None:
            return []
        else:
            return block_obs

    def build_blocked_obs(self):
        block_all = 'BEGIN BLOCKED OBSTRUCTIONS:\n'
        block_poly = '''
   BLOCKED ID: {0}
      POLYGON:
{1}   END:
'''
        block_vertex = '         {0}, {1}\n'
        block_end = '\nEND BLOCKED OBSTRUCTIONS:\n\n'
        for b in self.get_blocked_obstructions():
            vertices = ''
            block_id = b['BlockID']
            pnts = RasGisImport.unpack_wkt(b['wkt'])
            for pt in pnts:
                x, y = pt
                vertices += block_vertex.format(x, y)
            block_all += block_poly.format(block_id, vertices)
        block_all += block_end
        return block_all


class StorageAreasBuilder(object):
    """
    Return STORAGE AREAS part of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.schema = rgis.rdb.SCHEMA
        self.components = ['StorageAreas', 'SAVolume']

    def get_storage_areas(self):
        qry = 'SELECT "StorageID", ST_AsText(geom) AS wkt FROM "{0}"."StorageAreas";'
        qry = qry.format(self.schema)
        storage_areas = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if storage_areas is None:
            return []
        else:
            return storage_areas

    def get_storage_volume(self, sa_id):
        qry = 'SELECT "level", "volume" FROM "{0}"."SAVolume" WHERE "StorageID" = {1} ORDER BY "level";'
        qry = qry.format(self.schema, sa_id)
        storage_volume = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if storage_volume is None:
            return []
        else:
            return storage_volume

    def build_storage_areas(self):
        sa_all = 'BEGIN STORAGE AREAS:\n'
        sa_poly = '''
      SA ID: {0}
      POLYGON:
{1}      END:
      ELEVATION-VOLUME:
{2}      END:
      TERRAIN:
      END:
'''
        sa_vertex = '         {0}, {1}\n'
        sa_elev = '         {0}, {1}\n'
        sa_end = '\nEND STORAGE AREAS:\n\n'
        for s in self.get_storage_areas():
            vertices = ''
            elev = ''
            sa_id = s['StorageID']
            pnts = RasGisImport.unpack_wkt(s['wkt'])
            for pt in pnts:
                x, y = pt
                vertices += sa_vertex.format(x, y)
            for v in self.get_storage_volume(sa_id):
                elev += sa_elev.format(v['level'], v['volume'])
            sa_all += sa_poly.format(sa_id, vertices, elev)
        sa_all += sa_end
        return sa_all


class SAConnectionsBuilder(object):
    """
    Return SA CONNECTIONS part of RAS GIS Import file.
    """
    def __init__(self, rgis):
        self.rgis = rgis
        self.schema = rgis.rdb.SCHEMA
        self.components = ['SAConnections', 'SACSurface']

    def get_sa_conn(self):
        qry = 'SELECT "SAConnID", "USSA", "DSSA", "TopWidth", "NodeName", ST_AsText(geom) AS wkt FROM "{0}"."SAConnections";'
        qry = qry.format(self.schema)
        sa_connections = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if sa_connections is None:
            return []
        else:
            return sa_connections

    def get_surf(self, sac_id):
        qry = 'SELECT ST_X(geom) AS x, ST_Y(geom) AS y, "Elevation" FROM "{0}"."SACSurface" WHERE "SAConnID" = {1} ORDER BY "Station";'
        qry = qry.format(self.schema, sac_id)
        surfs = self.rgis.rdb.run_query(qry, fetch=True, be_quiet=True)
        if surfs is None:
            return []
        else:
            return surfs

    def build_sa_connections(self):
        sa_conn_all = 'BEGIN SA CONNECTIONS:\n'
        sa_conn_cut = '         {0}, {1}\n'
        sa_conn_surf = '         {0}, {1}, {2}\n'
        sa_conn_object = '''
   SA CONNECTION:
      SACONN ID: {0}
      NODE NAME: {1}
      US SA: {2}
      DS SA: {3}
      TOP WIDTH: {4}
      CUT LINE:
{5}   SURFACE LINE:
{6}   END:
'''
        sa_conn_end = '\nEND SA CONNECTIONS:\n\n'
        for sac in self.get_sa_conn():
            sac_id = sac['SAConnID']
            cuts = ''
            surfs = ''
            pnts = RasGisImport.unpack_wkt(sac['wkt'])
            for pt in pnts:
                x, y = pt
                cuts += sa_conn_cut.format(x, y)
            for s in self.get_surf(sac_id):
                surfs += sa_conn_surf.format(s['x'], s['y'], s['Elevation'])
            sa_conn_all += sa_conn_object.format(sac['SAConnID'], sac['NodeName'], sac['USSA'], sac['DSSA'], sac['TopWidth'], cuts, surfs)
        sa_conn_all += sa_conn_end
        return sa_conn_all
