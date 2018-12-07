from setuptools import setup
import unittest

setup(
    name="ipc-unix",
    version="0.0.0",
    url="https://github.com/realorangeone/ipc-unix",
    license='MIT',
    author="Jake Howard",
    description="Inter-Process Communication using unix sockets",
    packages=['ipc_unix'],
    include_package_data=True,
    zip_safe=False,
    pathon_requires='>=3.4',
    install_requires=[
        'ujson'
    ],
    project_urls={
        'GitHub: Issues': 'https://github.com/realorangeone/ipc-unix/issues'
    },
    test_suite="nose2.collector.collector"
)
