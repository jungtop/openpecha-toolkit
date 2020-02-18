import os
from pathlib import Path

from github import Github
from git import Repo


g = Github(os.environ.get('GITHUB_TOKEN'))
org = g.get_organization('OpenPecha')

def create_github_repo(path):
    repo = org.create_repo(path.name)
    return repo._html_url.value


def commit(repo, message, not_includes):
    has_changed = False

    # add untrack files
    for file in repo.untracked_files:
        for not_inlcude_file in not_includes:
            if not_includes in file:
                continue
        if file: repo.git.add(file)
        if has_changed is False:
            has_changed = True

    # add modified files
    if repo.is_dirty() is True:
        for file in repo.git.diff(None, name_only=True).split('\n'):
            if file: repo.git.add(file)
            if has_changed is False:
                has_changed = True
    
    if has_changed is True:
        if not message:
            message = 'Initial commit'
        repo.git.commit('-m', message)
        repo.git.push('origin', 'master')


def create_local_repo(path, remote_url):
    if (path/'.git').is_dir():
        return Repo(path)
    else:
        repo = Repo.init(path)
        old_url = remote_url.split('//')
        usr, pw = os.environ['GH_USR'], os.environ['GH_PW']
        auth_remote_url = f'{old_url[0]}//{usr}:{pw}@{old_url[1]}'
        repo.create_remote('origin', auth_remote_url)
        return repo


def github_publish(path, message=None, type=None, not_includes=None):
    path = Path(path)
    remote_repo_url = create_github_repo(path)
    local_repo = create_local_repo(path, remote_repo_url)
    commit(local_repo, message, not_includes)


def create_file(repo_name, path, content, msg, update=False):
    repo = org.get_repo(repo_name)
    if update:
        old_content = repo.get_contents(path)
        repo.update_file(old_content.path, msg, content, old_content.sha)
    else:
        repo.create_file(path, msg, content)

def get_bump_tag(repo):
    try:
        latest_release_tag = repo.get_latest_release().tag_name
    except:
        return 'v0.1'

    tag_number = round(float(latest_release_tag[1:]), 1)
    bump_tag_number = tag_number + 0.1
    return f'v{bump_tag_number}'


def create_release(repo_name, asset_paths=None):
    repo = org.get_repo(repo_name)
    bump_tag = get_bump_tag(repo)
    new_release = repo.create_git_release(
        bump_tag, bump_tag, 'Initial Release'
    )
    for asset_path in asset_paths:
        new_release.upload_asset(asset_path)


if __name__ == "__main__":
    create_release('P000002', asset_path='./output/P000300/release.zip')


    