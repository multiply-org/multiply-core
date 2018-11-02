from subprocess import call
import git
import os

repos_to_check = ['C:\\Users\\tonio\\Projekte\\multiply\\data_access']
repo_tags = ['v0.3']


def _is_newer_than(latest_git_version: str, installed_version: str):
    git_version_array = latest_git_version[1:].split('.')
    installed_version_array = installed_version[1:].split('.')
    i = 0
    while i < len(git_version_array) and i < len(installed_version_array):
        if int(git_version_array[i]) > int(installed_version_array[i]):
            return True
        elif int(git_version_array[i]) < int(installed_version_array[i]):
            return False
        i += 1
    if len(git_version_array) > len(installed_version_array):
        return True
    elif len(git_version_array) < len(installed_version_array):
        return False


def update():
    for repo in repos_to_check:
        cmd_git = git.cmd.Git(repo)
        tags = cmd_git.tag().split('\n')
        if _is_newer_than(tags[-1], repo_tags[0]):
            cmd_git.checkout('tags/{}'.format(tags[-1]))
            os.chdir(repo)
            call(["python", "setup.py", "develop"])
