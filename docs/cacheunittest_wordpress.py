from cacheunittest import CacheUnitTest

# You probably have to check https://www.varnish-software.com/wiki/content/tutorials/wordpress/wp_vcl.html

class test_wordpress(CacheUnitTest):
	def setUp(self):
		CacheTest.setUp(self, PROXYHOST, PROXYPORT, "mywebsite.com")

	def test_slash(self):
		url = '/'
		response = self.get_once(url)
		# Should be a redirect (lang test ?)
		self.assert301(response)

	def test_home_fr(self):
		url = '/fr/'

		response = self.get_twice(url)
		# Content should be cached
		self.assertHit(response)
		# Cache delay should be 60s
		self.assertMaxAge(response, 60)
		# Backend server should be HPV2
		self.assertBackend(response, "WORDPRESS")

	def test_login(self):
		url = '/wp-login.php'
		response = self.get_once(url)
		self.assert200(response)
		self.assertBackend(response, "WORDPRESS")






