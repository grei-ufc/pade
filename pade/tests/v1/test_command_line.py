#! /usr/bin/env python

import optparse

def main():
	p = optparse.OptionParser()	
	p.add_option('--person', '-p', default='person')
	options, arguments = p.parse_args()
	print 'Hello World, %s' % 	options.person

if __name__ == '__main__':
	main()

