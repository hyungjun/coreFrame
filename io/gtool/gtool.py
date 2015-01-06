#import os,sys,datetime
#from numpy          import frombuffer,array,empty,unpackbits,invert,ma,ndarray
#from numpy          import dtype as DType
#from cf.util        import OrderedDict,key2slice
#from cf.io          import fIO
#from cf.TimeSeries  import TSData,det_delT

#import struct,time
import os,datetime
from numpy          import dtype as DType
from numpy          import array,frombuffer

from cf.util        import OrderedDict
from cf.io          import fIO

from gt_hdr         import __gtHdr__
from gt_var         import __gtVarRead__, __gtVarNew__


class gtool(object):
    '''
    gt=GT(path, iomode,unit)

        * iomode : [
                    'r',    # read
                    'w',    # write
                    'ow'    # over write
                    ]

    # access ATTR
    gt.header[varName].DATE = '19990101 000000'
    gt.header[varName].UTIM = 'HOUR'        # ['HOUR','DAY'] only
    gt.header[varName].TDUR = 24

    gt.data = array()


    ******
    HEADER
    ******
    1  "IDFM":[int,"%16i",9010],                # req
    2  "DSET":[str,"%-16s",''],
    3  "ITEM":[str,"%-16s",''],                 # req
    4  "EDIT1":[str,"%-16s",''],
    5  "EDIT2":[str,"%-16s",''],
    6  "EDIT3":[str,"%-16s",''],
    7  "EDIT4":[str,"%-16s",''],
    8  "EDIT5":[str,"%-16s",''],
    9  "EDIT6":[str,"%-16s",''],
    10 "EDIT7":[str,"%-16s",''],
    11 "EDIT8":[str,"%-16s",''],
    12 "FNUM":[int,"%16i",1],
    13 "DNUM":[int,"%16i",1],
    14 "TITL1":[str,"%-16s",''],
    15 "TITL2":[str,"%-16s",''],
    16 "UNIT":[str,"%-16s",''],
    17 "ETTL1":[str,"%-16s",''],
    18 "ETTL2":[str,"%-16s",''],
    19 "ETTL3":[str,"%-16s",''],
    20 "ETTL4":[str,"%-16s",''],
    21 "ETTL5":[str,"%-16s",''],
    22 "ETTL6":[str,"%-16s",''],
    23 "ETTL7":[str,"%-16s",''],
    24 "ETTL8":[str,"%-16s",''],
    25 "TIME":[int,"%16i",0],
    26 "UTIM":[str,"%-16s",'HOUR'],
    27 "DATE":[str,"%-16s",'00000000 000000'],  # req
    28 "TDUR":[int,"%16i",0],
    29 "AITM1":[str,"%-16s",''],                # req
    30 "ASTR1":[int,"%16i",0],                  # req
    31 "AEND1":[int,"%16i",0],                  # req
    32 "AITM2":[str,"%-16s",''],                # req
    33 "ASTR2":[int,"%16i",0],                  # req
    34 "AEND2":[int,"%16i",0],                  # req
    35 "AITM3":[str,"%-16s",''],                # req
    36 "ASTR3":[int,"%16i",0],                  # req
    37 "AEND3":[int,"%16i",0],                  # req
    38 "DFMT":[str,"%-16s",''],
    39 "MISS":[float,"%16.7e",-999.],
    40 "DMIN":[float,"%16.7e",-999.],
    41 "DMAX":[float,"%16.7e",-999.],
    42 "DIVL":[float,"%16.7e",-999.],
    43 "DIVL":[float,"%16.7e",-999.],
    44 "STYP":[int,"%16i",1],
    45 "COPTN":[str,"%-16s",''],
    46 "IOPTN":[int,"%16i",0],
    47 "ROPTN":[float,"%16.7e",0.],
    48 "DATE1":[str,"%-16s",''],
    49 "DATE2":[str,"%-16s",''],
    50 "MEMO1":[str,"%-16s",''],
    51 "MEMO2":[str,"%-16s",''],
    52 "MEMO3":[str,"%-16s",''],
    53 "MEMO4":[str,"%-16s",''],
    54 "MEMO5":[str,"%-16s",''],
    55 "MEMO6":[str,"%-16s",''],
    56 "MEMO7":[str,"%-16s",''],
    57 "MEMO8":[str,"%-16s",''],
    58 "MEMO9":[str,"%-16s",''],
    59 "MEMO10":[str,"%-16s",''],
    60 "CDATE":[str,"%-16s",''],
    61 "CSIGN":[str,"%-16s",''],
    62 "MDATE":[str,"%-16s",''],
    63 "MSIGN":[str,"%-16s",''],
    64 "SIZE":[int,"%16i",0]
    '''

    def __init__(self,srcPath,mode='r',dtype='float32',dtypeOut='float64',unit=9,mask=None):

        self.srcPath = srcPath
        self.mode    = mode
        self.unit    = unit
        self.iomode  = 'unformatted'

        self.data    = None
        self.hdr     = None

        # add overwrite 'ow' option
        if mode == 'r':
            gtFile  = open(srcPath,'rb')
            fSize   = os.path.getsize(srcPath)

            '''
            s=time.time()
            SEEK,SIZE   = self.scan_struc2(gtFile,fSize)
            print time.time()-s
            return
            '''
            SEEK,SIZE   = self.scan_struc(gtFile,fSize)
            Header      = self.read_header(gtFile,SEEK)

