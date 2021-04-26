#!/usr/bin/python3
#------------------------------------------------------------------------------#
# (c) copyright 2003 - Malcolm McLean, MMcSoftware Ltd
#
# This file is subject to the terms and conditions of the GNU General Public
# License.
#
# dump.py - A dump program to list the binary and ascii contents of a file
#------------------------------------------------------------------------------#

import os, sys, getopt, stat

# See /usr/lib/pythonx.y/stat.py
#from stat import ST_SIZE

#------------------------------------------------------------------------------#
# Constants
#------------------------------------------------------------------------------#
space = ' '
lowercase = 'abcdefghijklmnopqrstuvwxyz'
uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'
digits = '0123456789'
letters = lowercase + uppercase
punctuation = '!"#$%&\'()*+,-./:;<=>?@[\]^_`{|}~'
printable = space + digits + letters + punctuation


#------------------------------------------------------------------------------#
# Functions
#------------------------------------------------------------------------------#
def errmsg (msg):
	if msg[-1] != '\n':
		msg += '\n'
	sys.stderr.write ( msg )
	sys.stderr.flush ()

def outmsg (msg):
	if msg[-1] != '\n':
		msg += '\n'
	sys.stdout.write ( msg )
	sys.stdout.flush ()

def usage ():
	errmsg ( 'usage: %s [-s start] [{-e end}|{-l len}] [-w width] [-v] file\n' \
		% sys.argv[0] )
	sys.exit ( 1 )

def paddr ( val ):
	sys.stdout.write ( '%08x' % (val) )

def pword ( val ):
	sys.stdout.write ( '%04x' % (val & 0xffff) )

def pbyte ( val ):
	sys.stdout.write ( '%02x' % (val & 0xff) )

def pascii ( val ):
	sys.stdout.write ( '%s' % (val[0]) )

def pspace ( n = 1 ):
	str = '%' + '%d' % n + 's'
	sys.stdout.write ( str % ' ' )

def pline ():
	sys.stdout.write ( '\n' )
	sys.stdout.flush ()

#------------------------------------------------------------------------------#
# Command line parsing...
#------------------------------------------------------------------------------#

opt_s = None
opt_e = None
opt_l = None
opt_w = None
opt_h = 0
opt_a = 0
opt_v = 0

class BadArgs ( Exception ):
	pass

try:
	opts, args = getopt.getopt ( sys.argv[1:], 's:e:l:w:hav' )

	for opt, val in opts:
		if opt == '-s':
			opt_s = int ( val, 0 )
		if opt == '-e':
			opt_e = int ( val, 0 )
		if opt == '-l':
			opt_l = int ( val, 0 )
		if opt == '-w':
			opt_w = int ( val, 0 )
		if opt == '-h':
			opt_h = 1
		if opt == '-a':
			opt_a = 1
		if opt == '-v':
			opt_v = 1

	if opt_v:
		print ('opts =', opts)
		print ('args =', args)

	if len ( args ) < 1:
		raise BadArgs ('the filename is missing')

	if len ( args ) > 1:
		raise BadArgs ('must have only one filename')

	if opt_h == 0 and opt_a == 0:
		opt_h = 1
		opt_a = 1

except ( getopt.GetoptError, ValueError, BadArgs ) as why:
	errmsg ( str ( why ) )
	usage ()

for arg in args:
	if not os.path.exists ( arg ):
		errmsg ( 'file %r does not exist\n' % arg )
		sys.exit ( 1 )

	filename = arg
	break

try:
	filestat = os.stat ( filename )
	stat.S_ISREG ( filestat[stat.ST_MODE] )
	filesize = filestat[stat.ST_SIZE]
	fp = open ( filename, 'rb' )

except (os.error, IOError) as why:
	errmsg ( str ( why ) )
	sys.exit ( 1 )

#------------------------------------------------------------------------------#
# Width is the number of bytes to display per line
#------------------------------------------------------------------------------#
if opt_w == None:
	width = 16
else:
	width = opt_w

#------------------------------------------------------------------------------#
# Calculate and check the beginning address.
#------------------------------------------------------------------------------#
if opt_s == None:
	beg = 0
else:
	beg = opt_s

if beg >= filesize: beg = filesize - 1
if beg < 0: beg = 0

#------------------------------------------------------------------------------#
# Calculate and check the number of bytes to dump.
#------------------------------------------------------------------------------#
if opt_e == None:
	if opt_l == None:
		nbytes = filesize
	else:
		nbytes = opt_l
else:
	nbytes = opt_e - beg + 1
	if opt_l != None and opt_l > nbytes:
		nbytes = opt_l

if nbytes > filesize - beg: nbytes = filesize - beg
if nbytes < 0: nbytes = 0

#------------------------------------------------------------------------------#
# Print some stats.
#------------------------------------------------------------------------------#
if opt_v:
	outmsg ( 'File name    : %s\n' % (filename) )
	outmsg ( 'File size    : %d (0x%x) bytes\n' % (filesize, filesize) )
	outmsg ( 'Starting at  : %d (0x%x)\n' % (beg, beg) )
	outmsg ( 'Bytes dumped : %d (0x%x)\n' % (nbytes, nbytes) )

#------------------------------------------------------------------------------#
# Main program
#------------------------------------------------------------------------------#
if beg != 0: fp.seek ( beg, 0 )
ptr = beg
line = 1
end = beg + nbytes

while ptr < end:
	count = end - ptr
	if count > width:
		count = width
	buf = fp.read ( count )
	paddr ( ptr )
	pspace ()

	if opt_h:
		for i in range ( 0, width, 1 ):
			if i % 4 == 0:
				pspace ()
			if i < count:
				pbyte ( buf[i] )
			else:
				pspace ( 2 )
			pspace ()
		pspace ()
	if opt_a:
		for i in range ( 0, width, 1 ):
			if i < count:
				c = chr ( buf[i] & 0x7f )
				if c in printable:
					pascii ( c )
				else:
					pascii ( '.' )
			else:
				pspace ()

	ptr += width
	pline ()
	if line % 16 == 0:
		pline ()
	line += 1

#------------------------------------------------------------------------------#
# Cleanup
#------------------------------------------------------------------------------#
fp.close ()

#------------------------------------------------------------------------------#
# End of program
#------------------------------------------------------------------------------#
