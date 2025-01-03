Mouse Recorder and Replay Tool

Overview

This tool is a Python application for recording and replaying mouse actions. It allows users to record mouse clicks and movements, save them to a file, load previously saved actions, and replay them multiple times.

Features

Record mouse actions (clicks and movements).

Save recorded actions to a JSON file.

Load actions from a JSON file.

Replay recorded actions multiple times.

Prerequisites

Ensure you have the following installed on your system:

Python 3.12 or later

Required Python packages:

pyautogui

pynput

tkinter

Install the required packages using:

pip install pyautogui pynput

tkinter is included with Python by default.

How to Use

1. Running the Application

Run the tool.py script:

python tool.py

2. Recording Actions

Click the "Bắt Đầu Ghi" button to start recording mouse actions.

Perform mouse actions (clicks/movements) that you want to record.

Click the "Dừng Ghi" button to stop recording.

3. Saving Actions

After recording actions, click "Lưu Hành Động" to save them to a JSON file.

Choose a location and name for the file.

4. Loading Actions

Click "Tải Hành Động" to load previously saved actions from a JSON file.

5. Replaying Actions

Click "Phát Lại Hành Động" to replay loaded actions.

Enter the number of times you want the actions to replay.

Packaging as an Executable

To distribute the application without requiring Python, you can package it as a standalone executable using PyInstaller:

Install PyInstaller:

pip install pyinstaller

Package the application:

pyinstaller --onefile --noconsole tool.py

The executable file will be located in the dist directory.

Known Issues

The replay feature requires precise timing to function correctly.

Ensure screen resolution and mouse settings match the environment where the actions were recorded.

Contributing

If you encounter any bugs or have feature suggestions, feel free to submit an issue or contribute via pull requests.

License

This project is licensed under the MIT License. See the LICENSE file for details.

Author

Developed by Vũ Hoài Nam.

vuhoainam.dev@gmail.com
