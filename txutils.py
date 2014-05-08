# -*- coding: utf-8 -*-

import os
import sys
from txclib import commands as tx
from repoutils import *


def _tx_update_source(cmd, path):
    """
    Calls cmd to generate new source translation and
    pushes new source to transifex.
    """
    os.system(cmd)
    tx.cmd_push(['--source'], path)


def _tx_pull(path):
    """
    Pull translations from Transifex
    """
    tx.cmd_pull(['--all', '--source', '--force'], path)
  

def txupdate(**kwargs):
    repoDir = kwargs['repodir']
    author = kwargs['author']
    txbranch = kwargs['txbranch']
    txgencmd = kwargs['txgencmd']
    
    txgencmd = txgencmd.replace('%REPO%', repoDir)
    repo = Repository(repoDir)
    
    print("Checking out branch %s..." % txbranch)
    repo.checkout(txbranch)

    print("Pulling...")
    repo.pull()

    print("Updating source translation...")
    _tx_update_source(txgencmd, repoDir)

    print("Pulling translations...")
    _tx_pull(repoDir)

    if repo.is_clean():
        print("No new translations.")
    else:
        print("Pushing new translations to the repo...")
        repo.commit(['Automatic translations update from Transifex', 'https://www.transifex.com/projects/p/vatsinator/'],
            author, True)
        repo.push()

