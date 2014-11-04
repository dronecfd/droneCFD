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
from stl import stl as newstl

class SolidSTL(object):

    def __init__(self, filepath, parserArgs=None):

        self.filepath = filepath

        try:
            self.title, self.triangles, self.norms = self.loadSTL(self.filepath)
        except Exception as e:
            print e
            try:
                self.title, self.triangles, self.norms, self.bytecount = self.loadBSTL(self.filepath)
            except Exception as e:
                print e
                print 'Couldnt open the STL file'
                exit()
            else:
                print 'Loaded Binary STL file'
        else:
            print 'Loaded ASCII STL File'

        if not self.triangles:
            self.triangles = []
        if not self.norms:
            self.norms = []
        self.vertices = self.__getVertices()
        self.centerGeometry()

    def iterTriangles(self):
        for i in xrange(len(self.triangles)):
            yield self.triangles[i], self.norms[i]

    def __getVertices(self):
        """
        WARNING: THIS IS THE NUMBER OF TRIANGLE EDGES, NOT THE OVERALL EDGES OF THE SOLID
        """
        self.vertices = set()
        for triangle in self.triangles:
            for vertex in triangle:
                self.vertices.add(vertex)

        return self.vertices

    def loadBSTL(self,bstl):
        """
        Loads triangles from file, input can be a file path or a file handler
        Returns a SolidSTL object
        """

        if isinstance(bstl, file):
            f = bstl
        elif isinstance(bstl, str):
            f = open(bstl, 'rb')
        else:
            raise TypeError("must be a string or file")

        header = f.read(80)
        numTriangles = struct.unpack("@i", f.read(4))
        numTriangles = numTriangles[0]

        triangles = [(0,0,0)]*numTriangles # prealloc, slightly faster than append
        norms = [(0,0,0)]*numTriangles
        bytecounts = [(0,0,0)]*numTriangles

        for i in xrange(numTriangles):
            # facet records
            norms[i] = struct.unpack("<3f", f.read(12))
            vertex1 = struct.unpack("<3f", f.read(12))
            vertex2 = struct.unpack("<3f", f.read(12))
            vertex3 = struct.unpack("<3f", f.read(12))
            bytecounts[i] = struct.unpack("H", f.read(2)) # not sure what this is

            triangles[i] = (vertex1, vertex2, vertex3)

        return header, triangles, norms, bytecounts


    def loadSTL(self, infilename):

        with open(infilename,'r') as f:
            name = f.readline().split()
            if not name[0] == "solid":
                raise IOError("Expecting first input as \"solid\" [name]")

            if len(name) == 2:
                title = name[1]
            elif len(name) == 1:
                title = None
            else:
                raise IOError("Too many inputs to first line")

            triangles = []
            norms = []

            for line in f:
                params = line.split()
                cmd = params[0]
                if cmd == "endsolid":
                    if name and params[1] == name:
                        break
                    else: #TODO: inform that name needs to be there
                        break
                elif cmd == "facet":
                    norm = map(float, params[2:5])
                    norms.append(tuple(norm))
                elif cmd == "outer":
                    triangle = []
                elif cmd == "vertex":
                    vertex = map(float, params[1:4])
                    triangle.append(tuple(vertex))
                elif cmd == "endloop":
                    continue
                elif cmd == "endfacet":
                    triangles.append(tuple(triangle)) #TODO: Check IO formatting
                    triangle = []

            return title, triangles, norms

    def centerGeometry(self):
        bb = self.boundingBox()
        ##Find the center of the bb

        dx = bb[1]-bb[0]
        dy = bb[3]-bb[2]
        dz = bb[5]-bb[4]


        self.translate( x=-1*(dx/2.+bb[0]), y=-1*(dy/2.+bb[2]), z=-1*(dz/2.+bb[4]))

        bb = self.boundingBox()
        ##Find the center of the bb
        dx = bb[1]-bb[0]
        dy = bb[3]-bb[2]
        dz = bb[5]-bb[4]
        self.bb = bb


    def boundingBox(self):
        xmin = None
        xmax = None
        ymin = None
        ymax = None
        zmin = None
        zmax = None
        for i in xrange(len(self.triangles)):

            triangle = list(self.triangles[i])
            for v in xrange(len(triangle)):
                triangle[v] = list(triangle[v])
                if xmax ==None:
                    xmin = triangle[v][0]
                    xmax = triangle[v][0]
                    ymin = triangle[v][1]
                    ymax = triangle[v][1]
                    zmin = triangle[v][2]
                    zmax = triangle[v][2]

                if triangle[v][0] < xmin:
                    xmin = triangle[v][0]
                if triangle[v][0] > xmax:
                    xmax = triangle[v][0]

                if triangle[v][1] < ymin:
                    ymin = triangle[v][1]
                    self.yminPoint = triangle[v]

                if triangle[v][1] > ymax:
                    ymax = triangle[v][1]
                    self.ymaxPoint = triangle[v]

                if triangle[v][2] < zmin:
                    zmin = triangle[v][2]
                if triangle[v][2] > zmax:
                    zmax = triangle[v][2]
        self.bb = [xmin, xmax, ymin, ymax, zmin, zmax]
        print self.bb
        return self.bb

    def getWingtip(self):
        return self.ymaxPoint

    def translate(self, x=0, y=0, z=0):
        for i in xrange(len(self.triangles)):
            triangle = list(self.triangles[i])

            for v in xrange(len(triangle)):
                triangle[v] = list(triangle[v])
                triangle[v][0] = x + triangle[v][0]
                triangle[v][1] = y + triangle[v][1]
                triangle[v][2] = z + triangle[v][2]
                triangle[v] = tuple(triangle[v])

            self.triangles[i] = tuple(triangle)


    def setaoa(self, aoa, units="degrees"):
        # TODO: Patch this up
        if units == 'degrees':
            aoa = np.radians(aoa)
        elif units =='radians':
            aoa = aoa
        else:
            return

        rm = self.euler2mat(y=aoa)

        for i in xrange(len(self.triangles)):
            triangle = list(self.triangles[i])

            for v in xrange(len(triangle)):
                triangle[v] = list(triangle[v])

                triangle[v] = tuple(np.dot(triangle[v], rm.T))

            self.triangles[i] = tuple(triangle)

    def rotate(self, z=0, y=0, x=0, units="degrees"):
        '''
        A function to manage rotations of the geometry
        :param z: rotation amount around the z asix
        :param y: rotation amount around the y axis
        :param x: rotation amount around the x axis
        :param units: set units, valid options are degrees or radians
        '''

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

        ## build a rotation matrix
        rm = self.euler2mat(z=z, y=y, x=x)

        ## Rotate each vertex in the geometry
        for i in xrange(len(self.triangles)):
            triangle = list(self.triangles[i])

            for v in xrange(len(triangle)):
                triangle[v] = list(triangle[v])

                triangle[v] = tuple(np.dot(triangle[v], rm.T))

            self.triangles[i] = tuple(triangle)

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


    def scale(self, x,y,z):
        for i in xrange(len(self.triangles)):
            triangle = list(self.triangles[i])

            for v in xrange(len(triangle)):
                triangle[v] = list(triangle[v])
                triangle[v][0] = x * triangle[v][0]
                triangle[v][1] = y * triangle[v][1]
                triangle[v][2] = z * triangle[v][2]
                triangle[v] = tuple(triangle[v])

            self.triangles[i] = tuple(triangle)




    # from (will be modified soon)
    # http://stackoverflow.com/questions/7566825/python-parsing-binary-stl-file
    def saveSTL(self, outfilename):
        """
        Saves the solid in standard STL format
        """

        triangles = self.triangles
        norms = self.norms

        with open(outfilename, "w") as f:

            f.write("solid "+outfilename+"\n")
            for i in xrange(len(triangles)):
                norm = norms[i]
                triangle = triangles[i]
                f.write("facet normal %f %f %f\n"%(norm))
                f.write("outer loop\n")
                f.write("vertex %f %f %f\n"%triangle[0])
                f.write("vertex %f %f %f\n"%triangle[1])
                f.write("vertex %f %f %f\n"%triangle[2])
                f.write("endloop\n")
                f.write("endfacet\n")
            f.write("endsolid "+outfilename+"\n")




class newSTL():
    def __init__(self, fp):
        print fp
        self.mesh = newstl.StlMesh(fp)

    def boundingBox(self):
        xmin = self.mesh.x.min()
        xmax = self.mesh.x.max()
        ymin = self.mesh.y.min()
        ymax = self.mesh.y.max()
        zmin = self.mesh.z.min()
        zmax = self.mesh.z.max()
        self.bb = [xmin, xmax, ymin, ymax, zmin, zmax]

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


if __name__ == "__main__":
    # stl = SolidSTL('data/geometries/benchmarkAircraft.stl')
    # stl.boundingBox()
    stl1 = newSTL('data/geometries/benchmarkAircraft.stl', )
    stl1.centerGeometry()
    stl1.setaoa(15)
    stl1.save('translated.stl')
