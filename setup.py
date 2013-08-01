from distutils.core import setup

setup(
    name='Hsm',
    version='0.1.0',
    author='Fabio N. Filasieno',
    author_email='fabio@filasieno.com',
    packages=['hsm', 'hsm.test'],
    scripts=[],
    url='http://www.pyhsm.org',
    license='LICENSE.txt',
    description='PyHsm is a hierarchical state machines library designed for very large hand written state machines.',
    long_description=open('README.txt').read(),
)