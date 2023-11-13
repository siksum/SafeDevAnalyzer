# setup.py
from setuptools import find_packages, setup

setup(
    name='antibug-safe_dev_analyzer',
    version='0.1.0',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.8',
    # install_requires=[
    #     'solc-select==1.0.3',

    # ],
    entry_points={
        'console_scripts': ['antibug=antibug.__main__:main', 
                            'antibug-read-storage=slither_core.tools.read_storage.__main__:main'],
    },
)