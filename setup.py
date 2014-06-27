from setuptools import setup

setup(
    name='split_block',
    version='0.0.1',
    url='http://github.com/mvj3/split_block/',
    license='MIT',
    author='David Chen',
    author_email=''.join(reversed("moc.liamg@emojvm")),
    description='split_block',
    long_description='split_block',
    packages=['split_block'],
    include_package_data=True,
    zip_safe=False,
    platforms='any',
    install_requires=[
        'etl_utils',
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
