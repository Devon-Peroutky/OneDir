from binascii import hexlify, unhexlify
from simplecrypt import encrypt, decrypt, DecryptionException


#
# Installing on Ubuntu LTS:
#
# update/upgrade as needed
# sudo apt-get install python-crypto
# sudo pip install simple-crypt
# cd /usr/lib/python2.7/dist-packages/Crypto/Protocol
# IF KDF.PY is not in the folder! 
# sudo wget https://raw.github.com/dlitz/pycrypto/master/lib/Crypto/Protocol/KDF.py
#


def can_you_crack_it():
    pw = '73630001570f1a310cb6889dc26de098389b942b2efd2b8bb4a5b2991fdc8fa7fb406de51e6de2b1e2b4ec67' \
         '01c13dff2bad025fbe3d3a1d5db2b4bd763efafe150ca7808f313dfc8332bccef9edaff76e13e418'
    pw = unhexlify(pw)
    print '\nJust for fun'
    print 'Here is a random encrypted value'
    print pw
    key = raw_input('Try guessing the password... it is not hard: ')
    try:
        print 'You got it!: %s' % decrypt(key, pw)
    except DecryptionException:
        print 'Nope you did not get it'


def main(key, password):
    print 'Uses aes encryption'
    print 'Key: %s Password: %s' % (key, password)
    encrypt_one = encrypt(key, password)  # python string
    encrypt_two = encrypt(key, unicode(password))  # unicode
    encrypt_three = encrypt(key, password.encode('utf8'))  # utf8
    print 'encrypt_one: %s' % hexlify(encrypt_one)
    print 'encrypt_twp: %s' % hexlify(encrypt_two)
    print 'encrypt_three: %s' % hexlify(encrypt_three)
    print '\nEven though the key and password are the same'
    print 'Encoding matters'
    print 'encrypt_one == encrypt_two', encrypt_one == encrypt_two
    print 'encrypt_one == encrypt_three', encrypt_one == encrypt_three
    print 'encrypt_two == encrypt_three', encrypt_two == encrypt_three
    print '\nThe following will be the same for all 3'
    print 'plaintext: %s' % decrypt(key, encrypt_one)


if __name__ == '__main__':
    k = raw_input('Please enter a not so secrete key: ')
    p = raw_input('Please enter a not so secrete password: ')
    main(k, p)
    can_you_crack_it()
