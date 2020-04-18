from mprint import *
import os
from maya import cmds, mel
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import json

"""
TODO:
    - Refresh button
    - Open workspace
    - Create workspace
    - Doc / Docstrings
"""


def get_recent_workspaces(user_prefs_file_path):
    start = ' -sva "RecentProjectsList" "'
    paths = list()
    if os.path.isfile(user_prefs_file_path):
        with open(user_prefs_file_path, 'r') as f:
            lines = f.readlines()

        for line in lines:
            if line.startswith(start):
                path = line.replace(start, '')[:-3]
                paths.append(path)

    workspaces = list()
    for path in paths:
        workspaces.append(path)
    workspaces.reverse()
    return workspaces


class Workspace(object):
    """
    Workspace is a class that permit to navigate between workspaces and create one.
    """

    def __init__(self, path):
        if not self.is_one(path):
            error('\'{0}\' is not a valid.'.format(path), prefix=self.__class__.__name__)
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
        current_workspace = cmds.workspace(q=True, rootDirectory=True)[:-1]
        if cls.is_one(current_workspace):
            return cls(current_workspace)
        return None

    @classmethod
    def create(cls, location, name):
        """
        Create a new workspace.
        :param location: Where the workspace should be placed (str).
        :param name: What the name of the workspace should be (str)
        :return: The freshly created workspace (Workspace or None).
        """
        if not os.path.isdir(location):
            return None

        path = '{0}/{1}'.format(location, name)

        if os.path.exists(path):
            return None

        current_workspace = cls.get_current()

        os.makedirs(path)

        mel.eval('setProject \"{0}\"'.format(path))

        for file_rule in cmds.workspace(query=True, fileRuleList=True):
            file_rule_dir = cmds.workspace(fileRuleEntry=file_rule)
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
        mel.eval('setProject \"{0}\"'.format(self.__path))

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


def ui_path_to_widget(ui_path, type_):
    pointer = omui.MQtUtil.findControl(ui_path)
    return wrapInstance(long(pointer), type_)


class FavoriteWorkspacesFile(object):
    file_name = 'favorite_workspaces.json'

    def __init__(self, path):
        if not self.is_one(path):
            error('\'{0}\' is not a valid file.'.format(path), prefix=self.__class__.__name__)
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


class Loader(QDialog):
    star_icon = QIcon('{0}/star.png'.format(os.path.dirname(__file__)))
    folder_icon = QIcon(':/folder-open.png')
    create_workspace_icon = QIcon(':/folder-new.png')

    def __init__(self, parent):
        super(Loader, self).__init__(parent)

        self.setWindowTitle(self.__class__.__name__)
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)

        current_workspace_label = QLabel('current')
        self.current_workspace_line = QLineEdit()
        self.current_workspace_line.setEnabled(False)

        current_workspace_lay = QHBoxLayout()
        current_workspace_lay.addWidget(current_workspace_label)
        current_workspace_lay.addWidget(self.current_workspace_line)

        self.workspace_list = QListWidget()
        self.workspace_list.itemDoubleClicked.connect(self.set_workspace)
        # self.workspace_list.ent.connect(self.check_refresh)

        set_btn = QPushButton('set current')
        set_btn.clicked.connect(self.set_workspace)

        open_folder_btn = QPushButton()
        open_folder_btn.setMaximumWidth(32)
        open_folder_btn.clicked.connect(self.open_folder)
        open_folder_btn.setIcon(self.folder_icon)

        favorite_btn = QPushButton()
        favorite_btn.setIcon(self.star_icon)
        favorite_btn.setMaximumWidth(32)
        favorite_btn.clicked.connect(self.toggle_favorite)

        create_workspace_btn = QPushButton()
        create_workspace_btn.setIcon(self.create_workspace_icon)
        create_workspace_btn.setMaximumWidth(32)
        create_workspace_btn.clicked.connect(self.create_workspace)

        btn_lay = QHBoxLayout()
        btn_lay.addWidget(favorite_btn)
        btn_lay.addWidget(open_folder_btn)
        btn_lay.addWidget(create_workspace_btn)
        btn_lay.addWidget(set_btn)

        main_lay = QVBoxLayout(self)
        main_lay.addLayout(current_workspace_lay)
        main_lay.addWidget(self.workspace_list)
        main_lay.addLayout(btn_lay)

    @classmethod
    def display(cls):
        parent = ui_path_to_widget('MayaWindow', QWidget)
        for child in parent.children():
            if type(child).__name__ == cls.__name__:
                child.deleteLater()

        dialog = cls(parent)
        dialog.show()
        dialog.reload()

        return dialog

    def reload(self):
        self.workspace_list.clear()

        cmds.savePrefs(general=True)

        current_workspace = Workspace.get_current()
        current_workspace_path = ''
        if isinstance(current_workspace, Workspace):
            current_workspace_path = current_workspace.get_path()

        self.current_workspace_line.setText(current_workspace_path)

        favorite_workspaces = FavoriteWorkspacesFile.get().get_workspaces()
        recent_workspaces = get_recent_workspaces('{0}userPrefs.mel'.format(cmds.internalVar(userPrefDir=True)))

        workspaces = list()
        workspaces.append(['-- favorites --', False])
        for workspace in favorite_workspaces:
            workspaces.append([workspace, True])
        workspaces.append(['-- recently opened --', False])
        for workspace in recent_workspaces:
            workspaces.append([workspace, False])

        for workspace, favorite in workspaces:
            list_item = QListWidgetItem(workspace)
            self.workspace_list.addItem(list_item)

            if not Workspace.is_one(workspace):
                list_item.setForeground(QBrush(QColor('gray')))

            if favorite is True:
                list_item.setIcon(self.star_icon)

    def get_selected_path(self):
        selected_items = self.workspace_list.selectedItems()
        if selected_items:
            text = selected_items[0].text()
            if not text.startswith('--'):
                return text
        return ''

    def set_workspace(self):
        path = self.get_selected_path()

        if path == '':
            return

        if Workspace.is_one(path):
            Workspace(path).set_current()
            info('\'{0}\' has been set as current workspace.'.format(path), prefix=self.__class__.__name__)
        else:
            warning('\'{0}\' is not valid. Skip...'.format(path), prefix=self.__class__.__name__)
            return

        self.reload()

    def toggle_favorite(self):
        path = self.get_selected_path()

        if path == '':
            return

        favorite_workspace_file = FavoriteWorkspacesFile.get()

        if path in favorite_workspace_file.get_workspaces():
            favorite_workspace_file.remove_workspace(path)
            info('\'{0}\' has been removed from the favorites.'.format(path), prefix=self.__class__.__name__)
        else:
            favorite_workspace_file.add_workspace(path)
            info('\'{0}\' has been added to the favorites.'.format(path), prefix=self.__class__.__name__)

        self.reload()

    def open_folder(self):
        path = self.get_selected_path()

        if path == '':
            return

        if not Workspace.is_one(path):
            warning('\'{0}\' is not valid. Skip...'.format(path), prefix=self.__class__.__name__)
            return

        os.startfile(path)

    def create_workspace(self):
        pass

    def enterEvent(self, *args, **kwargs):
        real_current_workspace = Workspace.get_current().get_path()
        current_workspace = self.current_workspace_line.text()

        if real_current_workspace != current_workspace:
            self.reload()
