import os
import hashlib


__author__ = 'Justin Jansen'
__status__ = 'Prototype'
__date__ = '03/10/14'


"""
This might not even be needed but, it could be used in the even that a client and server loose sync
"""


files = ['a.txt', 'b.txt', 'c.txt']
same = 'a.txt and b.txt are the same'
dif =  'c.txt is different'


def setup_module():
    """
    Creates 3 testing files.
    a.txt and b.txt are the same 
    c.txt is different
    """
    for f in files:
        with open(f, 'wb') as w:
            if not f == 'c.txt':
                w.write(same)
            else:
                w.write(dif)


def test_md5_same():
    """
    Checks that a.txt and b.txt produce the same md5 check sums
    """
    a = [hashlib.md5(open(files[0], 'rb').read()).digest()]  
    b = [hashlib.md5(open(files[1], 'rb').read()).digest()]  
    assert a == b


def test_md5_different():
    """
    Checks that a.txt and c.txt produce different md5 check sums
    """
    a = [hashlib.md5(open(files[0], 'rb').read()).digest()]  
    c = [hashlib.md5(open(files[2], 'rb').read()).digest()]  
    assert not a == c


def test_sha224_same():
    """
    Checks that a.txt and b.txt produce the same sha224 check sums
    """  
    a = [hashlib.sha224(open(files[0], 'rb').read()).digest()]  
    b = [hashlib.sha224(open(files[1], 'rb').read()).digest()]  
    assert a == b


def test_sha224_different():
    """
    Checks that a.txt and c.txt produce different sha224 check sums
    """
    a = [hashlib.sha224(open(files[0], 'rb').read()).digest()]  
    c = [hashlib.sha224(open(files[2], 'rb').read()).digest()]  
    assert not a == c


def test_sha512_same():
    """
    Checks that a.txt and b.txt produce the same sha512 check sums
    """
    a = [hashlib.sha512(open(files[0], 'rb').read()).digest()]  
    b = [hashlib.sha512(open(files[1], 'rb').read()).digest()]  
    assert a == b


def test_sha512_different():
    """
    Checks that a.txt and c.txt produce different sha512 check sums
    """
    a = [hashlib.sha512(open(files[0], 'rb').read()).digest()]  
    c = [hashlib.sha512(open(files[2], 'rb').read()).digest()]  
    assert not a == c


def teardown_module():
    """
    Deletes the testing files
    """
    for f in files:
        os.remove(f)   

    
if __name__ == '__main__':
    """
    A demo of what is going on above so you can see what is happening
    """
    setup_module()
    print same, dif
    print 'md5 checksums:'
    for f in files:
        print '\t%s:' % f, [hashlib.md5(open(f, 'rb').read()).digest()]
    print 'sha225 checksums:'
    for f in files:
        print '\t%s:' % f, [hashlib.sha224(open(f,'rb').read()).digest()]
    print 'sha512 checksums'
    for f in files:
        print '\t%s:' % f, [hashlib.sha512(open(f,'rb').read()).digest()]
    teardown_module()
