"""
package : 
file : ui.py

description : 
"""

# imports python
import os
import webbrowser

# imports third-parties
import PySide2.QtWidget
import PySide2.QtGui
import PySide2.QtCore
import maya.cmds
import maya.mel

# imports local
import workspace_loader.core.messages
import workspace_loader.core.workspaces
import workspace_loader.core


class Loader(PySide2.QtWidget.QDialog):
    """Docstring here
    """

    star_icon = PySide2.QtWidget.QIcon('{0}/star.png'.format(os.path.dirname(__file__)))
    folder_icon = PySide2.QtWidget.QIcon(':/folder-open.png')
    folder_new_icon = PySide2.QtWidget.QIcon(':/folder-new.png')
    search_icon = PySide2.QtWidget.QIcon(':/search.png')
    help_icon = PySide2.QtWidget.QIcon(':/help.png')
    doc_url = 'https://github.com/Noboxxx/workspace_loader'

    def __init__(self, parent):
        """docstring here

        :param parent: parent under which the loader will be parented
        :type parent: QWidget
        """

        # init
        super(Loader, self).__init__(parent)

        # set parameters
        self.setWindowTitle(self.__class__.__name__)
        self.setMinimumWidth(500)
        self.setMinimumHeight(500)

        if maya.cmds.about(ntOS=True):
            self.setWindowFlags(self.windowFlags() ^ PySide2.QtCore.Qt.WindowContextHelpButtonHint)
        elif maya.cmds.about(macOS=True):
            self.setWindowFlags(PySide2.QtCore.Qt.Tool)

        # current workspace label
        current_workspace_label = PySide2.QtWidget.QLabel(self)
        current_workspace_label.setText('current')

        # current workspace line
        self.current_workspace_line = PySide2.QtWidget.QLineEdit(self)
        self.current_workspace_line.setEnabled(False)

        # current workspace layout
        current_workspace_lay = PySide2.QtWidget.QHBoxLayout()
        current_workspace_lay.addWidget(current_workspace_label)
        current_workspace_lay.addWidget(self.current_workspace_line)

        # current workspace list
        self.workspace_list = PySide2.QtWidget.QListWidget(self)
        self.workspace_list.itemDoubleClicked.connect(self.set_workspace)

        # set button
        set_btn = PySide2.QtWidget.QPushButton(self)
        set_btn.setText('set current')
        set_btn.clicked.connect(self.set_workspace)

        # set and open button
        set_and_open_btn = PySide2.QtWidget.QPushButton(self)
        set_and_open_btn.setLabel('open file')
        set_and_open_btn.clicked.connect(self.set_and_open)

        # open folder button
        open_folder_btn = PySide2.QtWidget.QPushButton(self)
        open_folder_btn.setMaximumWidth(32)
        open_folder_btn.clicked.connect(self.open_workspace)
        open_folder_btn.setIcon(self.folder_icon)

        # favorite button
        favorite_btn = PySide2.QtWidget.QPushButton(self)
        favorite_btn.setIcon(self.star_icon)
        favorite_btn.setMaximumWidth(32)
        favorite_btn.clicked.connect(self.toggle_favorite)

        # create workspace button
        create_workspace_btn = PySide2.QtWidget.QPushButton(self)
        create_workspace_btn.setIcon(self.folder_new_icon)
        create_workspace_btn.setMaximumWidth(32)
        create_workspace_btn.clicked.connect(self.create_workspace)

        # open in explorer button
        open_in_explorer_btn = PySide2.QtWidget.QPushButton(self)
        open_in_explorer_btn.setIcon(self.search_icon)
        open_in_explorer_btn.setMaximumWidth(32)
        open_in_explorer_btn.clicked.connect(self.open_in_explorer)

        # help button
        help_btn = PySide2.QtWidget.QPushButton(self)
        help_btn.setIcon(self.help_icon)
        help_btn.setMaximumWidth(32)
        help_btn.clicked.connect(self.help)

        # button layout
        btn_lay = PySide2.QtWidget.QHBoxLayout()
        btn_lay.addWidget(favorite_btn)
        btn_lay.addWidget(open_folder_btn)
        btn_lay.addWidget(create_workspace_btn)
        btn_lay.addWidget(open_in_explorer_btn)
        btn_lay.addWidget(set_btn)
        btn_lay.addWidget(set_and_open_btn)
        btn_lay.addWidget(help_btn)

        # main layout
        main_lay = PySide2.QtWidget.QVBoxLayout(self)
        main_lay.addLayout(current_workspace_lay)
        main_lay.addWidget(self.workspace_list)
        main_lay.addLayout(btn_lay)

        # reload at initialization
        self.reload()

    @classmethod
    def display(cls):
        """display the loader

        :return: the displayed loader
        :rtype: Loader
        """

        # get the parent
        parent = workspace_loader.core.ui_path_to_widget('MayaWindow', PySide2.QtWidget.QWidget)

        # delete if already existing
        for child in parent.children():
            if type(child).__name__ == cls.__name__:
                child.deleteLater()

        # load instance
        dialog = cls(parent)
        dialog.show()

        # return
        return dialog

    def reload(self):
        """doc string here
        """

        # clear list widget
        self.workspace_list.clear()

        # Display current workspace at the top of the window
        current_workspace = workspace_loader.core.workspaces.Workspace.get_current()
        current_workspace_path = ''
        if isinstance(current_workspace, workspace_loader.core.workspaces.Workspace):
            current_workspace_path = current_workspace.get_path()
        self.current_workspace_line.setText(current_workspace_path)

        # Adding workspaces to the favorite section
        list_item = PySide2.QtWidgets.QListWidgetItem()
        list_item.setText('-- favorites --')
        self.workspace_list.addItem(list_item)

        for favorite in workspace_loader.core.Favorite.get_all():
            list_item = PySide2.QWidget.QListWidgetItem(favorite.get_path())
            list_item.setIcon(self.star_icon)
            list_item.setData(PySide2.QtCore.Qt.UserRole, favorite)
            self.workspace_list.addItem(list_item)
            if not favorite.get_workspace():
                list_item.setForeground(PySide2.QtGui.QBrush(PySide2.QtGui.QColor('gray')))

        list_item = PySide2.QtWidget.QListWidgetItem()
        self.workspace_list.addItem(list_item)

        # Adding workspaces to the recently opened section
        list_item = PySide2.QtWidget.QListWidgetItem()
        list_item.setText('-- recently opened --')
        self.workspace_list.addItem(list_item)

        for recent in workspace_loader.core.Recent.get_all():
            list_item = PySide2.QtWidget.QListWidgetItem(recent.get_path())
            list_item.setData(PySide2.QtCore.Qt.UserRole, recent)
            self.workspace_list.addItem(list_item)
            if not recent.get_workspace():
                list_item.setForeground(PySide2.QtGui.QBrush(PySide2.QtGui.QColor('gray')))

    def get_selected_data(self):
        """doc string here

        :return:
        :rtype:
        """

        # get selected items
        selected_items = self.workspace_list.selectedItems()

        # return
        return selected_items[-1].data(PySide2.QtCore.Qt.UserRole) if selected_items else None

    def set_workspace(self):
        """docstring here

        :return:
        :rtype:
        """

        # get data
        data = self.get_selected_data()

        if data is not None:
            workspace = data.get_workspace()

            if workspace is not None:
                self._set_as_current_workspace(workspace)
                return True
            else:
                maya.cmds.warning('\'{0}\' cannot be set because it is invalid '
                                  '(maybe it does not exist anymore). Cancel...'
                                  .format(data.get_path()), prefix=self.__class__.__name__)
        # return
        return False

    def toggle_favorite(self):
        """docstring here

        :return:
        :rtype:
        """

        # get data
        data = self.get_selected_data()

        if isinstance(data, workspace_loader.core.Favorite):
            data.remove()
            self.reload()
            return
        elif isinstance(data, workspace_loader.core.Recent):
            data.set_as_favorite()
            self.reload()
            return

    def open_workspace(self):
        """docstring here

        :return:
        :rtype:
        """

        # get path
        path = PySide2.QtWidget.QFileDialog.getExistingDirectory(self, "Create workspace in location")

        if path == '' or not workspace_loader.core.workspaces.Workspace.is_one(path):
            maya.cmds.warning('\'{0}\' is not a workspace. Cancel...'.format(path), prefix=self.__class__.__name__)
            return

        # set workspace
        workspace = workspace_loader.core.workspaces.Workspace(path)
        self._set_as_current_workspace(workspace)

    def open_in_explorer(self):
        """docstring here

        :return:
        :rtype:
        """

        # get data
        data = self.get_selected_data()

        # warning
        if data is None:
            maya.cmds.warning('No data specified. Cancel...')
            return

        # get workspace
        workspace = data.get_workspace()

        # warning
        if workspace is None:
            maya.cmds.warning('No workspace specified. Cancel...')
            return

        # startfile
        os.startfile(workspace.get_path())

    def create_workspace(self):
        """doc string here

        :return:
        :rtype:
        """

        # get path
        path = PySide2.QFileDialog.getExistingDirectory(self, "Create workspace in location")

        # return
        if not path:
            return

        # create workspace
        workspace = workspace_loader.core.workspaces.Workspace.create(path)

        # warning
        if workspace is None:
            workspace_loader.core.messages.warning('An error occurred while trying to set \'{0}\' as a workspace '
                                                   '(maybe it is already one). Cancel...'
                                                   .format(path), prefix=self.__class__.__name__)
            return

        # set current namespace
        self._set_as_current_workspace(workspace)

        # reload
        self.reload()

    def enterEvent(self, *args, **kwargs):
        """doc string here

        :param args:
        :type args:
        :param kwargs:
        :type kwargs:
        :return:
        :rtype:
        """

        # get real current workspace
        real_current_workspace = workspace_loader.core.workspaces.Workspace.get_current()

        # return
        if real_current_workspace is None:
            return

        # get current workspace
        current_workspace = self.current_workspace_line.text()

        # reload if necessary
        if not real_current_workspace.get_path() == current_workspace:
            self.reload()

    def set_and_open(self):
        """docstring here

        :return:
        :rtype:
        """

        if self.set_workspace():  # naming is unclear though command should be something like : is_workspace_setted
            maya.mel.eval('OpenScene;')

    def _set_as_current_workspace(self, workspace):
        """doc string here

        :param workspace:
        :type workspace:
        :return:
        :rtype:
        """

        # set current workspace
        workspace.set_current()

        # print
        workspace_loader.core.messages.info('\'{0}\' has been set as current workspace.'
                                            .format(workspace.get_path()), prefix=self.__class__.__name__)

        # reload
        self.reload()

    def help(self):
        """docstring here

        :return:
        :rtype:
        """

        # open web browser
        webbrowser.open(self.doc_url)
