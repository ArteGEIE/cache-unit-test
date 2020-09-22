from distutils.core import setup
import setuptools


with open("README.md", "r") as fh:
	long_description = fh.read()
	
setup(
	name='cacheunittest',
	version='1.2.5',
	author='Alapaje',
	author_email='paje@github.com',
	license='LICENSE.txt',
	description='Varnish unit test',
	long_description=long_description,
	long_description_content_type="text/markdown",
	url="https://github.com/ArteGEIE/cache-unit-test",
    packages=setuptools.find_packages(),
	py_modules=['cacheunittest'],
	install_requires=[
		"requests"],
	python_requires='>=3.7',
)
