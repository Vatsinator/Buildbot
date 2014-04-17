#!/usr/bin/env python
# -*- coding: utf-8 -*-

import git
import sys

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
  o.pull()
  

def txupdate(**kwargs):
  repoDir = kwargs['repodir']
  txbranch = kwargs['txbranch']
  
  repo = _get_repo(repoDir)
  
  print("Checking out branch %s..." % txbranch)
  _repo_checkout_branch(repo, txbranch)
  
  print("Pulling...")
  _repo_pull(repo)
