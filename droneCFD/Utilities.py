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

import shutil
import os
import PyFoam.Basics.STLFile as pySTL
import multiprocessing

## Utilities is responsible for setting up our test directory

class caseSetup():
    def __init__(self, folderPath, geometryPath=None, templatePath=None, parserArgs=None):

        ##Check if this gets args from the droneCFD_Run command
        if parserArgs:
            geometryPath = parserArgs.geometryPath

        ## Double check that a destination folder is set
        if folderPath is None:
            print 'Please specify a folder path, exiting...'
            exit()

        if templatePath is None:
            self.templatePath = os.path.dirname(__file__)+'/data/template'
            print 'Template File Path is: {0}'.format(self.templatePath)

        if geometryPath is None:
            ## Default to the base geometry
            geometryPath = os.path.dirname(__file__)+'/data/geometries/benchmarkAircraft.stl'

        ## Since the path exists, lets make sure that folder doesn't exist
        #TODO: Don't just delete a folder without asking for permission
        self.dir = os.path.abspath(folderPath)
        if os.path.isdir(self.dir): shutil.rmtree(self.dir)

        ## A few paths that will be useful later on
        self.triSurface = os.path.join('constant','triSurface')
        self.system = os.path.join('system')
        self.polyMesh = os.path.join('polyMesh')

        ## Now, copy the template directory into our new file location
        ## The template path is hard coded for now, but you can opt to introduce your own
        # self.templatePath = os.path.abspath(templatePath)
        self.copyTemplate(self.templatePath)

        ## Set geometry if supplied, move it into place
        if geometryPath:
            self.geometryPath = os.path.abspath(geometryPath)
            self.setGeometry(self.geometryPath)


    def copyTemplate(self, path):
        if not os.path.isdir(path):
            print 'The template path %s is missing. Please check the location and try again, exiting...'%path
            exit()
        if not os.path.isdir(os.path.join(path, self.triSurface)) and os.path.isdir(os.path.join(path, self.system)):
            print 'Template is not of the correct form. Please check. Exiting...'
            exit()
        ## Transfer the template directory into place
        shutil.copytree(path,self.dir)
        self.templatePath = path

    def setGeometry(self, path):
        self.geo_base_path = path
        print
        ## Double check that this is actually a file
        if not os.path.isfile(self.geo_base_path):
            print 'Geometry missing... Exiting... '
            exit()

        ## Now parse the STL file to double check that it's valid, we'll need this data later anyway
        print self.geo_base_path
        stl_file = pySTL.STLFile(fName=self.geo_base_path)

        try:
            self.patchinfo =  stl_file.patchInfo()
        except:
            print 'Please make sure your STL file is in ascii format, hoping to add binary soon'
            exit()
        if len(self.patchinfo)>1:
            print 'Make sure there is only one geometry in your STL file'
            exit()
        self.patchinfo = self.patchinfo[0]
        self.stl = {'patchName':self.patchinfo['name'], 'bb_min':self.patchinfo['min'], 'bb_max':self.patchinfo['max']}
        ## Finally, we can copy the STL file into place.
        shutil.copy(path, os.path.join(self.dir, self.triSurface))
        self.stlPath = os.path.join(self.dir, self.triSurface, os.path.basename(self.geo_base_path))
        #Rename the stl geometry to work with the OpenFoam Template
        shutil.move(self.stlPath, os.path.join(self.dir, self.triSurface, 'Aircraft.stl'))
        self.stlPath = os.path.join(self.dir, self.triSurface, 'Aircraft.stl')


class parallelUtilities():
    def __init__(self, procs=None):
        if not procs:
            print 'Evaluating computation hardware'
            self.procs = multiprocessing.cpu_count()
        else:
            print 'Running on user specified number of processors'
            self.procs = procs
            if self.procs > multiprocessing.cpu_count():
                print 'Warning: Number of requested cores is greater than the local core count'
        print "Using %s processors for computation"%self.procs



if __name__=='__main__':
    a = parallelUtilities()
    b = parallelUtilities(procs=1)
    b = parallelUtilities(procs=2)
    b = parallelUtilities(procs=4)

    # u = caseSetup(folderPath='test', geometryPath='../test_dir/benchmarkAircraft.stl')
