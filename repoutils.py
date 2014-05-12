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
        Initialize the Repository instance in the given path. The directory
        under path has to contain .git.
        @type path: str
        @raise NotAGitRepoError: The given path is not a git directory.
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
        @param branch: The branch name; must be a local branch.
        @raise NoSuchBranchError: The given repository has no branch of the given name.
        """
        gitbranch = self.repo.lookup_branch(branch)
        try:
            self.repo.checkout(gitbranch.name, pygit2.GIT_CHECKOUT_FORCE)
        except AttributeError:
            raise NoSuchBranchError("Branch %s does not exist" % branch)

    def is_clean(self):
        """
        Check if the repository is clean, i.e. it does not have any changes in the current working tree.
        @return: True if the current working tree is clean, False otherwise.
        """
        for filepath, flags in self.repo.status().items():
            if flags != pygit2.GIT_STATUS_CURRENT and flags != pygit2.GIT_STATUS_IGNORED:
                return False
        return True

    @property
    def current_branch(self):
        """
        Get current branch reference, but only if the current branch is on HEAD.
        @return: The current local branch reference or None, if on detached state.
        """
        for b in [self.repo.lookup_branch(x) for x in self.repo.listall_branches()]:
            if b.is_head():
                return b
        return None

    def get_remote(self, name='origin'):
        """
        Obtain remote reference of the specified name.
        @param name: Name of the remote.
        @return: The remote reference.
        """
        for r in self.repo.remotes:
            if r.name == name:
                return r
        return None

    def pull(self):
        """
        Pull the current branch from remote.
        @raise NoSuchRemoteError: The current branch does not have the remote origin.
        @raise DirtyRepoError: The working directory is not clean.
        """
        if not self.is_clean():
            raise DirtyRepoError("The repository (%s) has uncommited changes" % self.path)

        branch = self.current_branch
        if branch is None:
            raise DirtyRepoError("The repository (%s) is not on the upstream branch" % self.path)

        remote = self.get_remote()
        if remote is None:
            raise NoSuchRemoteError("The repository (%s) has no remote named %s" % (self.branch, 'origin'))
        remote.fetch()

        upstream = branch.upstream
        # merge with the upstream tree
        merge_result = self.repo.merge(upstream.target)
        if not merge_result.is_uptodate:
            # update head
            self.repo.head.resolve().target = merge_result.fastforward_oid
            # update working tree
            self.repo.reset(merge_result.fastforward_oid, pygit2.GIT_RESET_HARD)

    def commit(self, message, author, add_new=False, **kwargs):
        """
        Equivalent to git commit.
        @param message: The commit message; can be either a string or an array of strings, in which case
                each string is treated as a separate paragraph.
        @param author: The commit author; (name, email) tuple.
        @param add_new: Add new files to the index.
        @param kwargs: committer: The commit maker; (name, email) tuple.
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
        Push to the remote.
        """
        remote = self.get_remote()
        branch = self.get_current_branch()
        remote.push(branch.name)


