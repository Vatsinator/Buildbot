# -*- coding: utf-8 -*-

import pygit2


class NotAGitRepoError(Exception):
    """
    Exception raised when the Repository class is tried to be initialized
    with path that does not contain .git directory.
    """
    pass


class NoSuchBranchError(Exception):
    """
    Exception raised when the Repository tries to checkout the branch
    that does not exist.
    """
    pass


class DirtyRepoError(Exception):
    """
    Exception is raised when one tries to perform a pull on the repository
    that has uncommited changes in the working tree.
    """
    pass


class NoSuchRemoteError(Exception):
    """
    Exception raised when the repository has no such remote configured.
    """
    pass


class Repository(object):
    """
    The Repository class represents the single git repository for either
    Vatsinator or any other project. It is designed to provide similar
    usage as via the command line (ie. checkout(), pull() methods).
    """

    def __init__(self, path):
        """
        Constructor initializes the object on the existing git repository.

        Args:
            path: path to the initialized git repository.

        Raises:
            NotAGitRepoError
        """
        self.path = path
        try:
            gitdir = pygit2.discover_repository(path)
            self.repo = pygit2.Repository(gitdir)
        except KeyError:
            raise NotAGitRepoError("Not a git repository: %s" % path)

    def checkout(self, branch):
        """
        Equivalent to git checkout _branch_.

        Args:
            branch: the branch name; must be a local branch.

        Raises:
            NoSuchBranchError
        """
        gitbranch = self.repo.lookup_branch(branch)
        try:
            self.repo.checkout(gitbranch.name, pygit2.GIT_CHECKOUT_FORCE)
        except AttributeError:
            raise NoSuchBranchError("Branch %s does not exist" % branch)

    def is_clean(self):
        """
        This method checks if the repository is clean, i.e. it does not have
        any changes in the current working tree. Returns False instead.
        """
        for filepath, flags in self.repo.status().items():
            if flags != pygit2.GIT_STATUS_CURRENT and flags != pygit2.GIT_STATUS_IGNORED:
                return False
        return True

    def get_current_branch(self):
        """
        Gets current branch, but only if the current branch is on HEAD.
        Otherwise returns None.
        """
        for b in [self.repo.lookup_branch(x) for x in self.repo.listall_branches()]:
            if b.is_head():
                return b
        return None

    def get_remote(self, name='origin'):
        """
        Obtains remote reference by the specified name.

        Args:
            name: the remote reference name.
        """
        for r in self.repo.remotes:
            if r.name == name:
                return r
        return None

    def pull(self):
        """
        Equivalent to git pull.

        Raises:
            DirtyRepoError
            NoSuchRemoteError
        """
        if not self.is_clean():
            raise DirtyRepoError("The repository (%s) has uncommited changes" % self.path)

        # get current branch
        branch = self.get_current_branch()
        if branch is None:
            raise DirtyRepoError("The repository (%s) is not on the upstream branch" % self.path)

        remote = self.get_remote()
        if remote is None:
            raise NoSuchRemoteError("The repository (%s) has no remote named %s" % (self.branch, 'origin'))
        fetchresult = remote.fetch()

        upstream = branch.upstream
        # merge with the upstream tree
        mergeresult = self.repo.merge(upstream.target)
        if mergeresult.is_uptodate:  # nothing new
            return
        # update head
        self.repo.head.resolve().target = mergeresult.fastforward_oid
        # update working tree
        self.repo.reset(mergeresult.fastforward_oid, pygit2.GIT_RESET_HARD)

    def commit(self, message, author, add_new=False, **kwargs):
        """
        Equivalent to git commit.

        Args:
            message: commit message; can be either a string or an array of strings, in which case
                each string is treated as a separate paragraph.
            author: commit author, (name, email) tuple.
            add_new: if True, this function will automatically add new files to the index.
        
        Kwargs:
            committer: (name, email) tuple, default: author
        """

        if isinstance(message, list):
            message = '\n'.join(message)

        author = pygit2.Signature(author[0], author[1])

        try:
            committer = pygit2.Signature(kwargs['committer'][0], kwargs['committer'][1])
        except (IndexError, KeyError):
            committer = author

        # update index
        index = self.repo.index
        index.read()
        for filepath, flags in self.repo.status().items():
            if flags == pygit2.GIT_STATUS_WT_NEW:
                if add_new:
                    index.add(filepath)
            elif flags == pygit2.GIT_STATUS_WT_MODIFIED:
                index.add(filepath)
        index.write()

        treeid = self.repo.index.write_tree()
        head = self.repo.head
        commit = self.repo.create_commit('HEAD', author, committer, message, treeid, [head.target])

    def push(self):
        """
        Equivalent to git push.
        """
        remote = self.get_remote()
        branch = self.get_current_branch()
        remote.push(branch.name)


