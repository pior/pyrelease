# pylint: disable=redefined-outer-name,unused-argument
from subprocess import run, PIPE

import pytest


def git(path, *args):
    process = run(['git', '-C', path, *args], stdout=PIPE, stderr=PIPE)
    assert process.returncode == 0
    return process


@pytest.fixture
def cmd(repo):
    def func(*args, **kwargs):
        process = run(['pyreleaser', *args], cwd=repo, stdout=PIPE, stderr=PIPE, **kwargs)
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
    proc = cmd()
    assert b'Usage: pyreleaser' in proc.stdout


def test_no_setuppy(cmd, repo):
    proc = cmd('create', '1.0')
    assert b'missing setup.py file' in proc.stderr


def test_local_tag_exists(cmd, repo):
    proc = cmd('create', '0.1')
    assert b'tag already exists locally' in proc.stderr


def test_remote_tag_exists(cmd, repo):
    proc = cmd('create', '0.2')
    assert b'tag already exists remotely' in proc.stderr


def test_version_already_in_setuppy(cmd, repo, project):
    proc = cmd('create', '0.0')
    assert proc.returncode == 1
    assert b'already the current version' in proc.stderr


def test_branch_check(cmd, repo, project):
    proc = cmd('create', '0.0', '--only-on', 'wrongbranch')
    assert proc.returncode == 1
    assert b'not on the wrongbranch branch' in proc.stderr


def test_run(cmd, repo, project):
    proc = cmd('create', '1.0')
    assert proc.returncode == 0
    assert proc.stderr == b''

    setuppy = repo.join('setup.py').read()
    assert "\nVERSION = '1.0'  # " in setuppy

    tags = git(repo, 'tag').stdout.split(b'\n')
    assert b'v1.0' in tags


def test_upload_usage(cmd):
    proc = cmd('upload', '--help')
    assert b'Usage: pyreleaser' in proc.stdout


def test_upload(cmd, repo, project):
    proc = cmd('upload', '--dry-run')

    assert proc.returncode == 0
    assert proc.stderr == b''

    assert repo.join('dist', 'test-0.0.tar.gz').exists()
    assert repo.join('dist', 'test-0.0-py3-none-any.whl').exists()


def test_upload_setuppy_error(cmd, repo, project):
    repo.join('setup.py').write('raise Exception("TESTERROR")')

    proc = cmd('upload', '--dry-run')

    assert proc.returncode == 1
    assert b'failed to build distribution' in proc.stderr
    assert b'TESTERROR' in proc.stdout
