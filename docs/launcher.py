#!/usr/bin/env python


import argparse
import cacheunittest
import unittest
import sys


if __name__ == "__main__":

	argparse=argparse.ArgumentParser(description="Proxy directives tests app", add_help=True)
	argparse.add_argument("--host", default="127.0.0.1", help="define a target varnish host")
	argparse.add_argument("--httpport", type=int, default=80, help="override the default http port 80")
	argparse.add_argument("--httpsport", type=int, default=443, help="override the default https port 443")
	argparse.add_argument("--verbosity", type=int, default=2, help="verbosity level")
	argparse.add_argument("-p", "--path", default=".", help="code path")
	args = argparse.parse_args()

	verbosity = args.verbosity
	codePath = args.path

	cacheunittest.proxyhost = args.host
	cacheunittest.proxyhttpport  = args.httpport
	cacheunittest.proxyhttpsport = args.httpsport

	tests = unittest.TestSuite()
	loader = unittest.TestLoader()
	tests_auto = loader.discover(codePath, pattern="cacheunittest_*.py", top_level_dir=None)
	result = unittest.TextTestRunner(verbosity=verbosity).run(tests_auto)
	print(result)
	if result.wasSuccessful():
		print("everything seems fine")
		sys.exit(0)
	else:
		print("Do not panic ! test error")
		sys.exit(2)
