from setuptools import find_packages, setup

with open('README.rst', 'r') as f:
    long_description = f.read()

with open('VERSION', 'r') as f:
    version = f.read()

setup(
    name='sportsipy',
    version=version,
    author='Robert Clark',
    author_email='robdclark@outlook.com',
    description='A free sports API written for python',
    long_description=long_description,
    license='MIT',
    url='https://github.com/roclark/sportsipy',
    packages=find_packages(),
    python_requires='>=3.10',
    keywords='stats sports api sportsipy machine learning',
    install_requires=[
        "numpy >= 1.26.4, < 3",
        "pandas >= 2.2.2, < 3",
        "pyquery >= 2.0, < 3",
        "requests >= 2.32.3, < 3",
        "cloudscraper == 1.2.71",
        "filelock >= 3.13, < 5",
    ],
    classifiers=(
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.12',
        'License :: OSI Approved :: MIT License',
        'Operating System :: POSIX :: Linux',
    ),
)
