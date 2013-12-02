
LBINDEX INSTALLATION

# First install required libs:

python2.7
python-setuptools

# Install LBIndex:

~$ cd $PATH-TO-LBINDEX/LBIndex
IMPORTANT -> Rename the file production.ini-dist to production.ini and make the necessary changes
~$ sudo python setup.py install

# And then start the daemon:

~$ sudo python lbindex start

# To stop the daemon:
~$ sudo python lbindex stop
