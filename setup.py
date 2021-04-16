import setuptools

try:
    import multiprocessing  # noqa
except ImportError:
    pass

setuptools.setup(
    name='simple-web-server',
    version='1.0.0',
    setup_requires=['pbr'],
    pbr=True)
