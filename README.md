# workspace_loader
**Workspace Loader** is a tool made to manipulate workspaces with ease in maya. 

## About
I made this as a practice to create a tool from coding to sharing.
I know it's a basic tool but I really would like to improve it so feel free to ask for improvements and bug fixes!
I would like to make it as close from the maya philosophy about workspaces as possible.

## License
This project and source are released under the MIT License.

## Requirements
Working on Windows and Maya 2019. Nothing else is needed.

## Install
this is more of a tool dev approach than just a td tool. you will have to deal with env variables at some point for more complex tools - to put icons, c++ plugins and more
Put the python folder in the PYTHONPATH, and the icons folder in XBMLANGPATH run this: 
```python
import workspace_loader.ui
workspace_loader.ui.Loader.display()
```
You can of course place the command in a shelf button or in your userSetup file.

## How to use it
![Loader](/window.PNG)

### Current
On top after current is displayed the current workspace.

### List View
In the liste view you have two parts. One for the workspaces tagged as favortie and bellow are placed the recently opened workspaces. The gray workspaces doesn't exist anymore and none of most of the actions bellow won't work on them. Double-clicking on a workspace will set it as current workspace.

### Possible actions
#### favortie
You can tag a workspace as favortie by selecting a workspace and clicking on the star button. If a favortie workspace is selected. It will be removed from the favorite section.

#### open
You can open a workspace by clicking on the open folder button. It will automatically set it as current workspace.

#### create
You can create a new workspace by clicking on the new folder button. You have to choose a folder where the workspace will be set (I recommand to set it in an empty folder). It will automatically be set as current workspace.

#### explorer
You can open in explorer the selected workspace by clicking on the search icon.

#### set current
You can set as current the selected workspace by clicking on the button "set current".

#### open file
By clicking on the "open file" button you will be asked to open a scene in the selected workspace and it will set the workspace as current.

#### help
The help button will redirect you here :)
