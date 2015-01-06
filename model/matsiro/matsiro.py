#! /usr/bin/python
#--------------------------------------------------------------------
# PROGRAM    : MATSIRO.py
# CREATED BY : hjkim @IIS.2014-01-27 15:19:42.595514
# MODIFED BY :
#
# USAGE      : $ ./MATSIRO.py
#
# DESCRIPTION:
#------------------------------------------------------cf0.2@20120401


import  os,sys
from    optparse        import OptionParser
from    cf.util.LOGGER  import *

from    cf.io.gtool     import gtool
from    cf.util         import OrderedDict


class gt_file_list(list):
    def __getitem__(self,fName):
        srcPath = os.path.join(self.srcDir,fName)

        return gtool(srcPath)


class yearlyOut(object):
    def __init__(self,srcDir):
        excludeList = ['SYSIN','SYSOUT','ERROUT']

        fNames        = gt_file_list()
        fNames.srcDir = srcDir

        for fName in os.listdir(srcDir):
            if fName.split('.')[0] in excludeList:
                continue

            elif os.path.isdir( os.path.join(srcDir,fName) ):
                self.__dict__[fName]    = yearlyOut( os.path.join(srcDir,fName) )

            else:
                fNames.append(fName)

        self.files  = fNames


class MATSIRO(object):
    def __init__(self,srcInfo):
        '''
        srcInfo : directory or runscript


        dir. structure should follow @baseDir/prjName.subPrjName/year/var
        '''

        if not os.path.exists(srcInfo):
            raise ValueError('%s not exists'%srcInfo)

        if os.path.isdir(srcInfo):
            baseDir = srcInfo
            prjName = os.path.normpath(baseDir).split('/')[-1]

            timeDirs = []
            VAR     = []

            for dirName in os.listdir(baseDir):
                if dirName.isdigit():
                    timeDirs.append( int(dirName) )

                    VAR.extend(os.listdir( os.path.join(baseDir,dirName) ))

            timeDirs = sorted(timeDirs)
            VAR     = sorted( set(VAR) )

        else:
            print 'this is runscript.'


        self.prjName    = prjName
        self.baseDir    = baseDir
        self.timeDirs   = timeDirs

        return


    def __getitem__(self,year):

        if year in self.timeDirs:
            srcDir  = os.path.join( self.baseDir, str(year) )

            return yearlyOut(srcDir)

        else:
            raise KeyError, 'Year %i is not in target years: %s'%(year,self.timeDirs)


@ETA
def main(args,opts):
    print args
    print opts

    srcDir  = '/tank/test/MIROC5.0_mizu/out/JL1.Prcp_GPCCFGLW90/'
    srcDir  = '/tank/hjkim/ELSE/agcm5.6/out/JL1.Prcp_GPCCFG/'

    mat = MATSIRO(srcDir)

    print dir(mat)
    print
    print mat.timeDirs
    print mat.baseDir
    print mat.prjName

    return


if __name__=='__main__':
    usage   = 'usage: %prog [options] arg'
    version = '%prog 1.0'

    parser  = OptionParser(usage=usage,version=version)

#    parser.add_option('-r','--rescan',action='store_true',dest='rescan',
#                      help='rescan all directory to find missing file')

    (options,args)  = parser.parse_args()

#    if len(args) == 0:
#        parser.print_help()
#    else:
#        main(args,options)

    LOG     = LOGGER()
    main(args,options)


