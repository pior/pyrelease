import argparse
import fileinput
import pathlib
import re
import sys
from subprocess import run, PIPE, CalledProcessError


class Error(Exception):
    pass


def title(msg):
    print(f'\n🍄  {msg}\n')


def capture(args, check=True):
    result = run(args, check=check, stdout=PIPE)
    return result.stdout.strip().decode()


def get_git_branch():
    return capture(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])


def get_git_tags(remote=False):
    if remote:
        output = capture(['git', 'ls-remote', '--tags', 'origin'])
    else:
        output = capture(['git', 'show-ref', '--tags'], check=False)

    lines = re.findall(r'refs/tags/([^^\n]+)', output)
    return list(set(lines))


def is_git_clean():
    result = run(['git', 'diff-index', '--quiet', 'HEAD', '--'], check=False, stdout=PIPE)
    return result.returncode == 0


def read_version_setup_py():
    output = capture(['python', 'setup.py', '--version'])
    return output


def update_version_setup_py(version):
    changed = False
    for line in fileinput.input('setup.py', inplace=True):
        if re.match(r'VERSION\s*=', line):
            print(f"VERSION = '{version}'  # maintained by release tool")
            changed = True
        else:
            print(line, end='')
    return changed


def is_twine_installed():
    result = run(['which', 'twine'])
    return result.returncode == 0


def release(options):
    # pylint: disable=too-many-branches
    version_string = options.version
    if version_string.startswith('v'):
        raise Error('A version can\'t begin with a v')
    version = f'v{version_string}'

    # Checks

    if options.upload:
        if not is_twine_installed():
            raise Error('twine is not installed')

    if options.only_on:
        current_branch = get_git_branch()
        if current_branch != options.only_on:
            raise Error(f'not on the {options.only_on} branch. ({current_branch})')

    if not is_git_clean():
        raise Error('uncommited files')

    if version in get_git_tags(remote=False):
        raise Error(f'tag already exists locally ({version})')

    if version in get_git_tags(remote=True):
        raise Error(f'tag already exists remotely ({version})')

    if not pathlib.Path('setup.py').exists():
        raise Error('missing setup.py file')

    if version_string == read_version_setup_py():
        raise Error('already the current version')

    # Prepare

    title('Updating setup.py...')
    changed = update_version_setup_py(version_string)
    if not changed:
        raise Error('failed to update setup.py')

    # Build

    title('Building distribution...')
    run(['rm', '-rf', 'dist'], check=True)
    result = run(['python', 'setup.py', 'sdist', 'bdist_wheel'], stdout=PIPE)
    if result.returncode != 0:
        raise Error('failed to build distribution')

    # Create

    title('Create the release commit')
    run(['git', 'add', 'setup.py'], check=True)
    run(['git', 'commit', '-m', f'Release {version}'], check=True)

    title('Creating tag')
    run(['git', 'tag', '-a', '-m', f'Release tag for {version}', version], check=True)

    # Publish

    if options.push:
        title('Pushing to git upstream')
        run(['git', 'push', '--follow-tags'], check=True)
    else:
        title('Don\'t forget to push:\n  git push --follow-tags\n')

    if options.upload:
        title('Uploading to PyPI')
        run(['twine', 'upload', 'dist/*'], check=True)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('version', help='Version string without the "v"')
    parser.add_argument('--only-on', type=str, metavar='BRANCH-NAME')
    parser.add_argument('--push', default=False, action='store_true')
    parser.add_argument('--upload', default=False, action='store_true')
    args = parser.parse_args()

    try:
        release(args)
    except (CalledProcessError, Error) as err:
        print(f'\n💥  Fatal: {err}\n', file=sys.stderr)
        sys.exit(1)
    except KeyboardInterrupt:
        sys.exit(1)
