# PyReleaser

[![Version](https://img.shields.io/pypi/v/pyreleaser.svg)](https://pypi.python.org/pypi/pyreleaser)
[![License](https://img.shields.io/pypi/l/pyreleaser.svg)](https://pypi.python.org/pypi/pyreleaser)
[![PythonVersions](https://img.shields.io/pypi/pyversions/pyreleaser.svg)](https://pypi.python.org/pypi/pyreleaser)
[![Build](https://travis-ci.org/pior/pyreleaser.svg?branch=master)](https://travis-ci.org/pior/pyreleaser)

Command to release your Python project to PyPI.

Release flow:
- update setup.py version
- git tag
- git push
- twine upload


## Install

```shell
$ pip install pyreleaser
```


## Usage

```bash
$ pyreleaser 0.3 --push --upload

🍄  Updating setup.py...


🍄  Building distribution...


🍄  Create the release commit

[master ec09993] Release v0.3
 1 file changed, 1 insertion(+), 1 deletion(-)

🍄  Creating tag


🍄  Pushing to git upstream

Counting objects: 12, done.
Delta compression using up to 4 threads.
Compressing objects: 100% (12/12), done.
Writing objects: 100% (12/12), 2.71 KiB | 2.71 MiB/s, done.
Total 12 (delta 6), reused 0 (delta 0)
remote: Resolving deltas: 100% (6/6), completed with 3 local objects.
To github.com:pior/appsecrets.git
   3755ebd..ec09993  master -> master
 * [new tag]         v0.3 -> v0.3

🍄  Uploading to PyPI

Uploading distributions to https://upload.pypi.org/legacy/
Uploading appsecrets-0.3-py3-none-any.whl
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 13.8k/13.8k [00:01<00:00, 12.6kB/s]
Uploading appsecrets-0.3.tar.gz
100%|████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 9.95k/9.95k [00:00<00:00, 11.1kB/s]
```