#            self.header = Header
            self.vars   = OrderedDict(
                                      [(k,__gtVarRead__(gtFile,SEEK,SIZE,hdr))
                                                    for k,hdr in Header.items()]
                            )


        elif mode in ['w','ow']:
            if mode == 'w' and os.path.exists(srcPath): raise IOError

#            self.header         = OrderedDict()
            self.vars           = OrderedDict()

        else:
            raise IOError, 'not support %s option'%mode


    def __getitem__(self,k):
        if k in self.vars:  return self.vars[k]
        else             :  raise KeyError, 'Variable %s not exists.'


    def __setitem__(self,k,v):

        self.vars[k]    = __gtVarNew__(k,v)
#        self.header[k]  = self.vars[k].header


    def scan_struc(self,File,fSize):

        dtype   = DType('int32').newbyteorder('>')
        nextPnt = 0

        SEEK    = []
        SIZE    = []
        while nextPnt < fSize:
            nByte   = frombuffer(File.read(4),dtype)[0]

            SEEK.append(File.tell())
            SIZE.append(nByte)

            currPnt = File.tell()
            nextPnt = SEEK[-1]+SIZE[-1]+4

            File.seek(nextPnt)

        return SEEK, SIZE


    def scan_struc2(self,File,fSize):
        unpack  = struct.unpack

        dtype   = DType('int32').newbyteorder('>')

        nextPnt = 1032
        File.seek(nextPnt)

        nCnt    = 0
        SEEK    = []
        SIZE    = []
        while nextPnt < fSize:
            nByte   = unpack('>i4',File.read(4))[0]

            SEEK.append( nextPnt+4 )
            SIZE.append(nByte)

            nextPnt = SEEK[-1]+SIZE[-1]+4+1032

            File.seek(nextPnt)
            print nCnt,;nCnt+=1

        return SEEK, SIZE

    def read_header(self,File,SEEK):

        ### READ header ###
        HEADER  = []
        dataIDX = []
        maskIDX = []

        idx     = 0
        while idx < len(SEEK):
            seek    = SEEK[idx]
            File.seek(seek)

            HEADER.append(frombuffer(File.read(1024),'S16'))

            # check DFMT and skip records
