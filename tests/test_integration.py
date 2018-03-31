from subprocess import run, PIPE

import pytest


def git(path, *args):
    process = run(['git', '-C', path, *args], stdout=PIPE, stderr=PIPE)
    assert process.returncode == 0


@pytest.fixture
def cmd(repo):
    def func(*args, **kwargs):
        process = run(['pyrelease', *args], cwd=repo, **kwargs)
        return process
    return func


@pytest.fixture
def repo(tmpdir):
    upstream = tmpdir.mkdir('upstream')
    git(upstream, 'init')

    repo = tmpdir.mkdir('repo')
    git(tmpdir, 'clone', upstream, repo)

    repo.join('afile').write('afile-content')
    git(repo, 'add', 'afile')
    git(repo, 'commit', '-m', 'added afile')
    return repo


def test_usage(cmd):
    proc = cmd(stdout=PIPE, stderr=PIPE)
    assert proc.returncode == 2
    assert b'arguments are required' in proc.stderr


def test_poi(cmd, repo):
    proc = cmd('1.0', stdout=PIPE, stderr=PIPE)
    assert proc.returncode == 2
    assert b'arguments are required' in proc.stderr
