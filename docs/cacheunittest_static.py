from cacheunittest import CacheUnitTest



class test_static(CacheUnitTest):
	def setUp(self):
		CacheUnitTest.setUp(self, cacheunittest.proxyhost, cacheunittest.proxyhttpport, "mywebsite.com")

	def test_logo(self):
		url = '/static/logo.png'

		response = self.get_twice(url)
		self.assertHit(response)
		self.assert200(response)
		self.assertBackend(response, "STATIC")
