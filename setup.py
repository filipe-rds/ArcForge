from setuptools import setup, find_packages

with open("requirements.txt") as f:
    requirements = f.read().splitlines()

setup(
    name="arcforge",
    version="0.1.0",
    packages=find_packages(),
    install_requires=requirements,
    author="Filipe Rodriges, Lucas Pedro, Gabriel Felix",
    author_email="filiperodrigues.estudo@gmail.com, lucasjaud19@gmail.com, gfedacs@hotmail.com",
    description="Um framework web em Python",
    keywords="web, framework, python",
    url="https://github.com/filipe-rds/ArcForge",
    project_urls={
        "Author: Filipe Rodrigues": "https://github.com/filipe-rds",
        "Author: Lucas Pedro": "https://github.com/LucasJaud",
        "Author: Gabriel Felix": "https://github.com/gfedacs",
    }
)