#            print 'chk',HEADER[-1][37]
            if HEADER[-1][37][0] == 'M':
                maskIDX.append(idx+2)
                dataIDX.append(idx+3)

                idx += 4

            else:
                maskIDX.append(None)
                dataIDX.append(idx+1)

                idx += 2

        self._header    = HEADER
        #-----------------

        ### PARSE header###
        Header  = OrderedDict()

        for hdr,mIdx,dIdx in map(None,HEADER,maskIDX,dataIDX):
            varName = hdr[2].strip()

            if varName not in Header:
                Header[varName]                     = __gtHdr__(hdr)
                Header[varName].__Header__['TIME']  = []
                Header[varName].__Header__['DATE']  = []
                Header[varName].__Header__['dIdx']  = []  # for data Idx
                Header[varName].__Header__['mIdx']  = []  # for mask Idx

            Header[varName].__Header__['TIME'].append(int(hdr[24]))

            ##########################################
            #!!! TEMPORARY PATCH@20121107.HJKIM !!!  #
            # to consider datetime '00000000 000000 '#
            # year  0000 -> 0001                     #
            # month 00   -> 01                       #
            # day   00   -> 01                       #
            #                                        #

            HeaderDATE  = list(hdr[26])

            if hdr[26].strip() == ''            :   HeaderDATE      = list('00000000 000000 ')

            if ''.join(HeaderDATE[:4]) == '0000':   HeaderDATE[3]   = '1'
            if ''.join(HeaderDATE[4:6])== '00'  :   HeaderDATE[5]   = '1'
            if ''.join(HeaderDATE[6:8])== '00'  :   HeaderDATE[7]   = '1'


            ##########################################
            #!!! TEMPORARY PATCH@20121107.HJKIM !!!  #
            # to consider hour 24 :only allowed 00-23#
            # day   24   -> 00  & day++              #
            if ''.join(HeaderDATE[9:11]) == '24':
                HeaderDATE[9:11]    = '23'
                delT_off            = datetime.timedelta(seconds=3600)

            else:
                delT_off            = datetime.timedelta(seconds=0)


            HeaderDATE  = ''.join(HeaderDATE)

            Header[varName].__Header__['DATE'].append(  datetime.datetime.strptime(HeaderDATE,'%Y%m%d %H%M%S  ')
                                                      + delT_off)
            #
            # ORIGINAL CODE                         #
#            Header[varName].__Header__['DATE'].append(datetime.datetime.strptime(hdr[26],'%Y%m%d %H%M%S  '))
            ##########################################

            Header[varName].__Header__['dIdx'].append(dIdx)
            Header[varName].__Header__['mIdx'].append(mIdx)

        return Header


    def save(self,fUnit):
        os.environ['F_UFMTENDIAN']  = 'big'

        outPath     = self.srcPath
        iErr    = fIO.fopen(fUnit,outPath,self.iomode)

        for varName,var in self.vars.items():

            TIME    = var.header.TIME
            DATE    = var.header.DATE


            HEADER  = []
            for tme,dte in map(None,TIME,DATE):
                var.header.TIME = tme
                ###########################################
                #!!! TEMPORARY PATCH@20121107.HJKIM !!!   #
                # to avoid error in strftime (year < 1900)#
                if dte.year < 1900:
                    dtStamp = '%04d%02d%02d %02d%02d%02d'%(dte.year,dte.month,dte.day,
                                                           dte.hour,dte.minute,dte.second)
                else:
                    dtStamp = dte.strftime('%Y%m%d %H%M%S ')
                ###########################################
#                dtStamp = dte.strftime('%Y%m%d %H%M%S ')
                var.header.DATE = dtStamp

                HEADER.append(var.header.template)

            nData   = len(HEADER)
            HEADER  = array(HEADER)


#            data    = var.data.astype('float32').reshape(iT,-1)
            print HEADER
            print nData
            print var.data.shape
            print var.data.T.shape
            print var.data.reshape(nData,-1).shape
            aOut    = var.data.reshape(nData,-1).astype('float32')
            print aOut.shape

            iErr    = fIO.gtwrite(fUnit,HEADER,aOut)
