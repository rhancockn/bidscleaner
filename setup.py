from setuptools import setup, find_packages

setup(
        name='bidscleaner',
        version="0.0.1",
        packages=find_packages(),
        url='https://github.com/rhancockn/bidscleaner.git',
        license='MIT',
        author='Roeland Hancock',
        author_email='rhancock@gmail.com',
        description='A Python module for heuristically cleaning BIDS datasets',
        classifiers=[
            # How mature is this project? Common values are
            #   3 - Alpha
            #   4 - Beta
            #   5 - Production/Stable
            'Development Status :: 3 - Alpha',

            # Indicate who your project is intended for
            'Intended Audience :: Science/Research',
            'Topic :: Scientific/Engineering :: Medical Science Apps.',

            # Pick your license as you wish (should match "license" above)
            'License :: OSI Approved :: MIT License',

            # Specify the Python versions you support here.
            # Indicate whether you support Python 2, Python 3 or both.
            'Programming Language :: Python :: 3.6',

        ],
        test_requires=['pytest'],
        python_requires= '>=3',
        entry_points={
          'console_scripts': [
              'prune_fmap.py = bidscleaner.prune_fmap:main'
          ]
      },
)
