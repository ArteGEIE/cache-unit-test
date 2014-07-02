import random
import unittest
import sys, getopt
import http.cookiejar
import json
import re
import time

import requests
import http.client



class CacheTest(unittest.TestCase):
    """
        Basis class common to all CMS and tests
    """

    def setUp(self, proxy, port, website):

        self.website = ""
        self.headers = None

        if website != "":
            self.website = website
            self.headers = {'Host' : self.website}


        self.proxies = None
        if proxy != "":
            # print("proxying website ", website, " with proxy ", proxy)
            self.proxies = { "http": proxy, "https": proxy}
            self.proxy = proxy

        self.port = port


    def get_request(self, url):
        # Recoding get request to allow proxy
        conn = http.client.HTTPConnection(self.proxy, self.port)
        conn.putrequest("GET", url,  skip_host=True)
        conn.putheader("Host", self.website)
        conn.endheaders()
        response = conn.getresponse()
        conn.close()
        return response

    def build_url(self, path):
        """
        Construct an absolute url by appending a path to a domain.
        """
        return 'http://%s%s' % (self.website, path)

    def get_once(self, url, **kwargs):
        # self.build_url(url)
        # print("once url ", url, " headers ", self.headers)
        response = self.get_request(url)
        return response

    def get_twice(self, url, **kwargs):
        """
        Fetch a url twice and return the second response (for testing cache hits).
        """
        # self.build_url(url)
        #self.headers.update({'Connection' : 'close'})

        self.get_request(url)
        time.sleep(2)
        # print("Url : ", url, "Request : ", self.headers)
        response = self.get_request(url)
        return response

    """
        Assertions
    """

    def assertHit(self, response):
        """
        Assert that a given response contains the header indicating a cache hit.
        """
        self.assertEqual(response.headers['X-Cache'].lower(), 'HIT'.lower())

    def assertMiss(self, response):
        """
        Assert that a given response contains the header indicating a cache miss.
        """
        self.assertEqual(response.headers['X-Cache'].lower(), 'miss'.lower())

    def assertMaxAge(self, response, value):
        """
        Assert that a given response contains the header indicating specific "max-age" value.
        """
        MAX_AGE_REGEX = re.compile('max-age\s*=\s*(\d+)')
        try:
            cache_control = response.headers['cache-control']
        except KeyError:
            try:
                cache_control = response.headers['Cache-Control']
            except:
                raise AssertionError('No cache-control header.')

        max_age = MAX_AGE_REGEX.match(cache_control)

        if not max_age:
            raise AssertionError('No max-age specified in cache-control header.')

        self.assertEqual(int(max_age.group(1)), value)

    def assert200(self, response):
        # Ok
        self.assertEqual(response.status, 200)

    def assert30X(self, response):
        self.assertRegex(str(response.status), '30?')

    def assert301(self, response):
        # Permanent redirect
        self.assertEqual(response.status, 301)
 
    def assert302(self, response):
        # Temporary redirect
        self.assertEqual(response.status, 302)
 
    def assert304(self, response):
        # Not modified
        self.assertEqual(response.status, 304)

    def assert40X(self, response):
        self.assertRegex(str(response.status), '40?')

    def assert400(self, response):
        # Bad Request
        self.assertEqual(response.status, 400)

    def assert401(self, response):
        # Unauthorized
        self.assertEqual(response.status, 401)

    def assert403(self, response):
        # Forbidden
        self.assertEqual(response.status, 403)

    def assert404(self, response):
        # Not found
        self.assertEqual(response.status, 404)

    def assert405(self, response):
        # Method Not allowed
        self.assertEqual(response.status, 405)

    def assert50X(self, response):
        # Method Not allowed
        self.assertRegex(str(response.status), '50?')

    def assertBackend(self, response, backend):
        self.assertEqual(response.headers['X-Back'].lower(), backend.lower())


