from setuptools import setup, find_packages

setup(
    name='xelo2',
    version='0.1',
    description='Database GUI',
    url='https://github.com/gpiantoni/xelo2',
    author="Gio Piantoni",
    author_email='xelo2@gpiantoni.com',
    license='GPLv3',
    classifiers=[
        'Environment :: X11 Applications :: Qt',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.7',
    ],
    keywords='database qt',
    packages=find_packages(),
    install_requires=[
        'numpy',
        'PyQt5',
        'pandas',
        'nibabel',
        'wonambi',
        'bidso',
        ],
    entry_points={
        'console_scripts': [
            'xelo2=xelo2.gui.main:main',
        ],
    },
)
