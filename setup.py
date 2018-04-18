from distutils.core import setup

setup(
    name='cacheunittest',
    version='0.1.13',
    author='Patrice Eber',
    author_email='patrice.eber@arte.tv',
    url='https://pypi.org/pypi/CacheUnitTest/',
    license='LICENSE.txt',
    description='Varnish unit test',
    long_description=open('README.txt').read(),
    py_modules=['cacheunittest'],
    install_requires=[
    	"request >= 0.0.26"]
)
