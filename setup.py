try:
    from setuptools import setup, find_packages
except:
    print ("Package setuptools has not been properly set up")

setup(
    name="analyzer",
    version="1.0.0",
    description="Twitter Analyis",
    author="Christos Andrikos*",
    packages=find_packages(),
    # install_requires=[],
    package_dir={'analyzer': 'analyzer'}
)