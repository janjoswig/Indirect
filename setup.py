from setuptools import setup


with open("README.md", "r") as readme:
    desc = readme.read()

sdesc = "File system abstraction for Python based projects and workflows"

requirements_map = {"mandatory": "",
                    "dev": "-dev",}

requirements = {}
for category, fname in requirements_map.items():
    with open(f"requirements{fname}.txt") as fp:
        requirements[category] = fp.read().strip().split("\n")

setup(
    name="indirect",
    version="0.0.0",
    keywords=["Project Management", "Workflow Optimisation"],
    scripts=["indirect/indirect.py"],
    author="Jan-Oliver Joswig",
    author_email="jan.o.joswig@gmail.com",
    description=sdesc,
    long_description=desc,
    long_description_content_type="text/markdown",
    url="https://github.com/janjoswig/Indirect",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        ],
    extras_require={
        "dev": requirements["dev"],
        },
)