#            iErr    = fIO.gtwrite(fUnit,HEADER,var.data.astype('float32').reshape(nData,-1))

        iErr    = fIO.fclose(fUnit)


    def gen_TIME(self,date,utim,tdur,nCnt,origin=datetime.datetime(1,1,1,0)):
        sYear   = int(date[:4])
        sMonth  = int(date[4:6])
        sDay    = int(date[6:8])
        sHour   = int(date[9:11])
        sMin    = int(date[11:13])
        sSec    = int(date[13:15])

        sDT     = datetime(sYear,sMonth,sDay,sHour,sMin,sSec)

        if utim == 'DAY':
            DT  = timedelta(days=tdur)
            DATE    = [(sDT+DT*i) for i in range(nCnt)]

        elif utim == 'HOUR':
            DT  = timedelta(hours=tdur)
            DATE    = [(sDT+DT*i) for i in range(nCnt)]

        ### preliminary treatment for monthly time duration ###
        ### POSSIBLY VERY ERROUNOUS!!                       ###
        elif utim == 'MONTH':
            DATE    = []
            for n in range(nCnt):
                nY  = sYear+n/12
                nM  = sMonth+n%12

                if nM > 12:
                    nY += 1
                    nM -= 12

                DATE.append(datetime(nY,nM,15))
        ### ----------------------------------------------- ###

        TIME    = [dt-origin  for dt in DATE]

        if utim == 'DAY':
            TIME = [dt.days for dt in TIME]

        elif utim == 'HOUR':
            TIME = [dt.days*24+dt.seconds/3600 for dt in TIME]

        elif utim == 'MONTH':
            oY  = origin.year
            oM  = origin.month

            nM  = oY*12+oM

            TIME= [dtime.year*12+dtime.month-nM for dtime in DATE]


        DATE    = ['%04d%02d%02d %02d%02d%02d'
                                %(dt.year,dt.month,dt.day,
                                  dt.hour,dt.minute,dt.second)
                                        for dt in DATE]


        return TIME,DATE


### ======= TEST CODE ======= ###
class Chunk(object):
    def __init__(self,f):
        hdr = frombuffer(f.read(1036),'>i4')
        sz  = hdr[-1]
        sk  = f.tell()+sz+4

        self.f  = f
        self.f.seek(sk)

        self.SZ  = os.fstat(f.fileno()).st_size

    def __iter__(self):
        return self

    def next(self):
        if self.SZ == self.f.tell():
            raise StopIteration

        return Chunk(self.f)
### ========================= ###

if __name__=='__main__':
#    from pylab import *

    import os,sys
    from cf.util.LOGGER import *
    del(datetime)
    import datetime

#    LOG     = LOGGER()

#    srcPath = '/data/hjkim/ELSE/JL1/out/JL1.Prcp_GPCC/JL1.2000/GLG'
#    srcPath = '/data/hjkim/ELSE/JL1/out/JL1.Prcp_GPCC/JL1.2000/GRALB'
#    srcPath = '/data/hjkim/ELSE/JL1/in/Prcp_GPCC/Tair/Tair_2000.gt'
#    srcPath = '/export/nas16/kakushin/ISI-MIP/working/boundary_data/t213x6_bdata/grlai.y2000'
    srcPath = '/data1/hjkim/ELSE/JL1/out/JL1.Prcp_GPCC/JL1.2000/Restart'
#    srcPath = '/data/hjkim/ELSE/JL1/out/JL1.Prcp_GPCC/JL1.2000/GLW'


    print srcPath

    gt      = gtool(srcPath)

    for varName,val in gt.vars.items():
        aSrc    = gt[varName][:]
        DTIME   = gt[varName].DATE
        print varName, aSrc.shape,len(DTIME)
        print gt[varName].header


#    print gt.vars, 'gt.vars'
#    print len(gt.vars), 'len(gt.vars)'
#    print gt.vars[varName],'gt.vars[varName]'
#    print gt.vars[varName].header,'gt.vars[varName].header'
#    print type(gt.vars[varName].header),'type(gt.vars[varName].header'


#    figure();imshow(aSrc.mean(0).mean(0));colorbar();show()


    outPath = './test.gt'
    gt2     = gtool(outPath,'ow')

    for varName,val in gt.vars.items():
        aSrc    = gt[varName][:]
        DTIME   = gt[varName].DATE

        print varName, aSrc.shape,len(DTIME),type(DTIME)

#        gt2[varName]        = (aSrc,DTIME)
#        for i,(g,g2) in enumerate(map(None,gt[varName].header.template,gt2[varName].header.template)):
#            print i,g,g2
        gt2[varName]        = (aSrc,DTIME,gt[varName].header.template)
        gt2[varName].DATE   = gt[varName].DATE

        print gt2[varName].header

    gt2.save(20)
