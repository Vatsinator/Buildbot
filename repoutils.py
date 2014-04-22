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


class DirtyRepoError(Exception):
    '''
    Exception is raised when one tries to perform a pull on the repository
    that has uncommited changes in the working tree.
    '''
    pass


class NoSuchRemoteError(Exception):
    '''
    Exception raised when the repository has no such remote configured.
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
            self.repo.checkout(gitbranch.name, pygit2.GIT_CHECKOUT_FORCE)
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
    
    def pull(self):
        '''
        Equivalent to git pull.
        '''
        if not self.is_clean():
            raise DirtyRepoError("The repository (%s) has uncommited changes" % self.path)
        
        # get current branch
        branch = None
        for b in [self.repo.lookup_branch(x) for x in self.repo.listall_branches()]:
            if b.is_head():
                branch = b
                break

        if branch is None:
            raise DirtyRepoError("The repository (%s) is not on the upstream branch" % self.path)
        
        fetchresult = None
        remotename = u'origin'
        for r in self.repo.remotes:
            if r.name == remotename:
                fetchresult = r.fetch()
                break
        
        if fetchresult is None:
            raise NoSuchRemoteError("The repository (%s) has no remote named %s" % (self.branch, remotename))

        upstream = branch.upstream
        # merge with the upstream tree
        mergeresult = self.repo.merge(upstream.target)
        if mergeresult.is_uptodate: # nothing new
            return
        # update head
        self.repo.head.resolve().target = mergeresult.fastforward_oid
        # update working tree
        self.repo.reset(mergeresult.fastforward_oid, pygit2.GIT_RESET_HARD)
        

