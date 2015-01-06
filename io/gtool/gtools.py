#import  os,sys
#from    optparse        import OptionParser
#from    cf.util.LOGGER  import *

#from    cf.io.gtool     import gtool
#from    numpy           import concatenate

import  os, operator
from    numpy       import concatenate

from    cf.util     import OrderedDict
from    gtool       import gtool
from    gt_hdr      import __gtHdr__
from    gt_var      import __gtVarMF__


class gtools(object):
    def __init__(self, srcPATH=None, Slice=None):
        '''
        Slice   : slice object to get subset of each gtool data
                  maybe useful when exclude 0th or -1th record
        '''

#        baseDir     = '/data1/hjkim/ELSE/GSWP3/out/GSWP3.E1FT/'
#        varName     = 'runoffgw'
#        srcPATH     = [os.path.join(baseDir,'GSWP3.%i'%y,varName) for y in range(2000,2004)]

        '''
        for srcPath in srcPATH:
            print srcPath
            if not os.path.exists(srcPath):
                raise ValueError, '%s does not exist.'%srcPath
        '''

        self.Slice  = Slice if Slice != None else slice(None,None,None)

        self.gtFILE = [gtool(s, 'r') for s in srcPATH]

        varNAME     = self.gtFILE[0].vars.keys()

        self.vars   = OrderedDict()
        for varName in varNAME:
            self.vars[varName]          = __gtVarMF__( self.merge_header(varName),
                                                       self.get_gtVars(varName) )
        '''
        print self.vars[varName.upper()][100:-30].shape
        print self.vars[varName.upper()][3:3]
        print self.vars[varName.upper()][4].shape


        return

        print DTime
        print TIME
        print self.gtFILE[0].vars[varName.upper()].header
        print 'NEXT '*10
        print self.gtFILE[0].vars[varName.upper()].UTIM
        '''


    def merge_header(self, varName):

        header  = reduce( operator.add, [gt.vars[varName].header for gt in self.gtFILE] )
        return header


    def get_gtVars(self, varName):

        gtVars  = [gt.vars[varName] for gt in self.gtFILE]
        return gtVars

