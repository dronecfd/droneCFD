##########################################################################################
##  _______  .______        ______   .__   __.  _______      ______  _______  _______   ##
## |       \ |   _  \      /  __  \  |  \ |  | |   ____|    /      ||   ____||       \  ##
## |  .--.  ||  |_)  |    |  |  |  | |   \|  | |  |__      |  ,----'|  |__   |  .--.  | ##
## |  |  |  ||      /     |  |  |  | |  . `  | |   __|     |  |     |   __|  |  |  |  | ##
## |  '--'  ||  |\  \----.|  `--'  | |  |\   | |  |____    |  `----.|  |     |  '--'  | ##
## |_______/ | _| `._____| \______/  |__| \__| |_______|    \______||__|     |_______/  ##
##                                                                                      ##
##########################################################################################
__author__ = 'cpaulson'

from droneCFD import Utilities
from droneCFD import stlTools
from droneCFD import Meshing
from droneCFD import Solver


## Set true if you want to preview the process at each stage (Opens mesh/results externally in Paraview)
preview = False


## Case setup will configure a directory for an OpenFoam run
case = Utilities.caseSetup('test')


## This manages the STL file. This includes the option to scale and rotate the geometry.
model = stlTools.SolidSTL(case.stlPath)
## Rotate the geometry to the correct aoa for the simulation
model.setaoa(5, units='degrees')
## Save the Modified geometry to disk
model.saveSTL(case.stlPath)

## Meshing will execute blockMeshDict and snappyHexMesh to create the mesh for simulation
mesh = Meshing.mesher(case.dir, model)
## Run blockMesh to generate the simulation domain
mesh.blockMesh()
## Used snappyHexMesh to refine the domain and subtract out regions around the geometry
mesh.snappyHexMesh()
## Display the mesh in a Paraview preview window
if preview:
    mesh.previewMesh()

solver = Solver.solver(case.dir)
if preview:
    ## Call the mesh function again, but Paraview will find the solver results in the case directory
    mesh.previewMesh()