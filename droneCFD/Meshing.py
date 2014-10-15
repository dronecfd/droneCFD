##########################################################################################
##  _______  .______        ______   .__   __.  _______      ______  _______  _______   ##
## |       \ |   _  \      /  __  \  |  \ |  | |   ____|    /      ||   ____||       \  ##
## |  .--.  ||  |_)  |    |  |  |  | |   \|  | |  |__      |  ,----'|  |__   |  .--.  | ##
## |  |  |  ||      /     |  |  |  | |  . `  | |   __|     |  |     |   __|  |  |  |  | ##
## |  '--'  ||  |\  \----.|  `--'  | |  |\   | |  |____    |  `----.|  |     |  '--'  | ##
## |_______/ | _| `._____| \______/  |__| \__| |_______|    \______||__|     |_______/  ##
##                                                                                      ##
##########################################################################################
__author__ = 'chrispaulson'

import os
import numpy as np
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Applications.Runner import Runner
from PyFoam.Applications.MeshUtilityRunner import MeshUtilityRunner
import Utilities
import math

def which(program):
    ## Taken from harmv's stackoverflow answer (http://stackoverflow.com/questions/377017/test-if-executable-exists-in-python)
    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    fpath, fname = os.path.split(program)
    if fpath:
        if is_exe(program):
            return program
    else:
        for path in os.environ["PATH"].split(os.pathsep):
            path = path.strip('"')
            exe_file = os.path.join(path, program)
            if is_exe(exe_file):
                return exe_file

    return None

