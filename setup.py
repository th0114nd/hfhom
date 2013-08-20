from setuptools import setup

setup(
        name='hfhom',
        version='1.0',
        packages=['corrterm',],
        license='GNU General Public License',
        # -f http://math.uic.edu/t3m/plink plink
        install_requires=["PIL", "networkx", "numpy >= 1.5", "plink", "matplotlib"],
        include_package_data = True,
        package_data={'corrterm': ['sys', 'nx', 'images/*.png', 'images/*.txt',
            'test/testing/*.txt']},
        long_description=open('README').read(),
        scripts=['bin/hfhom']
)
