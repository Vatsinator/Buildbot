#!/usr/bin/env python
# -*- coding: utf-8 -*-

import os
import sh
import sys
from txclib import commands as tx

'''
Raised when local clone of the repository is not prepared to work with
'''
class RepoCloneDirtyError(Exception):
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
    
    git = sh.git.bake(_cwd=repoDir)
    diff = git.diff('--no-ext-diff', '--quiet', '--exit-code')
    if len(diff) > 0:
        raise RepoCloneDirtyError('Your local clone of Vatsinator repository is not clean!')
    
    print("Checking out branch %s..." % txbranch)
    git.checkout(txbranch)

    print("Pulling...")
    git.pull()

    print("Updating source translation...")
    _tx_update_source(txgencmd, repoDir)

    print("Pulling translations...")
    _tx_pull(repoDir)

    diff = git.diff('--no-ext-diff', '--quiet', '--exit-code')
    clean = len(diff) == 0

    if clean:
        print("No new translations.")
    else:
        print("Pushing new translations to the repo...")
        git.add('.')
        git.commit('-am', 'Automatic translations update from Transifex\n')

