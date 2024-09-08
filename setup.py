import os
import setuptools

with open(os.path.join(os.path.dirname(__file__), 'VERSION')) as version_file:
    version = version_file.read().strip()

with open(os.path.join(os.path.dirname(__file__), 'README.rst')) as f:
    readme = f.read()

setuptools.setup(
    name='labinform-datasafe',
    version=version,
    description='Datasafe component of the LabInform project.',
    long_description=readme,
    long_description_content_type='text/x-rst',
    author='Mirjam Schröder, Till Biskup',
    author_email='till@till-biskup.de',
    url='https://www.labinform.de/',
    project_urls={
        'Documentation': 'https://datasafe.docs.labinform.de/',
    },
    packages=setuptools.find_packages(exclude=('tests', 'docs')),
    keywords=[
        'Reproducible research',
        'data storage',
        'repository',
        'warm research data',
        'checksums',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Intended Audience :: Science/Research",
        "Development Status :: 3 - Alpha",
        "Topic :: Scientific/Engineering",
    ],
    install_requires=[
        'flask',
        'oyaml',
    ],
    extras_require={
        'dev': ['prospector', 'black', 'flask-unittest'],
        'docs': ['sphinx', 'sphinx-rtd-theme'],
    },
    entry_points={
        'labinform_fileformats': [
            'epr = datasafe.manifest:EPRFormatDetector',
        ],
    },
    python_requires='>=3.7',
)
