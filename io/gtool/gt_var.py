#import os,sys,datetime
#from numpy          import frombuffer,array,empty,unpackbits,invert,ma,ndarray
#from cf.util        import OrderedDict,key2slice
#from cf.io          import fIO
#from cf.TimeSeries  import TSData,det_delT
#
#import struct,time
import os,datetime
from numpy          import array,empty,frombuffer
from numpy          import arange,ma, concatenate   # __gtVarMF__
from numpy          import dtype as DType

from cf.TimeSeries  import TSData,det_delT

from gt_hdr         import __gtHdr__
from gt_hdr         import __gtHdrFmt__


class __gtVar__(object):

    header  = __gtHdr__()

    def __len__(self):
        return self.shape[0]
#        return len(self.header['DATE'])
#        return len(self.header[-1])


    def __repr__(self):
        return '%s, %s'%(self.header.__Header__['ITEM'].strip(),self.shape)


    def __getattr__(self,k):
        if k in self.header.__Header__:
            return self.header.__Header__[k]

        elif k in self.__dict__:
            return self.__dict__[k]

        else:
            raise KeyError,'Attribute %s not exists.'%k


    def __setattr__(self,k,v):
        if   k not in self.header.__Header__: self.__dict__[k] = v
        elif type(v) in [list,tuple]        : self.__dict__[k] = v
        else                                : self.header.__Header__[k] = __gtHdrFmt__.fmt[k][1]%v


class __gtVarMF__(__gtVar__):
    def __init__(self, header, gtVars):
        self.header     = header

        self.shape      = ( len(self.header['TIME']),
                            int(self.header['AEND3']),
                            int(self.header['AEND2']),
                            int(self.header['AEND1']) )

        self.gtVars     = gtVars


    def __getitem__(self, Slice):
        '''
        only allow slice for 0-axis (t-axis)
        '''

        # check and align Slice obj. ------------------------------------------
#        Slice   = Slice if type(Slice) != int   else slice(Slice,Slice+1,None)

        if type(Slice) == int:
            Slice   = [ slice(Slice,Slice+1,None) ] + [ slice(None) ]*3

        elif type(Slice) == slice:
            Slice   = [ Slice ] + [ slice(None) ]*3

        elif type(Slice) in [tuple, list]:
            Slice   = list(Slice) + [ slice(None) ]*(4-len(Slice))

        else:
            raise TypeError, '%s is wrong type of slice obj.'%Slice
        # ---------------------------------------------------------------------

        slcT    = Slice[0]

        IDX         = arange( len(self.header['TIME']), dtype='int32' )[slcT]

#        if len(IDX) == 0:   return None         # return None for 0-size array

        shape       = ( len(IDX),
                        len( range( int(self.header['AEND3']) )[Slice[1]] ),
                        len( range( int(self.header['AEND2']) )[Slice[2]] ),
                        len( range( int(self.header['AEND1']) )[Slice[3]] ) )

        if 0 in shape:  return None         # return None for 0-size array

        dtype       = self.gtVars[0][0].dtype

        aOut        = empty( shape, dtype=dtype )

        sIdx        = 0
        for var in self.gtVars:
            Idx     = ma.masked_greater_equal(IDX, len(var)).compressed()

            eIdx    = sIdx + len(Idx)

#            print len(self.header['TIME']),Slice[0],len(IDX),Idx[0],Idx[-1]

            # tentative treatment len(1) index -----------------------------
            # should carefully reimplement slicding in __getitem__ @ gt_var.py
            offsetIdx   = 1 if len(Idx) == 1 else 0
            aOut[sIdx:eIdx] = var[Idx][ ( [slice(None)] + Slice[1:] )[offsetIdx:] ]
#            aOut[sIdx:eIdx] = var[ [Idx] + Slice[1:] ]
            # --------------------------------------------------------------

            IDX     = ma.masked_less(IDX-len(var),0).compressed()
            sIdx    = eIdx

        return aOut


class __gtIter__(TSData):
    def __init__(self,gtVar,iterT):
        DATE    = gtVar.header['DATE']

        UTIM    = gtVar.header['UTIM'].strip()
        TDUR    = int(gtVar.header['TDUR'].strip())

        delT   = det_delT( '%i%s'%(TDUR,UTIM[0].lower()))


        sup     = super(__gtIter__,self)
        sup.__init__(gtVar,DATE,delT,iterT)


