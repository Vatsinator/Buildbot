#!/usr/bin/env python
# -*- coding: utf-8 -*-

import git
import sys

def _getRepo(dir):
  try:
    repo = git.Repo(dir)
    assert repo.bare == False
    return repo
  except git.NoSuchPathError as e:
    print('No such path: %s' % e)
    sys.exit(1)

def _repoPull(repo):
  ''' Switch to branch we work with translations on and pull it '''
  if repo.is_dirty():
    print('Your local clone of repo is changed. Cannot work with that.')
    sys.exit(1)
  
  # TODO

def txupdate(repoDir):
  repo = _getRepo(repoDir)
