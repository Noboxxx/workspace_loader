import os
from maya import cmds, mel
from PySide2.QtWidgets import *
from PySide2.QtGui import *
from PySide2.QtCore import *
from shiboken2 import wrapInstance
import maya.OpenMayaUI as omui
import json
import webbrowser
import sys


def f_msg(msg, prefix, suffix, new_line_after):
    s = ''

    if prefix != '':
        s += '{0} : '.format(prefix)

    s += str(msg)

    if suffix != '':
        s += ' / {0}'.format(suffix)

    if new_line_after:
        s += '\n'

    return s


def warning(msg='', prefix='', suffix='', new_line_after=False):
    cmds.warning(f_msg(msg, prefix, suffix, new_line_after))


def error(msg='', prefix='', suffix='', new_line_after=False):
    cmds.error(f_msg(msg, prefix, suffix, new_line_after))


def info(msg='', prefix='', suffix='', new_line_after=False):
    sys.stdout.write('{0}\n'.format(f_msg(msg, prefix, suffix, new_line_after)))


def get_recent_workspaces():
    recent = mel.eval('optionVar -query "RecentProjectsList"') or list()
    recent.reverse()
    return recent


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
    def create(cls, path):
        """
        Create a new workspace in the selected location.
        :param path: str
        :return: Workspace or None
        """
        if os.path.isdir(path):
            if not cls.is_one(path):
                current_workspace = cls.get_current()

                mel.eval('setProject \"{0}\"'.format(path))

                for file_rule in cmds.workspace(query=True, fileRuleList=True):
                    file_rule_dir = cmds.workspace(fileRuleEntry=file_rule)
                    maya_file_rule_dir = '{0}/{1}'.format(path, file_rule_dir)
                    if not os.path.exists(maya_file_rule_dir):
                        os.makedirs(maya_file_rule_dir)

                if current_workspace:
                    current_workspace.set_current()

                return cls(path)
        return None

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


class Favorite(object):

    def __init__(self, path):
        self.__path = path

    def remove(self):
        FavoriteWorkspacesFile.get().remove_workspace(self.__path)

    @classmethod
    def get_all(cls):
        favorites = list()
        for favorite in FavoriteWorkspacesFile.get().get_workspaces():
            favorites.append(cls(favorite))
        return favorites

    @classmethod
    def create(cls, recent):
        FavoriteWorkspacesFile.get().add_workspace(recent.get_path())
        return cls(recent.get_path())

    def get_workspace(self):
        if Workspace.is_one(self.__path):
            return Workspace(self.__path)
        return None

    def get_path(self):
        return self.__path


class Recent(object):

    def __init__(self, path):
        self.__path = path

    @classmethod
    def get_all(cls):
        recents = list()
        for recent in mel.eval('optionVar -query "RecentProjectsList"') or list():
            recents.append(cls(recent))

        recents.reverse()
        return recents

    def set_as_favorite(self):
        return Favorite.create(self)

    def get_path(self):
        return self.__path

    def get_workspace(self):
        if Workspace.is_one(self.__path):
            return Workspace(self.__path)
        return None


