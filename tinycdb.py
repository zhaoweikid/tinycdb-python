# coding: utf-8
'''
python bind for tinycdb
author: zhaoweikid
date: 2009-12-14
site: http://code.google.com/p/tinycdb-python
'''
import os, sys
import ctypes
from ctypes import *
from ctypes.util import find_library

if sys.platform == 'win32':
    cdblib = cdll.LoadLibrary("libcdb.dll")
else:
    cdblib = cdll.LoadLibrary("libcdb.so")


CDB_PUT_ADD = 0
CDB_FIND = CDB_PUT_ADD
CDB_PUT_REPLACE = 1
CDB_FIND_REMOVE = CDB_PUT_REPLACE
CDB_PUT_INSERT = 2
CDB_PUT_WARN = 3
CDB_PUT_REPLACE0 = 4
CDB_FIND_FILL0 = CDB_PUT_REPLACE0

class cdb (Structure):
    _fields_ = [('cdb_fd', c_int),
                ('cdb_fsize', c_uint),
                ('cdb_dend', c_uint),
                ('cdb_men', c_char_p),
                ('cdb_vpos', c_uint),
                ('cdb_vlen', c_uint),
                ('cdb_kpos', c_uint),
                ('cdb_klen', c_uint)]

class cdb_rec (Structure):
    _fields_ = [('hval', c_uint),
                ('rpos', c_uint)]


class cdb_rl (Structure):
    pass
cdb_rl._fields_ = [('next', POINTER(cdb_rl)),
                ('cnt', c_uint),
                ('rec', cdb_rec * 254)]


class cdb_find (Structure):
    _fields_ = [('cdb_cdbp', POINTER(cdb)),
                ('cdb_hval', c_uint),
                ('cdb_htp', c_char_p),
                ('cdb_htab', c_char_p),
                ('cdb_htend', c_char_p),
                ('cdb_httodo', c_uint),
                ('cdb_key', c_void_p),
                ('cdb_klen', c_uint)]

class cdb_make (Structure):
    _fields_ = [('cdb_fd', c_int),
                ('cdb_dpos', c_uint),
                ('cdb_cdb_rcnt', c_uint),
                ('cdb_cdb_buf', c_ubyte * 4096),
                ('cdb_bpos', POINTER(c_ubyte)),
                ('cdb_rec', POINTER(cdb_rl) * 256)]


cdblib.cdb_make_start.argtypes = [POINTER(cdb_make), c_int]
cdblib.cdb_make_add.argtypes = [POINTER(cdb_make), c_void_p, c_uint, c_void_p, c_uint]
cdblib.cdb_make_put.argtypes = [POINTER(cdb_make), c_void_p, c_uint, c_void_p, c_uint, c_uint]
cdblib.cdb_make_exists.argtypes = [POINTER(cdb_make), c_void_p, c_uint]
cdblib.cdb_make_finish.argtypes = [POINTER(cdb_make)]

cdblib.cdb_findinit.argtypes = [POINTER(cdb_find), POINTER(cdb), c_void_p, c_uint]
cdblib.cdb_findnext.argtypes = [POINTER(cdb_find)]
cdblib.cdb_seqnext.argtypes = [c_uint, POINTER(cdb)]
cdblib.cdb_seek.argtypes  = [c_int, c_void_p, c_uint, POINTER(c_uint)]
cdblib.cdb_bread.argtypes = [c_int, c_void_p, c_int]

cdblib.cdb_init.argtypes = [POINTER(cdb), c_int]
cdblib.cdb_free.argtypes = [POINTER(cdb)]
cdblib.cdb_read.argtypes = [POINTER(cdb), c_void_p, c_uint, c_uint]
cdblib.cdb_get.argtypes  = [POINTER(cdb), c_uint, c_uint]
cdblib.cdb_find.argtypes = [POINTER(cdb), c_void_p, c_uint]

cdblib.cdb_hash.argtypes = [c_void_p, c_uint]
cdblib.cdb_unpack.argtypes = [POINTER(c_ubyte)]
cdblib.cdb_pack.argtypes = [c_uint, POINTER(c_ubyte)]

def cdb_datapos(c):
    return c.cdb_vpos

def cdb_datalen(c):
    return c.cdb_vlen

def cdb_keypos(c):
    return c.cdb_kpos

def cdb_keylen(c):
    return c.cdb_klen

def cdb_fileno(c):
    return c.cdb_fd


class CDB:
    def __init_(self):
        pass


class Maker:
    def __init__(self, filename):
        self.cdbm = cdb_make()
        self.file = open(filename, 'w')
        self.fd = self.file.fileno()
        cdblib.cdb_make_start(self.cdbm, self.fd)

    def add(self, key, val):
        cdblib.cdb_make_add(self.cdbm, key, len(key), val, len(val)) 


    def put(self, key, val, flags):
        cdblib.cdb_make_put(self.cdbm, key, len(key), val, len(val), flags) 


    def finish(self):
        cdblib.cdb_make_finish(self.cdbm)


class Finder:
    def __init__(self, filename):
        self.file = open(filename, 'r')
        self.fd = self.file.fileno()
        self.cdb = cdb()
        
        cdblib.cdb_init(self.cdb, self.fd)


    def find(self, key):
        ret = cdblib.cdb_find(self.cdb, key, len(key))
        if ret > 0:
            vpos = cdb_datapos(self.cdb)
            vlen = cdb_datalen(self.cdb)

            buf = (c_char * vlen)()
            val = cast(buf, c_void_p)

            cdblib.cdb_read(self.cdb, val, vlen, vpos)

            return buf.value
        else:
            return None
 
    def findall(self, key):
        retv = []
        finder = cdb_find()
        cdblib.cdb_findinit(finder, self.cdb, key, len(key))
        while cdblib.cdb_findnext(finder) > 0:
            vpos = cdb_datapos(self.cdb)
            vlen = cdb_datalen(self.cdb)

            buf = (c_char * vlen)()
            val = cast(buf, c_void_p)

            cdblib.cdb_read(self.cdb, val, vlen, vpos)

            retv.append(buf.value)

        return retv


    def seek(self, key):
        vlen = c_uint()
        ret = cdblib.cdb_seek(self.fd, key, len(key), vlen)
        if ret > 0:
            buf = (c_char * vlen.value)()
            val = cast(buf, c_void_p)

            cdblib.cdb_bread(self.fd, val, vlen.value)
            return buf.value
        else:
            return None


    def close(self):
        cdblib.cdb_free(self.cdb)
        self.file.close()



def test_make():
    m = Maker('test.db')

    for i in xrange(1, 100000):
        m.add('zhaoweikid' + str(i%5000), 'testinfoiiiiiiiiiiiiiiiii'+str(i))
    m.finish()
   
def test_find():
    import time, random

    f = Finder('test.db')
    print 'seek:', f.seek('zhaoweikid0')
    start = time.time()
    for i in xrange(1, 100):
        a = f.find('zhaoweikid' + str(random.randint(0,100)))
    end = time.time()
    print 'find time:', end-start, a

    start = time.time()
    for i in xrange(1, 10000):
        a = f.findall('zhaoweikid2')
    end = time.time()
    print 'findall time:', end-start, a


    f.close()



if __name__ == '__main__':
    test_make()
    test_find()


