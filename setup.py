from setuptools import setup, find_packages

setup(
    name='spclipper',
    version='0.1',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Flask',
        'pysrt',
        'numpy',
        'sqlalchemy',
        'soundfile',
        'simplejson',
        'pydub'
    ],
    entry_points={
        'console_scripts': [
            'spclipper=spclipper:main' 
        ]
    },
    author='Andre LaBranche',
    author_email='dre@mac.com', 
    description='Search SRT transcripts and get audio results',
    keywords='audio processing, flask, web app'
)
