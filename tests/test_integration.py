from subprocess import run, PIPE

import pytest


def git(path, *args):
    process = run(['git', '-C', path, *args], stdout=PIPE, stderr=PIPE)
    assert process.returncode == 0
    return process


@pytest.fixture
def cmd(repo):
    def func(*args, **kwargs):
        process = run(['pyreleaser', *args], cwd=repo, **kwargs)
        return process
    return func


@pytest.fixture
def repo(tmpdir):
    upstream = tmpdir.mkdir('upstream')
    git(upstream, 'init')

    upstream.join('afile').write('value-1')
    git(upstream, 'add', 'afile')
    git(upstream, 'commit', '-m', 'added afile')

    git(upstream, 'tag', 'v0.1')

    repo = tmpdir.mkdir('repo')
    git(tmpdir, 'clone', upstream, repo)

    repo.join('afile').write('value-2')
    git(repo, 'commit', 'afile', '-m', 'update afile')

    git(upstream, 'tag', 'v0.2')

    return repo


SETUPPY = """
from setuptools import setup

VERSION = '0.0'

setup(
    name='test',
    version=VERSION,
    author='supercat',
    author_email='supercat@cat.cat',
    url='https://cat.cat',
)
"""


@pytest.fixture
def project(repo):
    repo.join('setup.py').write(SETUPPY)
    repo.join('README').write('Read me.')


def test_usage(cmd):
    proc = cmd(stdout=PIPE, stderr=PIPE)
    assert b'arguments are required' in proc.stderr


def test_no_setuppy(cmd, repo):
    proc = cmd('1.0', stdout=PIPE, stderr=PIPE)
    assert b'missing setup.py file' in proc.stderr


def test_local_tag_exists(cmd, repo):
    proc = cmd('0.1', stdout=PIPE, stderr=PIPE)
    assert b'tag already exists locally' in proc.stderr


def test_remote_tag_exists(cmd, repo):
    proc = cmd('0.2', stdout=PIPE, stderr=PIPE)
    assert b'tag already exists remotely' in proc.stderr


def test_version_already_in_setuppy(cmd, repo, project):
    proc = cmd('0.0', stdout=PIPE, stderr=PIPE)
    assert proc.returncode == 1
    assert b'already the current version' in proc.stderr


def test_run(cmd, repo, project):
    proc = cmd('1.0', stdout=PIPE, stderr=PIPE)
    assert proc.returncode == 0
    assert b'' == proc.stderr

    setuppy = repo.join('setup.py').read()
    assert "\nVERSION = '1.0'  # " in setuppy

    tags = git(repo, 'tag').stdout.split(b'\n')
    assert b'v1.0' in tags
