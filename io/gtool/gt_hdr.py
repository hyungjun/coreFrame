#import os,sys,datetime
#from numpy          import frombuffer,array,empty,unpackbits,invert,ma,ndarray
#from numpy          import dtype as DType
#from cf.util        import OrderedDict,key2slice
#from cf.io          import fIO
#from cf.TimeSeries  import TSData,det_delT

#import struct,time

from cf.util        import OrderedDict


class __gtHdrFmt__(object):
    fmt = OrderedDict([
    ("IDFM",[int,"%16i",9010]),     ("DSET",[str,"%-16s",'']),      ("ITEM",[str,"%-16s",'']),      #00
    ("EDIT1",[str,"%-16s",'']),     ("EDIT2",[str,"%-16s",'']),     ("EDIT3",[str,"%-16s",'']),     #03
    ("EDIT4",[str,"%-16s",'']),     ("EDIT5",[str,"%-16s",'']),     ("EDIT6",[str,"%-16s",'']),     #06
    ("EDIT7",[str,"%-16s",'']),     ("EDIT8",[str,"%-16s",'']),     ("FNUM",[int,"%16i",1]),        #09
    ("DNUM",[int,"%16i",1]),        ("TITL1",[str,"%-16s",'']),     ("TITL2",[str,"%-16s",'']),     #12
    ("UNIT",[str,"%-16s",'']),      ("ETTL1",[str,"%-16s",'']),     ("ETTL2",[str,"%-16s",'']),     #15
    ("ETTL3",[str,"%-16s",'']),     ("ETTL4",[str,"%-16s",'']),     ("ETTL5",[str,"%-16s",'']),     #18
    ("ETTL6",[str,"%-16s",'']),     ("ETTL7",[str,"%-16s",'']),     ("ETTL8",[str,"%-16s",'']),     #21
    ("TIME",[int,"%16i",[]]),       ("UTIM",[str,"%-16s",'HOUR']),  ("DATE",[str,"%-16s",[]]),      #24
    ("TDUR",[int,"%16i",0]),        ("AITM1",[str,"%-16s",'']),     ("ASTR1",[int,"%16i",1]),       #27
    ("AEND1",[int,"%16i",0]),       ("AITM2",[str,"%-16s",'']),     ("ASTR2",[int,"%16i",1]),       #30
    ("AEND2",[int,"%16i",0]),       ("AITM3",[str,"%-16s",'']),     ("ASTR3",[int,"%16i",1]),       #33
    ("AEND3",[int,"%16i",0]),       ("DFMT",[str,"%-16s",'UR4']),   ("MISS",[float,"%16.7e",-999.]),#36
    ("DMIN",[float,"%16.7e",-999.]),("DMAX",[float,"%16.7e",-999.]),("DIVL",[float,"%16.7e",-999.]),#39
    ("DIVL",[float,"%16.7e",-999.]),("STYP",[int,"%16i",1]),        ("COPTN",[str,"%-16s",'']),     #42
    ("IOPTN",[int,"%16i",0]),       ("ROPTN",[float,"%16.7e",0.]),  ("DATE1",[str,"%-16s",'']),     #45
    ("DATE2",[str,"%-16s",'']),     ("MEMO1",[str,"%-16s",'']),     ("MEMO2",[str,"%-16s",'']),     #48
    ("MEMO3",[str,"%-16s",'']),     ("MEMO4",[str,"%-16s",'']),     ("MEMO5",[str,"%-16s",'']),     #51
    ("MEMO6",[str,"%-16s",'']),     ("MEMO7",[str,"%-16s",'']),     ("MEMO8",[str,"%-16s",'']),     #54
    ("MEMO9",[str,"%-16s",'']),     ("MEMO10",[str,"%-16s",'']),    ("CDATE",[str,"%-16s",'']),     #57
    ("CSIGN",[str,"%-16s",'']),     ("MDATE",[str,"%-16s",'']),     ("MSIGN",[str,"%-16s",'']),     #60
    ("SIZE",[int,"%16i",0])                                                                         #63
    ])

