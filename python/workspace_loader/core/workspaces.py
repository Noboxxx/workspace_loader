"""
package : 
file : workspaces.py

description : 
"""

# imports python
import os

# imports third-parties
import maya.mel
import maya.cmds

# imports local
import workspace_loader.core.messages


def get_recent_workspaces():
    """doc string here

    :return:
    :rtype:
    """

    # get recent
    recent = maya.mel.eval('optionVar -query "RecentProjectsList"') or [] # [] has faster initialization than list()
    recent.reverse()

    # return
    return recent


class Workspace(object):
    """
    Workspace is a class that permit to navigate between workspaces and create one.
    """

    def __init__(self, path):
        if not self.is_one(path):
            workspace_loader.core.messages.error('\'{0}\' is not a valid.'.format(path), prefix=self.__class__.__name__)
        self.__path = path

    @classmethod
    def is_one(cls, path):
        """
        Make sure that the given path is indeed a workspace path.
        :param path: A workspace path (str).
        :return: Return True if the path is indeed a workspace path (bool).
        """
        if os.path.isdir(path):
            if 'workspace.mel' in os.listdir(path):
                return True
        return False

    @classmethod
    def get_current(cls):
        """
        Get the current workspace.
        :return: Workspace or None.
        """
        current_workspace = maya.cmds.workspace(q=True, rootDirectory=True)[:-1]
        if cls.is_one(current_workspace):
            return cls(current_workspace)
        return None

    @classmethod
    def create(cls, path):
        """
        Create a new workspace in the selected location.
        :param path: str
        :return: Workspace or None
        """

        # return
        if not os.path.isdir(path) or cls.is_one(path):
            return

        # execute
        current_workspace = cls.get_current()

        maya.mel.eval('setProject \"{0}\"'.format(path))

        for file_rule in maya.cmds.workspace(query=True, fileRuleList=True):
            file_rule_dir = maya.cmds.workspace(fileRuleEntry=file_rule)
            maya_file_rule_dir = '{0}/{1}'.format(path, file_rule_dir)
            if not os.path.exists(maya_file_rule_dir):
                os.makedirs(maya_file_rule_dir)

        if current_workspace:
            current_workspace.set_current()

        return cls(path)

    def set_current(self):
        """
        Set the workspace as current workspace.
        :return: Nothing
        """

        maya.mel.eval('setProject \"{0}\"'.format(self.__path))

    def get_name(self):
        """
        Get the name of the last folder of the workspace's full path.
        :return: str
        """
        return self.__path.split('/')[-1]

    def get_path(self):
        """
        Get workspace's path.
        :return: str
        """
        return self.__path
