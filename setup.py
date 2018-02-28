from distutils.core import setup

setup(
    name='CacheUnitTest',
    version='0.1.0',
    author='Patrice Eber',
    author_email='patrice.eber@arte.tv',
    packages=['CacheUnitTest'],
    url='http://pypi.python.org/pypi/CacheUnitTest/',
    license='LICENSE.txt',
    description='Varnish unit test',
    long_description=open('README.txt').read(),
    install_requires=[
	"random",
	"unittest",
	"sys",
	"getopt",
	"http.cookiejar",
	"json",
	"re",
	"time",
	"requests",
	"http.client"
    ],
)
