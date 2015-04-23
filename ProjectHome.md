tinycdb-python is a python bind for TinyCDB.
before use this extension, you must install tinycdb first.


tinycdb site: http://www.corpit.ru/mjt/tinycdb.html

TinyCDB is a very fast and simple package for creating and reading constant data bases.

CDB is a constant database, that is, it cannot be updated at a runtime, only rebuilt. Rebuilding is atomic operation and is very fast - much faster than of many other similar packages. Once created, CDB may be queried, and a query takes very little time to complete.

tinycdb-python是一个TinyCDB的python绑定。通过它，python可以直接使用tinycdb。

tinycdb是一个高性能的嵌入式数据库。它使用简单，查询性能很好。但它也有限制，数据不能在数据库运行过程中修改，只能重建。由于它的这个特性，带来了它极快的查询速度，以及非常高的可靠性。
他的key是支持重复的，可以有一个key对应多个value。

据我这里的简单测试。在100万数据中，每秒可以查询20万次。

```
# coding: utf-8
import os, sys
import tinycdb

def test():
    m = tinycdb.Maker('test.db')

    for i in xrange(1, 100000):
        m.add('zhaoweikid' + str(i%5000), 'testinfoiiiiiiiiiiiiiiiii'+str(i))
    m.finish()

    import time

    f = tinycdb.Finder('test.db')
    print 'seek:', f.seek('zhaoweikid0')
    start = time.time()
    for i in xrange(1, 100000):
        a = f.find('zhaoweikid1')
    end = time.time()
    print 'find time:', end-start, a

    #print 'find:', f.find('zhaoweikid2')

    start = time.time()
    for i in xrange(1, 100000):
        a = f.findall('zhaoweikid2')
    end = time.time()
    print 'findall time:', end-start, a


    f.close()


test()

```