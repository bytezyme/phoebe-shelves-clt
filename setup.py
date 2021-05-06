from setuptools import setup

setup(
    name="owl_shelves_clt",
    version="0.0.1",
    description="Reading database management on the command line",
    url="https://github.com/anthony-agbay/owl_shelves_clt",
    author="Anthony Agbay",
    author_email="aj.agbay@gmail.com",
    packages=['owl_shelves_clt'],
    zip_safe=False,
    entry_points={
        'console_scripts': [
            'owl_shelves_clt = owl_shelves_clt.__main__:cli'
        ]
    }
)