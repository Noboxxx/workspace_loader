"""
package : 
file : toSort.py

description : 
"""

# imports python
import os
import json

# imports third-parties
from maya import cmds, mel
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui

# imports local
import workspace_loader.core.messages
import workspace_loader.core.workspaces

# from PySide2.QtWidgets import *
# from PySide2.QtGui import *
# from PySide2.QtCore import *
# import * are usually really really bad Idea. stands for really hard debug at some point. from X import Y or absolute import is better



def ui_path_to_widget(ui_path, type_):
    """doc string

    :param ui_path:
    :type ui_path:
    :param type_:
    :type type_:
    :return:
    :rtype:
    """

    pointer = omui.MQtUtil.findControl(ui_path)
    return wrapInstance(long(pointer), type_)


class FavoriteWorkspacesFile(object):
    file_name = 'favorite_workspaces.json'

    def __init__(self, path):
        if not self.is_one(path):
            workspace_loader.core.messages.error('\'{0}\' is not a valid file.'
                                                 .format(path), prefix=self.__class__.__name__)
        self.__path = path

    @classmethod
    def is_one(cls, path):
        if os.path.isfile(path):
            if path.split('/')[-1] == cls.file_name:
                return True
        return False

    @classmethod
    def get(cls):
        location = cmds.internalVar(userAppDir=True)[:-1]
        path = '{0}/{1}'.format(location, cls.file_name)

        if os.path.exists(path):
            return cls(path)
        return cls.create(location)

    @classmethod
    def create(cls, location):
        path = '{0}/{1}'.format(location, cls.file_name)

        with open(path, 'w') as f:
            json.dump(list(), f)

        return cls(path)

    def get_workspaces(self):
        content = self.read()
        if isinstance(content, list):
            return content
        return list()

    def read(self):
        with open(self.__path, 'r') as f:
            return json.load(f)

    def write(self, content):
        with open(self.__path, 'w') as f:
            json.dump(content, f)

    def add_workspace(self, path):
        workspaces = self.get_workspaces()
        if path in workspaces:
            workspaces.remove(path)
        workspaces.insert(0, path)

        self.write(workspaces)

    def remove_workspace(self, path):
        workspaces = self.get_workspaces()
        workspaces.remove(path)
        self.write(workspaces)


class Favorite(object):

    def __init__(self, path):
        self.__path = path

    def remove(self):
        FavoriteWorkspacesFile.get().remove_workspace(self.__path)

    @classmethod
    def get_all(cls):
        favorites = []
        for favorite in FavoriteWorkspacesFile.get().get_workspaces():
            favorites.append(cls(favorite))
        return favorites

    @classmethod
    def create(cls, recent):
        FavoriteWorkspacesFile.get().add_workspace(recent.get_path())
        return cls(recent.get_path())

    def get_workspace(self):
        if workspace_loader.core.workspaces.Workspace.is_one(self.__path):
            return workspace_loader.core.workspaces.Workspace(self.__path)
        return None

    def get_path(self):
        return self.__path


class Recent(object):

    def __init__(self, path):
        self.__path = path

    @classmethod
    def get_all(cls):
        recents = []
        for recent in mel.eval('optionVar -query "RecentProjectsList"') or list():
            recents.append(cls(recent))

        recents.reverse()
        return recents

    def set_as_favorite(self):
        return Favorite.create(self)

    def get_path(self):
        return self.__path

    def get_workspace(self):
        if workspace_loader.core.workspaces.Workspace.is_one(self.__path):
            return workspace_loader.core.workspaces.Workspace(self.__path)
        return None # this return is useless