class __gtVarRead__(__gtVar__):
    def __init__(self,File,SEEK,SIZE,Header):

        self.header = Header
        self._seek  = array(SEEK)
        self._size  = array(SIZE)
        self._F     = File

        nAx0        = len(Header.__Header__['DATE'])
        nAx1        = int(Header.__Header__['AEND3'])-int(Header.__Header__['ASTR3'])+1
        nAx2        = int(Header.__Header__['AEND2'])-int(Header.__Header__['ASTR2'])+1
        nAx3        = int(Header.__Header__['AEND1'])-int(Header.__Header__['ASTR1'])+1

        self.shape  = [nAx0,nAx1,nAx2,nAx3]

        self.day    = __gtIter__(self,'1d')
        self.mon    = __gtIter__(self,'1m')
        self.year   = __gtIter__(self,'1y')



    def __iter__(self):
        self.pnt    = 0

        return self


    def next(self):
        if self.pnt < len(self._seek)/2:
            self.pnt+=1

            return self.__getitem__(self.pnt-1)

        else:
            raise StopIteration


    '''
    def next(self):
        if self.pnt < len(self._seek):
            skszHdr = self._seek[self.pnt], self._size[self.pnt]
            skszData= self._seek[self.pnt+1], self._size[self.pnt+1]

            self.pnt+=2

            self._F.seek(skszData[0])

            # !!! ITERATION ONLY SUPPORTS dtype 'float32' !!!
            dtype   = DType('float32').newbyteorder('>')
            return frombuffer(self._F.read(skszData[1]),dtype)


        else:
            raise StopIteration
    '''


    def __getitem__(self,k):                            ### k = slice
        reduceRank = False

        if type(k) == int:
            k   = slice(k,k+1) if k >=0 else slice(k,None,None)
            reduceRank  = True

        # only t-aixs indexing??? -------------------------------
        seek    = self._seek[self.header.__Header__['dIdx']][k]
        size    = self._size[self.header.__Header__['dIdx']][k]        # should be all same values for a variable
        # -------------------------------------------------------


        ### check DFMT ---------------------
        DFMT    = self.header.__Header__['DFMT'].strip()

        if DFMT == '':  DFMT = 'UR4'            # default treatment
        if DFMT[-1] == '4':
            dtype   = DType('float32').newbyteorder('>')


        if DFMT[-1] == '8':
            dtype   = DType('float64').newbyteorder('>')


        if DFMT[0] == 'M':
            aMsk= empty(
                        (len(size),self.shape[1]*self.shape[2]*self.shape[3]),
                        dtype='bool')

            seek_m  = self._seek[self.header.__Header__['mIdx']][k]
            size_m  = self._size[self.header.__Header__['mIdx']][k]        # should be all same values for a variable

        else:
            seek_m  = [None]*len(seek)
            size_m  = [None]*len(size)

        aOut    = empty(
                        (len(size),self.shape[1]*self.shape[2]*self.shape[3]),
                        dtype=dtype)

        IDX     = None
        mask    = None

        for iAx4,(sk,sz,sk_m,sz_m) in enumerate(map(None,seek,size,seek_m,size_m)):

            ### to reduce overhead for SEEK (need to benchmark)
            if DFMT[0] == 'M':
                self._F.seek(sk_m)

                ### assume indentical structure within same variable
                if mask == None:
                    mask    = invert(unpackbits(frombuffer(self._F.read(sz_m),'uint8')).astype('bool'))

                if IDX  == None:
                    IDX     = ma.array(arange(mask.size),mask=mask).compressed()
                # --------------------------------------------------

                aMsk[iAx4]  = mask
            # ------------------------------------------------

            self._F.seek(sk)

            aOut[iAx4,IDX]  = frombuffer(self._F.read(sz),dtype)

        # ----------------------------------
        #### !!!!! CHECK malfunctioning !!!!! ####
        if len(size) == 1:
            Shape       = (self.shape[1],self.shape[2],self.shape[3])
        else:
            Shape       = (len(size),self.shape[1],self.shape[2],self.shape[3])

#        if reduceRank:  Shape = Shape[1:]

        aOut.shape  = Shape

        return aOut if mask == None else ma.array(aOut,mask=aMsk.reshape(*Shape))


class __gtVarNew__(__gtVar__):
    def __init__(self,varName,args):
#    def __init__(self,varName,(aSrc,DTIME), Header=None):

        if len(args) == 2:
            aSrc,DTIME          = args
            header              = None

        else:
            aSrc,DTIME,header   = args

        ### gen header
        Header          = __gtHdr__(header,shape=aSrc.shape)

        Header.ITEM     = varName

        Header.DATE     = DTIME

        Header.UTIM     = 'HOUR'
        utimSec         = 3600
        dtOrigin        = datetime.datetime(1,1,1)
        dtOffset        = datetime.timedelta(days=366)
        Header.TIME     = [(dtime-dtOrigin+dtOffset).days*86400/utimSec+
                           (dtime-dtOrigin+dtOffset).seconds/utimSec for dtime in DTIME]

        Header.TDUR     = 0 if len(DTIME) == 1 else                         \
                                (DTIME[1]-DTIME[0]).days*86400/utimSec+     \
                                (DTIME[1]-DTIME[0]).seconds/utimSec

        dictDFMT        = {DType('float32'):'UR4',
                           DType('float64'):'UR8'}

        Header.DFMT     = dictDFMT[aSrc.dtype] if aSrc.dtype in dictDFMT else 'UR4'

        Header.CDATE    = datetime.datetime.now().strftime('%Y%m%d %H%M%S ')
        Header.CSIGN    = os.environ['USER']
        Header.MDATE    = datetime.datetime.now().strftime('%Y%m%d %H%M%S ')
        Header.MSIGN    = os.environ['USER']

        Header.SIZE     = aSrc.shape[1]*aSrc.shape[-2]*aSrc.shape[-1]
        # ------------

        self.shape      = aSrc.shape

        self.header     = Header
        self.data       = aSrc