class mesher():

    def __init__(self, casePath, stlSolid, nprocs=None, baseCellSize=0.25, parserArgs=None):
        self.casePath = casePath
        self.stlSolid = stlSolid
        self.procsUtil = Utilities.parallelUtilities(nprocs)
        self.baseCellSize = baseCellSize
        if self.procsUtil.procs > 1:
            self.parallel = True
            self.nprocs = self.procsUtil.procs
        else:
            self.parallel = False
            self.nprocs = 1
        ## Load in blockMeshDict
        self.blockMeshDict = ParsedParameterFile(os.path.join(casePath,'constant','polyMesh','blockMeshDict'))
        self.snappyHexMeshDict = ParsedParameterFile(os.path.join(casePath,'system','snappyHexMeshDict'))
        self.decomposeParDict = ParsedParameterFile(os.path.join(casePath,'system','decomposeParDict'))

    def blockMeshDomain(self):
        x_verts = []
        y_verts = []
        z_verts = []

        ## Get the vertices from the template blockmeshdict (this ranges from -1,1 for x,y and z)
        for i in self.blockMeshDict['vertices']:
            x_verts.append(i[0])
            y_verts.append(i[1])
            z_verts.append(i[2])
        ##Based on the bounding box of the STL, calculate the domain (12 times the bb length in the downwind direction, 4 in the other two )
        dx = (self.stlSolid.bb[1]-self.stlSolid.bb[0])*12
        dy = (self.stlSolid.bb[3]-self.stlSolid.bb[2])*4
        dz = (self.stlSolid.bb[5]-self.stlSolid.bb[4])*4

        ##Enfore some minimum size constraints if the STL geometry is small
        if dx<2.5: dx = 2.5
        if dy<2.5: dy = 2.5
        if dz<2.5: dz = 2.5

        ## Calculate the number of blocks in each direction based on the option baseCellSize of this class
        block_x = math.ceil(dx/float(self.baseCellSize))
        block_y = math.ceil(dy/float(self.baseCellSize))
        block_z = math.ceil(dz/float(self.baseCellSize))

        ## Set the block sizes in blockMeshDict
        self.blockMeshDict['blocks'][2] = [block_x, block_y, block_z]

        ##Then scale the verts, also notice that the box is moved downwind a bit (the x_verts).
        x_verts = (np.array(x_verts) * dx)+((self.stlSolid.bb[1]-self.stlSolid.bb[0])*6)
        y_verts = np.array(y_verts) * dy
        z_verts = np.array(z_verts) * dz
        new_verts = []
        for enu,i in enumerate(x_verts):
            new_verts.append('(%f %f %f)'%(x_verts[enu],y_verts[enu],z_verts[enu]))

        #set the new verts in blockMeshDict
        self.blockMeshDict['vertices'] = new_verts

    def blockMesh(self):
        '''This functions configures and runs blockMeshDict'''

        ## The first step is to configure the domain for blockMeshDict based on the stl file
        self.blockMeshDomain()
        ## That file gets written to file
        self.blockMeshDict.writeFile()
        ## And we run blockMeshDict
        Runner(args=["--silent","blockMesh","-case",self.casePath])
        Runner(args=["--silent","surfaceFeatureExtract","-case",self.casePath])


    def snappyHexMesh(self):
        '''
        This function runs snappyHexMesh for us
        '''
        ## First, lets add a few refinement regions based on the geometry

        ## The first is a box that surrounds the aircraft and extends downwind by three body lengths
        self.snappyHexMeshDict['geometry']['downwindbox'] = {}
        dwBox = self.snappyHexMeshDict['geometry']['downwindbox']
        dwBox['type'] = 'searchableBox'
        boxenlarge = 2.5
        dwBox['min'] = [boxenlarge*self.stlSolid.bb[0],boxenlarge*self.stlSolid.bb[2],boxenlarge*self.stlSolid.bb[4]]
        dwBox['max'] = [boxenlarge*self.stlSolid.bb[1]+4*(self.stlSolid.bb[1]-self.stlSolid.bb[0]),boxenlarge*self.stlSolid.bb[3],boxenlarge*self.stlSolid.bb[5]]

        self.snappyHexMeshDict['castellatedMeshControls']['refinementRegions']['downwindbox']={}
        self.snappyHexMeshDict['castellatedMeshControls']['refinementRegions']['downwindbox']['mode']='inside'
        self.snappyHexMeshDict['castellatedMeshControls']['refinementRegions']['downwindbox']['levels'] = [[1,4]]



        ## Next we add some refinement regions around the wing tips
        self.snappyHexMeshDict['geometry']['wingtip1'] = {}
        wt1Box = self.snappyHexMeshDict['geometry']['wingtip1']
        wt1Box['type'] = 'searchableCylinder'
        wt1Box['point1'] = self.stlSolid.yminPoint
        ## Next point is 6 meters downwind
        wt1Box['point2'] = [sum(x) for x in zip(self.stlSolid.yminPoint, [6,0,0])]
        wt1Box['radius'] = .2

        self.snappyHexMeshDict['castellatedMeshControls']['refinementRegions']['wingtip1']={}
        self.snappyHexMeshDict['castellatedMeshControls']['refinementRegions']['wingtip1']['mode']='inside'
        self.snappyHexMeshDict['castellatedMeshControls']['refinementRegions']['wingtip1']['levels'] = [[1,5]]

        ## Next we add some refinement regions around the wing tips
        self.snappyHexMeshDict['geometry']['wingtip2'] = {}
        wt2Box = self.snappyHexMeshDict['geometry']['wingtip2']
        wt2Box['type'] = 'searchableCylinder'
        wt2Box['point1'] = self.stlSolid.ymaxPoint
        ## Next point is 6 meters downwind
        wt2Box['point2'] = [sum(x) for x in zip(self.stlSolid.ymaxPoint, [6,0,0])]
        wt2Box['radius'] = .2


        self.snappyHexMeshDict['castellatedMeshControls']['refinementRegions']['wingtip2']={}
        self.snappyHexMeshDict['castellatedMeshControls']['refinementRegions']['wingtip2']['mode']='inside'
        self.snappyHexMeshDict['castellatedMeshControls']['refinementRegions']['wingtip2']['levels'] = [[1,5]]

        ## Save the snappyHexMeshDict file
        self.snappyHexMeshDict.writeFile()

        ## We need to know if we should run this in parallel
        if self.parallel:
            ## Ok, running in parallel. Lets first configure the decomposePar dict based on the number of processors we have
            self.decomposeParDict['numberOfSubdomains'] = self.nprocs
            self.decomposeParDict.writeFile()
            ## The we decompose the case (Split up the problem into a few subproblems)
            Runner(args=['--silent',"decomposePar","-force","-case",self.casePath])

            ## Then run snappyHexMesh to build our final mesh for the simulation, also in parallel
            print "Starting snappyHexMesh"
            # Runner(args=['--silent', "--proc=%s"%self.nprocs,"snappyHexMesh","-overwrite","-case",self.casePath])
            Runner(args=["--proc=%s"%self.nprocs,"snappyHexMesh","-overwrite","-case",self.casePath])
            ## Finally, we combine the mesh back into a single mesh. This allows us to decompose it more intelligently for simulation

            Runner(args=['--silent', "reconstructParMesh","-constant","-case",self.casePath])
        else:
            ## No parallel? Ok, lets just run snappyHexMesh
            Runner(args=['--silent' ,"snappyHexMesh","-overwrite","-case",self.casePath])

    def previewMesh(self):
        '''
        Utility function that simply opens the simulation in paraview
        '''
        if not which('paraview'):
            print 'Could not find paraview'
            return
        os.system('paraview %s'%(os.path.join(self.casePath, 'openme.foam')))

if __name__=='__main__':
    import stlTools
    import time
    import Utilities
    Utilities.caseSetup('test')
    stlSolid = stlTools.SolidSTL('../test_dir/benchmarkAircraft.stl')
    stlSolid.setaoa(5, units='degrees')
    stlSolid.saveSTL('test/constant/triSurface/benchmarkAircraft.stl')
    print stlSolid.bb
    a = mesher('test', stlSolid,baseCellSize=0.31)
    a.blockMesh()
    a.snappyHexMesh()
    a.previewMesh()