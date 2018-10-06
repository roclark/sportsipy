from setuptools import find_packages, setup

with open('README.rst', 'r') as f:
    long_description = f.read()

with open('VERSION', 'r') as f:
    version = f.read()

setup(
    name='sportsreference',
    version=version,
    author='Robert Clark',
    author_email='robdclark@outlook.com',
    description='A free sports API written for python',
    long_description=long_description,
    license='MIT',
    url='https://github.com/roclark/sportsreference',
    packages=find_packages(),
    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',
    keywords='stats sports api sportsreference machine learning',
    install_requires=[
        "pandas >= 0.21.0",
        "pyquery >= 1.4.0",
        "requests >= 2.18.4"
    ],
    classifiers=(
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ),
)
