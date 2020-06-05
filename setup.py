from distutils.core import setup



with open("README.md", "r") as fh:
	long_description = fh.read()
	
setup(
	name='cacheunittest',
	version='1.2.0',
	author='Alapaje',
	author_email='patrice.eber@arte.tv',
	url='https://pypi.org/pypi/CacheUnitTest/',
	license='LICENSE.txt',
	description='Varnish unit test',
	long_description=long_description,
	long_description_content_type="text/markdown",
	py_modules=['cacheunittest'],
	install_requires=[
		"request >= 0.0.26"],
	python_requires='>=3.6',
)
