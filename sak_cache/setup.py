from setuptools import find_packages, setup


setup(
    name='sak-cache',
    version='0.0.1',
    packages=find_packages(),
    install_requires=[
        "redis>=2.10.5",
        "funcy>=1.14"
    ],
)
