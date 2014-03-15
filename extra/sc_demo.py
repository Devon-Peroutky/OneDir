from binascii import hexlify, unhexlify
from simplecrypt import encrypt, decrypt, DecryptionException


def can_you_crack_it():
    pw = '736300016c85cbf950ae8a1795a3f10a1bb675e64fa6645d6e4756e9048f1409e9c267b6a5d87c2627f30715' \
         'cb1e18f7246377ce0dc63160053c0209cde896d0ff74eb199464aaf3b6a33458b3c75b92afe82bb951976aeb' \
         '331fd76295ab1a60075f7a3793db6d41e3703c081567a783ed323f8c'
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
