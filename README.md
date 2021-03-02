[![Code Coverage](https://raw.githubusercontent.com/janjoswig/Indirect/master/badges/coverage.svg)](https://github.com/janjoswig/Indirect)


# Indirect

Looking for a way to manage file locations in your project? `Indirect`
is a lightweight tool to mirror relevant parts of a file system in a
project-specific, simplified fashion. It may be helpful in cases where
...

  - ... the absolute paths to files are long and complicated but files
    need to be accessed frequently in varying contexts
  - ... the files of a project are distributed over more than one
    directory trees (e.g. on different hard-disks)
  - ... directory and file names are messy and can not be changed for
    some reason

Let's consider the following directory structure as an [example](example/):

```
example/
├── system_with_complicated_and_explicit_name/
│   ├── exp_11102020/
│   │   └── replica_1/
│   │       └── data.dat
│   └── exp_11102020/
│       └── replica_2/
│           └── data.dat
├── system_two_with_an_even_more_complicated_name/
│   ├── rep1
│   │   └── exp.dat
│   ├── rep2
│   │   └── exp.dat
│   └── rep3
│       └── exp.dat
├── example.ipynb
└── info
```

In this tree we find two systems with very explicit naming and reports
for several experiments on them. Note, that the experiment-directory
naming is not very consistent. Let's assume we cannot do anything about
this and imagine we want to analyse the different reports in this
project together. In this case, we can use `Indirect` as a convenient
layer to manage these files.

```python
>>> from indirect import indirect
>>> from indirect import cookbook

>>> # We create a new project ...
>>> project = indirect.Project("example")
>>> print(f"{project!r}")
Project(alias='example', file=None)

>>> # ... set the "example" directory as a root point ...
>>> project.source["main"] = "example"

>>> # ... add new abstractions representing our systems ...
>>> project.add_abstraction(
...    "a", path="system_with_complicated_and_explicit_name"
...    )
>>> project.add_abstraction(
...    "b", path="system_two_with_an_even_more_complicated_name"
...    )

>>> # ... look for experiments under the system directories ... 
>>> path = project.source["main"] / project["a"].fullpath
>>> exp_dirs = cookbook.get_dirs(path=path, regex="^exp")
>>> for directory in exp_dirs:
...     rep_dirs = cookbook.get_dirs(path=path / directory, regex="^replica")
...     for number, sub_directory in enumerate(rep_dirs, 1):
...         project.add_abstraction(
...             f"{number}", path=f"{directory}/{sub_directory}", view=["a"]
...             )

>>> path = project.source["main"] / project["b"].fullpath
>>> rep_dirs = cookbook.get_dirs(path=path, regex="^rep")
>>> for number, directory in enumerate(rep_dirs, 1):
...     project.add_abstraction(
...         f"{number}", path=f"{directory}", view=["b"]
...         )

>>> # ... create new views for the found experiments under each system ...
>>> for system in ["a", "b"]:
...     project.views[system] = indirect.View([
...         f"{system}.{rid}"
...         for rid in project[system].next.keys()
...         ])

>>> # ... and finally add the report files
>>> for view, report_file in [("a", "data.dat"), ("b", "exp.dat")]:
...     project.add_content(
...         "report",
...         filename=report_file,
...         source="main",
...         desc="data to analyse",
...         view=view
...         )

>>> # Now we can access our data like this,
>>> # instead of fiddeling with the actual file-locations
>>> project["b.1.report"].fullpath.is_file()
True

```

