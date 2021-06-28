from setuptools import setup, find_packages

setup(
    name="HexChess",
    packages=find_packages(),
    use_scm_version= {
        'write_to': 'HexChess/_version.py'
    },
    setup_requires=['setuptools_scm'],
    description="Play Hexagonal Chess!",
    author='Janahan Selvanayagam',
    author_email='seljanahan@hotmail.com',
    install_requires=[
        'pyparsing',
    ],
    extras_require = {
        'FULL': ['click','pygame']
    },
    # entry_points='''
    #     [console_scripts]
    #     simi=simianpy.scripts:simi
    # ''',
    zip_safe=False,
    include_package_data=True
)