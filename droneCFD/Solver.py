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
from PyFoam.RunDictionary.ParsedParameterFile import ParsedParameterFile
from PyFoam.Applications.Runner import Runner
from PyFoam.Applications.PlotRunner import PlotRunner
import shutil
import glob
import Utilities

class solver():

    def __init__(self, casedir,nprocs=None, parserArgs=None):
        self.casePath = casedir
        self.procsUtil = Utilities.parallelUtilities(nprocs)
        self.decomposeParDict = ParsedParameterFile(os.path.join(self.casePath,'system','decomposeParDict'))
        if parserArgs:
            self.modifyDicts(parserArgs)

        if self.procsUtil.procs > 1:
            self.parallel = True
            self.nprocs = self.procsUtil.procs
            print 'Using %s processors based on procsUtil'%self.nprocs
            self.decomposeParDict['numberOfSubdomains'] = self.nprocs
            self.decomposeParDict.writeFile()
        else:
            self.parallel = False
            self.nprocs = 1
        if self.parallel:
            for file in glob.glob(self.casePath+'/processor*'):
                shutil.rmtree(file)
            Runner(args=["decomposePar","-case",self.casePath])
            Runner(args=["--proc=%s"%self.nprocs,"potentialFoam","-case",self.casePath,"-noFunctionObjects"])
            Runner(args=["--proc=%s"%self.nprocs,"simpleFoam","-case",self.casePath])
            Runner(args=["reconstructParMesh", "-mergeTol", "1e-6", "-constant", "-case", self.casePath])
            Runner(args=["reconstructPar", "-case", self.casePath])
            for file in glob.glob(self.casePath+'/processor*'):
                shutil.rmtree(file)
        else:
            runner = Runner(args=["simpleFoam","-case",self.casePath])

    def modifyDicts(self, parserArgs):
        if parserArgs.airspeed:
            file = ParsedParameterFile(os.path.join(self.casePath,'0','U'))
            file['internalField'].val.vals[0]=parserArgs.airspeed
            file.writeFile()

            file = ParsedParameterFile(os.path.join(self.casePath,'system','controlDict'))
            file['functions']['forces']['magUInf'] = parserArgs.airspeed
            file['functions']['forceCoeffs1']['magUInf'] = parserArgs.airspeed
            file.writeFile()

        if parserArgs.cofg:
            file = ParsedParameterFile(os.path.join(self.casePath,'system','controlDict'))
            file['functions']['forces']['CofR'].vals[0] = parserArgs.cofg
            file['functions']['forceCoeffs1']['CofR'].vals[0] = parserArgs.cofg
            file.writeFile()

        if parserArgs.refarea:
            file = ParsedParameterFile(os.path.join(self.casePath,'system','controlDict'))
            file['functions']['forces']['Aref'] = parserArgs.refarea
            file['functions']['forceCoeffs1']['Aref'] = parserArgs.refarea
            file.writeFile()

        # if parserArgs.Lref:
        #     file = ParsedParameterFile(os.path.join(self.casePath,'system','controlDict'))
        #     file['functions']['forces']['CofR'].vals[0] = parserArgs.cofg
        #     file['functions']['forceCoeffs1']['CofR'].vals[0] = parserArgs.cofg
        #     file.writeFile()

        if parserArgs.convergence:
            file = ParsedParameterFile(os.path.join(self.casePath,'system','fvSolution'))
            for i in file['SIMPLE']['residualControl']:
                file['SIMPLE']['residualControl'][i]=parserArgs.convergence
            file.writeFile()


if __name__=='__main__':
    s = solver('test')
    print s.a['addLayersControls']
