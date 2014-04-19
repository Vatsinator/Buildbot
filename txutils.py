#!/usr/bin/env python
# -*- coding: utf-8 -*-

import git
import os
import sys
from txclib import commands as tx

'''
Raised when local clone of the repository is not prepared to work with
'''
class RepoCloneDirtyError(Exception):
    pass

'''
Raised when the specified repo path does not exist
'''
class NoSuchPathError(Exception):
    pass


def _get_repo(dir):
    '''
    Get reference to repo, check if its okay and on desired branch
    '''
    try:
        repo = git.Repo(dir)
    
        if repo.bare:
            raise RepoCloneDirtyError("The repository is empty")
    
        if repo.is_dirty():
            raise RepoCloneDirtyError("Your local clone of the repository has uncommited changes")
        return repo
  
    except git.NoSuchPathError as e:
        raise NoSuchPathError("The specified path (%s) does not exist" % e)


def _repo_checkout_branch(repo, branch):
    '''
    Switch to the specified branch.
    '''
    myBranch = getattr(repo.heads, branch)
    myBranch.checkout()


def _repo_pull(repo):
    '''
    git pull
    '''
    o = repo.remotes.origin
    try:
        o.pull()
    except AssertionError:
        '''
        There is this bug, still unresolved. But pull is successful.
        '''
        pass


def _tx_update_source(cmd, path):
    '''
    Calls cmd to generate new source translation and
    pushes new source to transifex.
    '''
    os.system(cmd)
    tx.cmd_push(['--source'], path)


def _tx_pull(path):
    '''
    Pull translations from Transifex
    '''
    tx.cmd_pull(['--all', '--source', '--force'], path)
  

def txupdate(**kwargs):
    repoDir = kwargs['repodir']
    txbranch = kwargs['txbranch']
    txgencmd = kwargs['txgencmd']
    
    txgencmd = txgencmd.replace('%REPO%', repoDir)
    
    repo = _get_repo(repoDir)
    
    print("Checking out branch %s..." % txbranch)
    _repo_checkout_branch(repo, txbranch)
    
    print("Pulling repository...")
    _repo_pull(repo)

    print("Updating source translation...")
    _tx_update_source(txgencmd, repoDir)

    print("Pulling translations...")
    _tx_pull(repoDir)

