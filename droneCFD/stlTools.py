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
## Based on arizonat/py-stl-toolkit on github: https://github.com/arizonat/py-stl-toolkit/

import struct
import numpy as np
import math
from stl import stl as stl


class solidSTL():
    def __init__(self, fp):
        print fp
        self.mesh = stl.StlMesh(fp)
        self.boundingBox()
        self.centerGeometry()

    def boundingBox(self):
        xmin = self.mesh.x.min()
        xmax = self.mesh.x.max()
        ymin = self.mesh.y.min()
        ymax = self.mesh.y.max()
        zmin = self.mesh.z.min()
        zmax = self.mesh.z.max()
        self.bb = [xmin, xmax, ymin, ymax, zmin, zmax]

        where = np.where(self.mesh.data['vectors']==ymax)
        self.ymaxPoint = self.mesh.data['vectors'][where[0][0]][where[1][0]]

        where = np.where(self.mesh.data['vectors']==ymin)
        self.yminPoint = self.mesh.data['vectors'][where[0][0]][where[1][0]]

    def translate(self, dx=0, dy=0, dz=0):
        self.mesh.data['vectors'] = self.mesh.data['vectors'] + [dx,dy,dz]

    def centerGeometry(self):
        self.boundingBox()
        dx = self.bb[1]-self.bb[0]
        dy = self.bb[3]-self.bb[2]
        dz = self.bb[5]-self.bb[4]
        self.translate(dx=-1*(dx/2.+self.bb[0]), dy=-1*(dy/2.+self.bb[2]), dz=-1*(dz/2.+self.bb[4]))

    def scale(self, x=1,y=1,z=1):
        self.mesh.data['vectors'] = self.mesh.data['vectors'] * [x,y,z]

    def save(self, fp):
        self.mesh.save(fp, mode=2, update_normals=True)

    def setaoa(self, aoa, units="degrees"):
        self.rotate(y=aoa, units=units)

    def rotate(self, z=0, y=0, x=0, units="degrees"):
        if units == 'degrees':
            z = np.radians(z)
            y = np.radians(y)
            x = np.radians(x)
        elif units =='radians':
            z = z
            y = y
            x = x
        else:
            return
        rm = self.euler2mat(z,y,x)
        for i in range(self.mesh.data['vectors'].shape[0]):
            self.mesh.data['vectors'][i][0] = np.dot(self.mesh.data['vectors'][i][0], rm.T)
            self.mesh.data['vectors'][i][1] = np.dot(self.mesh.data['vectors'][i][1], rm.T)
            self.mesh.data['vectors'][i][2] = np.dot(self.mesh.data['vectors'][i][2], rm.T)

    def euler2mat(self, z=0, y=0, x=0):
        Ms = []
        if z:
            cosz = math.cos(z)
            sinz = math.sin(z)
            Ms.append(np.array(
                    [[cosz, -sinz, 0],
                     [sinz, cosz, 0],
                     [0, 0, 1]]))
        if y:
            cosy = math.cos(y)
            siny = math.sin(y)
            Ms.append(np.array(
                    [[cosy, 0, siny],
                     [0, 1, 0],
                     [-siny, 0, cosy]]))
        if x:
            cosx = math.cos(x)
            sinx = math.sin(x)
            Ms.append(np.array(
                    [[1, 0, 0],
                     [0, cosx, -sinx],
                     [0, sinx, cosx]]))
        if Ms:
            return reduce(np.dot, Ms[::-1])
        return np.eye(3)

    def getWingtip(self):
        return self.ymaxPoint


if __name__ == "__main__":
    model = newSTL('data/geometries/benchmarkAircraft.stl', )
    model.centerGeometry()
    model.setaoa(5)
    model.boundingBox()
    model.save('translated.stl')
