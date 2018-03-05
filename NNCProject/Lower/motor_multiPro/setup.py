from distutils.core import setup
from Cython.Build import cythonize

setup(
    name='motor',
    ext_modules=cythonize('__init__.pyx')
)


