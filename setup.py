import setuptools

try:
    import multiprocessing  # noqa
except ImportError:
    pass

setuptools.setup(name='simple-web-server', setup_requires=['pbr'], pbr=True)