class Loader(QDialog):
    star_icon = QIcon('{0}/star.png'.format(os.path.dirname(__file__)))
    folder_icon = QIcon(':/folder-open.png')
    folder_new_icon = QIcon(':/folder-new.png')
    search_icon = QIcon(':/search.png')
    help_icon = QIcon(':/help.png')
    doc_url = 'https://github.com/Noboxxx/workspace_loader'

    def __init__(self, parent):
        super(Loader, self).__init__(parent)

        self.setWindowTitle(self.__class__.__name__)
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)
        if cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ Qt.WindowContextHelpButtonHint)
        elif cmds.about(macOS=True):
            self.setWindowFlags(Qt.Tool)

        current_workspace_label = QLabel('current')
        self.current_workspace_line = QLineEdit()
        self.current_workspace_line.setEnabled(False)

        current_workspace_lay = QHBoxLayout()
        current_workspace_lay.addWidget(current_workspace_label)
        current_workspace_lay.addWidget(self.current_workspace_line)

        self.workspace_list = QListWidget()
        self.workspace_list.itemDoubleClicked.connect(self.set_workspace)

        set_btn = QPushButton('set current')
        set_btn.clicked.connect(self.set_workspace)

        set_and_open_btn = QPushButton('open file')
        set_and_open_btn.clicked.connect(self.set_and_open)

        open_folder_btn = QPushButton()
        open_folder_btn.setMaximumWidth(32)
        open_folder_btn.clicked.connect(self.open_workspace)
        open_folder_btn.setIcon(self.folder_icon)

        favorite_btn = QPushButton()
        favorite_btn.setIcon(self.star_icon)
        favorite_btn.setMaximumWidth(32)
        favorite_btn.clicked.connect(self.toggle_favorite)

        create_workspace_btn = QPushButton()
        create_workspace_btn.setIcon(self.folder_new_icon)
        create_workspace_btn.setMaximumWidth(32)
        create_workspace_btn.clicked.connect(self.create_workspace)

        open_in_explorer_btn = QPushButton()
        open_in_explorer_btn.setIcon(self.search_icon)
        open_in_explorer_btn.setMaximumWidth(32)
        open_in_explorer_btn.clicked.connect(self.open_in_explorer)

        help_btn = QPushButton()
        help_btn.setIcon(self.help_icon)
        help_btn.setMaximumWidth(32)
        help_btn.clicked.connect(self.help)

        btn_lay = QHBoxLayout()
        btn_lay.addWidget(favorite_btn)
        btn_lay.addWidget(open_folder_btn)
        btn_lay.addWidget(create_workspace_btn)
        btn_lay.addWidget(open_in_explorer_btn)
        btn_lay.addWidget(set_btn)
        btn_lay.addWidget(set_and_open_btn)
        btn_lay.addWidget(help_btn)

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

        current_workspace = Workspace.get_current()
        current_workspace_path = ''
        if isinstance(current_workspace, Workspace):
            current_workspace_path = current_workspace.get_path()

        self.current_workspace_line.setText(current_workspace_path)

        list_item = QListWidgetItem('-- favorites --')
        self.workspace_list.addItem(list_item)

        for favorite in Favorite.get_all():
            list_item = QListWidgetItem(favorite.get_path())
            list_item.setIcon(self.star_icon)
            list_item.setData(Qt.UserRole, favorite)
            self.workspace_list.addItem(list_item)

            if not favorite.get_workspace():
                list_item.setForeground(QBrush(QColor('gray')))

        list_item = QListWidgetItem('')
        self.workspace_list.addItem(list_item)

        list_item = QListWidgetItem('-- recently opened --')
        self.workspace_list.addItem(list_item)

        for recent in Recent.get_all():
            list_item = QListWidgetItem(recent.get_path())
            list_item.setData(Qt.UserRole, recent)
            self.workspace_list.addItem(list_item)

            if not recent.get_workspace():
                list_item.setForeground(QBrush(QColor('gray')))

    def get_selected_data(self):
        selected_items = self.workspace_list.selectedItems()
        if selected_items:
            return selected_items[-1].data(Qt.UserRole)
        return None

    def set_workspace(self):
        data = self.get_selected_data()

        if data is not None:
            workspace = data.get_workspace()

            if workspace is not None:
                self._set_as_current_workspace(workspace)
                return True
            else:
                warning('\'{0}\' cannot be set because it is invalid (maybe it does not exist anymore). Cancel...'.format(data.get_path()), prefix=self.__class__.__name__)

        return False

    def toggle_favorite(self):
        data = self.get_selected_data()

        if isinstance(data, Favorite):
            data.remove()
            self.reload()
            return
        elif isinstance(data, Recent):
            data.set_as_favorite()
            self.reload()
            return

    def open_workspace(self):
        path = QFileDialog.getExistingDirectory(self, "Create workspace in location")

        if path == '':
            return

        if Workspace.is_one(path):
            workspace = Workspace(path)
            self._set_as_current_workspace(workspace)
            return

        warning('\'{0}\' is not a workspace. Cancel...'.format(path), prefix=self.__class__.__name__)
        return

    def open_in_explorer(self):
        data = self.get_selected_data()

        if data is not None:
            workspace = data.get_workspace()
            if workspace is not None:
                os.startfile(workspace.get_path())
            else:
                warning('\'{0}\' cannot be opened because it is invalid (maybe it does not exist anymore). Cancel...'.format(data.get_path()), prefix=self.__class__.__name__)

    def create_workspace(self):
        path = QFileDialog.getExistingDirectory(self, "Create workspace in location")

        if path == '':
            return

        workspace = Workspace.create(path)

        if workspace is not None:
            self._set_as_current_workspace(workspace)
            self.reload()
        else:
            warning('An error occurred while trying to set \'{0}\' as a worskapce (maybe it is already one). Cancel...'.format(path), prefix=self.__class__.__name__)

    def enterEvent(self, *args, **kwargs):
        real_current_workspace = Workspace.get_current()

        if real_current_workspace is not None:
            current_workspace = self.current_workspace_line.text()

            if real_current_workspace.get_path() != current_workspace:
                self.reload()

    def set_and_open(self):
        result = self.set_workspace()

        if result is True:
            mel.eval('OpenScene;')

    def _set_as_current_workspace(self, workspace):
        workspace.set_current()
        info('\'{0}\' has been set as current workspace.'.format(workspace.get_path()), prefix=self.__class__.__name__)
        self.reload()

    def help(self):
        webbrowser.open(self.doc_url)