import os

from setuptools import setup, find_packages

# For development and local builds use this version number, but for real builds replace it
# with the tag found in the environment
package_version = "4.0.0.dev0"
for variable_name in ['BITBUCKET_TAG']:
    package_version = os.environ.get(variable_name, package_version)
    package_version = package_version.lstrip('v')


setup(
    name="assemblyline-service-client",
    version=package_version,
    description="Assemblyline (v4) automated malware analysis framework - Service client components.",
    long_description="This package provides the service client components for the Assemblyline v4 malware analysis framework.",
    url="https://bitbucket.org/cse-assemblyline/alv4_service_client/",
    author="CCCS Assemblyline development team",
    author_email="assemblyline@cyber.gc.ca",
    license="MIT",
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
    ],
    keywords="assemblyline malware gc canada cse-cst cse cst cyber cccs",
    packages=find_packages(exclude=['test/*']),
    install_requires=[
        'assemblyline',
        'assemblyline-core',
        'python-socketio',
        'watchdog',
    ],
    package_data={
    }
)