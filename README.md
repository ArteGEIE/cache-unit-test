cache-unit-test
===============

Unit test Python library for testing cache systems like varnish

Based on the work of @onyxfish (https://gist.github.com/onyxfish)



- [x] cachetest.py : productive
- [ ] wordpresscachetest.py : not usable yet

````bash
user@localhost> python3.3 exampletest 
````

# Python test launcher
With the unittest python system, you may have a unittest launcher, and many tests on different folders


````
#!/usr/bin/env python

import sys, getopt
import json
import re
import random
import unittest
import argparse
import cacheunittest
from cacheunittest import CacheUnitTest
import unittest
import os
import sys


if __name__ == "__main__":

	os.environ['MOZ_HEADLESS'] = '1'

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



	print("")
	print("")
	print("Discovering ", codePath, " for artetest*.py tests")
	print("")
	tests = unittest.TestSuite()
	loader = unittest.TestLoader()
	tests_auto = loader.discover(codePath, pattern="artetest*.py", top_level_dir=None)
	result = unittest.TextTestRunner(verbosity=verbosity).run(tests_auto)
	print(result)
	if result.wasSuccessful():
		print("")
		print("")
		print("")
		print("")
		print("    All tests were successfully passed")
		print("        GGGGGOOOOOOOODDDDDD JOB !!!!")
		print("")
		print("")
		print("")
		print("")
		sys.exit(0)
	else:
		print("")
		print("    OOps something wrong happened")
		print("")
		print("###########################")
		print("###########################")
		print("###########################")
		print("#     KEEP THE FAITH!     #")
		print("###########################")
		print("###########################")
		print("###########################")
		sys.exit(2)

````

# cache unit test


# Varnish configuration

The tests are only valid if the varnish configuration contains the following setup
Based on:
* https://www.varnish-software.com/wiki/content/tutorials/varnish/sample_vclTemplate.html
* https://docs.varnish-software.com/tutorials/hit-miss-logging/
* https://www.varnish-software.com/wiki/content/tutorials/varnish/multiple_varnishes.html
* https://varnish-cache.org/docs/trunk/users-guide/purging.html

**It's probably a good idea to put some security around it via a test on client.ip for example**

## Example VCL ([docs/example.vcl](docs/example.vcl)):
````
acl dev {
    # ACL we'll use later to allow purges
    "localhost";
    "127.0.0.1";
    "::1";
}

sub vcl_recv  {

	# To avoid any hack based on these headers
	unset req.http.x-cache;
    unset req.http.X-Back;

    if (req.url ~ "^/static/") {
        set req.http.X-Back = "STATIC";
    } else {
        set req.http.X-Back = "WORDPRESS";
    }

    if (req.method == "PURGE") {
        if (!client.ip ~ dev) {
            return(synth(405,"Not allowed."));
        }
        return (purge);
    }
}

sub vcl_hit {
	set req.http.x-cache = "HIT";
	if (obj.ttl <= 0 and obj.grace > 0s) {
		set req.http.x-cache = "HIT_GRACED";
	}
}

sub vcl_miss {
	set req.http.x-cache = "MISS";
}

sub vcl_pass {
	set req.http.x-cache = "PASS";
}

sub vcl_pipe {
	set req.http.x-cache = "PIPE";
}

sub vcl_synth {
    if (!client.ip ~ dev) {
        set resp.http.X-Back = "VARNISH";
        set resp.http.x-cache = "SYNTH";
    }
}

sub vcl_deliver {
    if (!client.ip ~ dev) {
        if (obj.hits > 0) {
            set resp.http.X-NumberOfHits = obj.hits;
        }
        set resp.http.X-Varnish-Server = server.identity;
        set resp.http.X-Back = req.http.X-Back;
        set resp.http.X-Cache = req.http.X-Cache;
    }
}
````