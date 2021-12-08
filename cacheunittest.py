import http.client
import http.cookiejar
import json
import random
import re
import ssl
import time
import unittest
from xml.dom import minidom

import logging

logger = logging.getLogger(__name__)

__unittest = True
PROXYHOST = ""
PROXYPORT = ""
PROXYHTTPSPORT = ""

'''
 Based on https://stackoverflow.com/questions/61280350/how-to-set-the-sni-via-http-client-httpsconnection
'''


class WrapSSSLContext(ssl.SSLContext):
	"""
	HTTPSConnection provides no way to specify the
	server_hostname in the underlying socket. We
	accomplish this by wrapping the context to
	overrride the wrap_socket behavior (called later
	by HTTPSConnection) to specify the
	server_hostname that we want.
	"""

	def __new__(cls, server_hostname, *args, **kwargs):
		return super().__new__(cls, *args, *kwargs)

	def __init__(self, server_hostname, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self._server_hostname = server_hostname

	def wrap_socket(self, sock, *args, **kwargs):
		kwargs['server_hostname'] = self._server_hostname
		return super().wrap_socket(sock, *args, **kwargs)


class CacheUnitTest(unittest.TestCase):
	"""
		Basis class common to all CMS and tests
	"""

	def setUp(self, proxy, port, website, https=False):

		self.headers = None

		self.proxies = None
		if proxy:
			self.proxies = {"http": proxy, "https": proxy}
			self.proxy = proxy

		if port:
			self.port = port
		else:
			if not https:
				self.port = 80
			else:
				self.port = 443

		if website:
			self.website = website
			self.headers = {'Host': self.website}

		self.https = https

		self.response_content = ""
		self.response_content_bytes = 2048

	# Add specific header
	def set_header(self, header_value):
		self.headers.update(header_value)

	def purge_request(self, url):
		return self.request("PURGE", url)

	def get_request(self, url):
		return self.request("GET", url)

	def request(self, method, url):
		# Recoding get request to allow proxy
		if not self.https:
			logging.debug("Establishing HTTP Connection with {} on port {}".format(self.proxy, self.port))
			conn = http.client.HTTPConnection(self.proxy, self.port)
		else:
			proxy_to_server_context = WrapSSSLContext(self.proxy)
			logging.debug("Establishing HTTPS Connection with {} on port {}".format(self.proxy, self.port))
			conn = http.client.HTTPSConnection(self.proxy, self.port, context=proxy_to_server_context)

		logging.debug("Pushing request on url {} with method {}".format(url, method))
		conn.putrequest(method, url, skip_host=True)
		for header in self.headers.keys():
			logging.debug("Specifying header {} with value {}".format(str(header), self.headers.get(header)))
			conn.putheader(str(header), str(self.headers.get(header)))
		conn.endheaders()
		response = conn.getresponse()
		self.response_header = response.headers
		self.response_content = str(response.read(self.response_content_bytes))
		conn.close()
		return response

	def build_url(self, path):
		"""
		Construct an absolute url by appending a path to a domain.
		"""
		return 'http://%s%s' % (self.website, path)

	def get_once(self, url, needpurge=False, **kwargs):
		if needpurge:
			self.purge_request(url)
		response = self.get_request(url)
		return response

	def get_twice(self, url, **kwargs):
		"""
		Fetch a url twice and return the second response (for testing cache hits).
		"""

		self.get_request(url)
		# time.sleep(2)
		response = self.get_request(url)
		return response

	def get_twice_tokenized(self, url, tokenname=None, **kwargs):
		"""
		Fetch a url twice with two different tokens and return the 2nd response
		"""

		if tokenname is not None:
			token = tokenname + "=" + str(random.randint(10000, 999999))
		else:
			token = str(random.randint(10000, 999999))
		# print("url1: " + url + "?" + token)
		self.get_request(url + "?" + token)
		if tokenname is not None:
			token = tokenname + "=" + str(random.randint(10000, 999999))
		else:
			token = str(random.randint(10000, 999999))
		# print("url2: " + url + "?" + token)
		response = self.get_request(url + "?" + token)
		return response

	def purgeandget_twice(self, url, **kwargs):
		"""
		Fetch a url twice and return the second response (for testing cache hits).
		"""
		self.purge_request(url)
		time.sleep(1)
		self.get_request(url)
		time.sleep(2)
		response = self.get_request(url)
		return response

	"""
		Assertions
	"""

	def assertHit(self, response):
		"""
		Assert that a given response contains the header indicating a cache hit.
		"""
		self.assertEqual(str(response.headers['X-Cache']).lower(), 'HIT'.lower(),
						 msg='Uncached while cache was expected')

	def assertMiss(self, response):
		"""
		Assert that a given response contains the header indicating a cache miss.
		"""
		self.assertEqual(str(response.headers['X-Cache']).lower(), 'miss'.lower())

	def assertPass(self, response):
		"""
		Assert that a given response contains the header indicating a pass.
		"""
		self.assertEqual(str(response.headers['X-Cache']).lower(), 'pass'.lower())

	def assertSynth(self, response):
		"""
		Assert that a given response contains the header indicating a pass.
		"""
		self.assertEqual(str(response.headers['X-Cache']).lower(), 'synth'.lower())

	def assertMaxAge(self, response, value):
		"""
		Assert that a given response contains the header indicating specific "max-age" value.
		"""
		max_age_regex = re.compile('max-age\s*=\s*(\d+)')
		try:
			cache_control = response.headers['cache-control']
		except KeyError:
			try:
				cache_control = response.headers['Cache-Control']
			except:
				raise AssertionError('No cache-control header.')

		max_age = max_age_regex.match(cache_control)

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
		self.assertEqual(str(response.headers['X-Back']).lower(), backend.lower())

	def assertRedirectURL(self, response, url):
		self.assertEqual(str(response.headers['location']).lower(), url.lower())

	def assertValidJSON(self, response):
		try:
			logging.debug("Parsing response {} first {} bytes, expecting valid JSON".format(self.response_content,
																							self.response_content_bytes))
			json_object = json.loads(self.response_content)
			return True
		except ValueError as error:
			return False

	def assertValidXML(self, response):
		try:
			logging.debug("Parsing response {} first {} bytes, expecting valid JSON".format(self.response_content,
																							self.response_content_bytes))
			minidom.parseString(self.response_content)
			return True
		except ValueError as error:
			return False

