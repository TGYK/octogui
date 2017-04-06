Requirements
------
	- python3
	- qt5
	- pyqt5
Installation
------
The requirements can be installed with the following commands:

    - sudo apt-get install python3 qt5
	- sudo apt-get install pyqt5
To install the script, simply copy the main.py, backend.py, and mainwindow_auto.py files into one directory. Create a config containing your access address and API key and place it within the same folder, an example has been provided.

Start with:
	- python3 main.py

Todo
------
	- Handle directories
	- Impliment move operation
	- Impliment mkdir operation
	- Add extruder move sub-menu to control menu
	- Move progress bar to Monitor page
	-Possibly add on-screen keyboard for config page - to not require an ssh login to edit config file/keyboard to type parameters.
	- Add extruder count and heated bed options to config page
	  * Modify print page UI based on config options for extruder count, heated bed
	- Add labels to print page UI
