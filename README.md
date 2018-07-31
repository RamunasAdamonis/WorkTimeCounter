# WorkTimeCounter
Small windows app to read windows security logs and determine time of the day when user first entered his credentials succefully. This is then used to track your working day and notify when to go home.
*****
Note: You have to run this as admin in order for it to work
*****
## Setup

To install following libraries you need to run `pip install pypiwin32` command:
* win32api
* win32gui
* win32con

*****
## Single file executable
To create a single fine executable I am using [pyinstaller](http://www.pyinstaller.org/)
Command: 
```pyinstaller WorkTimeCounter.py -F -w```

`-F`  - Single file
`-w`  - windows (no command line output)




