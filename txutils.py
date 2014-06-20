# -*- coding: utf-8 -*-

import os
import subprocess

from txclib import commands as tx

from repoutils import *


class NoLupdateExecFound(Exception):
    """
    This exception is raised if lupdate application is not found
    in the system.
    """
    pass


class LupdateExecError(Exception):
    """
    This exception is raised when lupdate exec fails.
    """
    pass


def _find_lupdate():
    """
    Find lupdate program in the system.
    :return: The lupdate exec complete path.
    """
    names = ['lupdate', 'lupdate-qt4']
    for p in os.environ['PATH'].split(':'):
        for n in names:
            path = os.path.join(p, n)
            if os.path.isfile(path):
                return path
    raise NoLupdateExecFound()


def _tx_update_source(path):
    """
    Push new source to Transifex.
    :param path: Path to Transifex project.
    """
    lupdate = _find_lupdate()
    r = subprocess.call([lupdate, '-recursive', '%s/source/' % path, '-no-obsolete'])
    if r != 0:
        raise LupdateExecError(lupdate)

    # push source for vatsinator application
    tx.cmd_push(['--source', '--resource=vatsinator.application'], path)


def _tx_pull(path):
    """
    Pull translations from Transifex.
    """
    tx.cmd_pull(['--all', '--source', '--force'], path)


def txupdate(**kwargs):
    """
    Pull Vatsinator repository, update transifex source, pull new translations and push them to the main repository.
    @param kwargs:
    """
    repo_dir = kwargs['repodir']
    author = kwargs['author']
    txbranch = kwargs['txbranch']

    repo = Repository(repo_dir)

    print("Checking out branch %s..." % txbranch)
    repo.checkout(txbranch)

    print("Pulling...")
    repo.pull()

    print("Updating source translation...")
    _tx_update_source(repo_dir)

    print("Pulling translations...")
    _tx_pull(repo_dir)

    if repo.is_clean():
        print("No new translations.")
    else:
        print("Pushing new translations to the repo...")
        repo.commit(
            ['Automatic translations update from Transifex', 'https://www.transifex.com/projects/p/vatsinator/'],
            author, True)
        repo.push()

