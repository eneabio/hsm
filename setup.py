from distutils.core import setup

setup(
    name='Hsm',
    version='0.1.9',
    author='Fabio N. Filasieno',
    author_email='fabio@filasieno.com',
    packages=['hsm', 'hsm.test'],
    scripts=[],
    url='http://pyhsm.org',
    license='LICENSE.txt',
    description='Hsm is a hierarchical state machines library designed for very large hand written state machines.',
    long_description=open('README.txt').read(),
    provides=["hsm"]
)