class __gtHdr__(object):
    def __init__(self,lHeader=None,shape=None):

        if lHeader == None:
            Header  = OrderedDict([(k,v[2]) for k,v in __gtHdrFmt__.fmt.items()])

        else:
            Header  = OrderedDict([(k,v) for k,v in map(None,__gtHdrFmt__.fmt.keys(),lHeader)])

        if shape != None and lHeader == None:

            Header['AITM1'] = __gtHdrFmt__.fmt['AITM1'][1]%('CONST%i'%shape[3])
            Header['AITM2'] = __gtHdrFmt__.fmt['AITM2'][1]%('CONST%i'%shape[2])
            Header['AITM3'] = __gtHdrFmt__.fmt['AITM3'][1]%('CONST%i'%shape[1])

            Header['AEND1'] = __gtHdrFmt__.fmt['AEND1'][1]%shape[3]
            Header['AEND2'] = __gtHdrFmt__.fmt['AEND2'][1]%shape[2]
            Header['AEND3'] = __gtHdrFmt__.fmt['AEND3'][1]%shape[1]

        self.__Header__   = Header


    def __repr__(self):

        OUT         = []

        lOut, lNote = [],[]
        for i,(k,v) in enumerate(self.__Header__.items()):

            if k in ['dIdx','mIdx']: continue        ## skip dIdx, mIdx

            fmt     = __gtHdrFmt__.fmt[k]

            if type(v) not in [list,tuple]:
                if str(v).strip() == '':
                    lOut.append((k,' '*16))

                else:
                    lOut.append((k,fmt[1]%fmt[0](v)))

            else:
                lOut.append((k,'[  ** NOTE **  ]'))
                lNote.append((k,v))

            if len(lOut)%3 == 0:
                OUT.append('[%02d]  '%(i-2) + ''.join(['%-6s :%s:  '%(_k,_v) for _k,_v in lOut]))
                lOut = []

        OUT.append('[%02d]  '%(i-2) + ''.join(['%-6s :%s:  '%(_k,_v) for _k,_v in lOut]) + '\n')

        if lNote != []:
            OUT.append('   ** NOTE **   ')
            OUT.append('\n'.join(
                                ['[%02d]  %-6s :%s, (%i)'%(self.__Header__.keys().index(k),k,
                                                   '[%s ... %s]'%(v[0],v[-1]) if v != [] else '[]',
                                                   len(v)
                                                    )
                                                for k,v in lNote])+'\n'
            )

        return '\n'+'\n'.join(OUT)

    def __radd__(self,other):
        raise TypeError, 'numpy operator is not supported.'


    def __add__(self,other):
        # check the consistency for each spatial structure --------------------
        selfShp     = [ int(self['AEND3']),  int(self['AEND2']),  int(self['AEND1']) ]
        otherShp    = [ int(other['AEND3']), int(other['AEND2']), int(other['AEND1']) ]

        if selfShp != otherShp:     raise Warning, 'SHAPE: %s != %s'%(selfShp, otherShp)
        # ---------------------------------------------------------------------

        # check both have same ITEM -------------------------------------------
        selfItem    = self['ITEM']
        otherItem   = other['ITEM']

        if selfItem != otherItem:   raise Warning, 'ITEM : %s != %s'%(selfItem, otherItem)
        # ---------------------------------------------------------------------

        # need to check DTIME structure (delT, redundancy, deviation from oriDTime...)
        DTIME   = self['DATE'] + other['DATE']
        TIME    = self['TIME'] + other['TIME']

        Shape   = tuple( [len(DTIME)] + selfShp )

        header          = __gtHdr__( self.template,   # get a header as a template
                                     shape=Shape)
        self['DATE']  = DTIME
        self['TIME']  = TIME

        return self


    def __setitem__(self,k,v):
        # 'DATE' added; need to sync TIME, DATE automatically
        #if k not in ['TIME','DATE','dIdx','mIdx']:
        if k not in ['TIME','DATE','dIdx','mIdx']:
            self.__Header__[k]  = __gtHdrFmt__.fmt[k][0](v)

        else:
            self.__Header__[k]  = v


    def __getitem__(self,k):
        return self.__Header__[k]


    def __getattr__(self,k):
        if k == 'template'  :

            Template    = []
            for _k,_v in self.__Header__.items():
                if _k in ['dIdx','mIdx']:   continue    # skip records for file structure

                if type(_v) not in [list,tuple]:
                    _v  = __gtHdrFmt__.fmt[_k][0](_v)   # convert back to defalut type
                    Template.append(__gtHdrFmt__.fmt[_k][1]%_v)

                else:
                    Template.append(_v)

            return Template


        if k != '__Header__':   return self.__Header__[k]
        else                :   return self.__dict__[k]


    def __setattr__(self,k,v):
        if k == '__Header__':
            self.__dict__['__Header__'] = v

        elif type(v) not in [list]:
            self.__Header__[k]  = __gtHdrFmt__.fmt[k][1]%v
#            self.__Header__[k]  = __gtHdrFmt__.fmt[k][0](v)

        else:
            self.__Header__[k]  = v


