try:
    from setuptools import setup, find_packages
except ImportError:
    from ez_setup import use_setuptools
    use_setuptools()
    from setuptools import setup, find_packages

setup(
    name='Notification Server Example',
    version='0.1',
    description='',
    author='Ckluster Technologies LLC',
    author_email='arturo@ckluster.com',
    url='http://www.ckluster.com/',
    install_requires=[
        'Flask==0.10.1'
    ],
    packages=find_packages(exclude=['ez_setup']),
    include_package_data=True,
    zip_safe=False
)
