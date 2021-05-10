from setuptools import setup

setup(
    name="phoebeshelves",
    version="0.0.1",
    description="Reading database management on the command line",
    url="https://github.com/anthony-agbay/phoebe-shelves-clt",
    author="Anthony Agbay",
    author_email="aj.agbay@gmail.com",
    packages=['phoebeshelvesclt'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'phoebeshelves = phoebeshelvesclt.main:cli_entry_point'
        ]
    }
)
