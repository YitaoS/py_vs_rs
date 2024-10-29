from setuptools import setup, find_packages

def parse_requirements(filename):
    with open(filename, "r") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name='my_python_project',
    version='0.1',
    packages=find_packages(),
    install_requires=parse_requirements('requirements.txt'),
    extras_require={
        'dev': parse_requirements('dev-requirements.txt'),
    },
    entry_points={
        'console_scripts': [
        ],
    },
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.6',
)
