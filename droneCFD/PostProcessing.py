__author__ = 'chrispaulson'

# The force log paring code came from protarius on http://www.cfd-online.com/Forums/openfoam-post-processing/79474-how-plot-forces-dat-file-all-brackets.html

import re
import numpy as np
import glob
import xlsxwriter
import os
import math

class PostProcessing():
    def __init__(self, casedir, parserArgs=None):
        self.casedir = casedir
        self.parserArgs = parserArgs
        workbook = xlsxwriter.Workbook(os.path.join(self.casedir,'RunSummary.xlsx'))
        globalResults = workbook.add_worksheet('Global Results')
        chartGR = workbook.add_chart({'type': 'scatter','subtype': 'straight'})
        grRow = 0
        grCol = 0
        for set in glob.glob(self.casedir):
            print set
            if not os.path.isdir(set):
                continue
            run = set.split('/')[-1]
            worksheet = workbook.add_worksheet(run)
            column = 0
            row = 0
            chartLift = workbook.add_chart({'type': 'scatter','subtype': 'straight'})
            chartDrag = workbook.add_chart({'type': 'scatter','subtype': 'straight'})
            for aoa in glob.glob(set+'/*'):
                print aoa
                aoatmp = float(aoa.split('/')[-1].split('_')[-1])
                print aoatmp
                tmp = worksheet.write(row, column, str(aoatmp) + ' Simulation Time')
                tmp = worksheet.write(row, column+1, str(aoatmp) + ' Drag')
                tmp = worksheet.write(row, column+2, str(aoatmp) + ' Lift')
                row +=1
                pipefile=open(aoa+'/postProcessing/forces/0/forces.dat','r')
                data = []
                for line in pipefile:
                    line = line.translate(None, '()')
                    lineData = line.split()
                    if len(lineData)>10:
                        data.append(np.array(lineData, dtype='float'))

                data =  np.array(data)
                startCellTime = xlsxwriter.utility.xl_rowcol_to_cell(row, column,row_abs=True, col_abs=True)
                startCellDrag = xlsxwriter.utility.xl_rowcol_to_cell(row, column+1,row_abs=True, col_abs=True)
                startCellLift = xlsxwriter.utility.xl_rowcol_to_cell(row, column+2,row_abs=True, col_abs=True)
                for i in data:
                    tmp = worksheet.write(row, column, i[0])
                    tmp = worksheet.write(row, column+1, i[1]+i[4])
                    tmp = worksheet.write(row, column+2, i[3]+i[6])
                    row +=1
                endCellTime = xlsxwriter.utility.xl_rowcol_to_cell(row, column,row_abs=True, col_abs=True)
                endCellDrag = xlsxwriter.utility.xl_rowcol_to_cell(row, column+1,row_abs=True, col_abs=True)
                endCellLift = xlsxwriter.utility.xl_rowcol_to_cell(row, column+2,row_abs=True, col_abs=True)
                chartLift.add_series({'name': '{0}'.format(aoatmp), 'categories':'={0}!{1}:{2}'.format(run,startCellTime,endCellTime), 'values':'={0}!{1}:{2}'.format(run,startCellLift, endCellLift)})
                chartDrag.add_series({'name':'{0}'.format(aoatmp), 'categories':'={0}!{1}:{2}'.format(run,startCellTime,endCellTime), 'values':'={0}!{1}:{2}'.format(run,startCellDrag, endCellDrag)})
                column+=3
                row = 0
                avgLength = 15
                a = math.sin(math.radians(aoatmp))
                b = math.cos(math.radians(aoatmp))
                zForce = np.mean(data[-avgLength:,3]+data[-avgLength:,6])
                xForce = np.mean(data[-avgLength:,1]+data[-avgLength:,4])
                planeRefLift = b*zForce + a*xForce
                planeRefDrag = b*xForce + a*zForce
                tmp = globalResults.write(grRow, grCol, aoatmp)
                tmp = globalResults.write(grRow, grCol+1, planeRefLift)
                tmp = globalResults.write(grRow, grCol+2, planeRefDrag)
                grRow+=1
            grCol+=3
            grRow=0
            chartLift.set_y_axis({'date_axis': False,'min': -15,'max': 30,})
            chartDrag.set_y_axis({'date_axis': False,'min': 0,'max': 10,})
            worksheet.insert_chart('A1', chartLift)
            worksheet.insert_chart('I1', chartDrag)


        workbook.close()





