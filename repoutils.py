# -*- coding: utf-8 -*-

import pygit2


class NotAGitRepoError(Exception):
    '''
    Exception raised when the Repository class is tried to be initialized
    with path that does not contain .git directory.
    '''
    pass


class NoSuchBranchError(Exception):
    '''
    Exception raised when the Repository tries to checkout the branch
    that does not exist.
    '''
    pass


class Repository:
    '''
    The Repository class represents the single git repository for either
    Vatsinator or any other project. It is designed to provide similar
    usage as via the command line (ie. checkout(), pull() methods).
    '''

    def __init__(self, path):
        '''
        Constructor takes path to the git repository. Can raise NotAGitRepoError.
        '''
        self.path = path
        try:
            gitdir = pygit2.discover_repository(path)
            self.repo = pygit2.Repository(gitdir)
        except KeyError:
            raise NotAGitRepoError("Not a git repository: %s" % path)
    
    def checkout(self, branch):
        '''
        Equivalent to git checkout _branch_.
        '''
        gitbranch = self.repo.lookup_branch(branch)
        try:
            self.repo.checkout(gitbranch.name)
        except AttributeError:
            raise NoSuchBranchError("Branch %s does not exist" % branch)
    
    def is_clean(self):
        '''
        This method checks if the repository is clean, i.e. it does not have
        any changes in the current working tree. Returns False instead.
        '''
        for filepath, flags in self.repo.status().items():
            if flags != pygit2.GIT_STATUS_CURRENT and flags != pygit2.GIT_STATUS_IGNORED:
                return False
        return True


