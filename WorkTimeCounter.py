import win32api
import win32gui
import win32con
import os
import time
import win32evtlog
import datetime
import tkinter as tk
import getpass
import threading
import json

exitFlag = 0
TkinterRunFlag = 1
handel = None
LogonTime = None

class MainThread (threading.Thread):
    def __init__(self, threadID, name, ControlVar):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.ControlVar = ControlVar
    def run(self):
        if self.ControlVar == 2:
            UpdateStatus(self.name)
        if self.ControlVar == 3:
            ShowTimer(self.name)
        if self.ControlVar == 4:
            RefreshLogonTime(self.name)        
        
def UpdateStatus(threadName):
    popup_not_hapened = 1
    while not exitFlag:
        CurrentDateTime = datetime.datetime.now()
        diff = LogonTime - CurrentDateTime
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, \
                         (handel, 0, win32gui.NIF_TIP, win32con.WM_USER+20,\
                          0, CommonResources.GetFormatedTime(int(diff.total_seconds()), 1)))
        if popup_not_hapened and diff.total_seconds() <= 0:
            popup_not_hapened = 0
            messagePopup('It is time to go home.', 'Go home!')
        time.sleep(60)

def RefreshLogonTime(threadName):
    while not exitFlag:
        time.sleep(3600)
        global LogonTime
        LogonTime = CommonResources.GetLoginTime()


def ShowTimer(threadName):
            global TkinterRunFlag
            TkinterRunFlag = 1
            root = tk.Tk()
            time_str = tk.StringVar()
            label_font = ('helvetica', 40)
            tk.Label(root, textvariable=time_str, font=label_font, bg='white', 
            fg='blue', relief='raised', bd=3).pack(fill='x', padx=5, pady=5)
            root.protocol("WM_DELETE_WINDOW", on_closing)
            while TkinterRunFlag:
                CurrentDateTime = datetime.datetime.now()
                diff = LogonTime - CurrentDateTime
                time_str.set(CommonResources.GetFormatedTime(int(diff.total_seconds())))
                root.update()
                time.sleep(1)
            root.destroy()
                
def on_closing():
    global TkinterRunFlag
    TkinterRunFlag = 0

def messagePopup(Message, Title):
    hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
    win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, \
                     (handel, 0, win32gui.NIF_INFO, win32con.WM_USER+20,\
                      0, "Balloon  tooltip",Message,1,Title, win32gui.NIIF_WARNING))
       
class CommonResources:
    def GetFormatedTime(Seconds, time_format = 0):
        m, s = divmod(abs(Seconds), 60)
        h, m = divmod(m, 60)
        if time_format == 0:           
            if Seconds >= 0:
                FormatedTime ='{:d}:{:02d}:{:02d}'.format(h, m, s)
            else:
                FormatedTime ='-{:d}:{:02d}:{:02d}'.format(h, m, s)
        else:
            if Seconds >= -59:
                FormatedTime ='{:d}:{:02d}'.format(h, m)
            else:
                FormatedTime ='-{:d}:{:02d}'.format(h, m)            
        return FormatedTime

    def GetParameters():
        print("")
           
    def GetLoginTime():
        server = 'localhost' # name of the target computer to get event logs
        logtype = 'Security' # Log type
        hand = win32evtlog.OpenEventLog(server,logtype)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ|win32evtlog.EVENTLOG_SEQUENTIAL_READ
        total = win32evtlog.GetNumberOfEventLogRecords(hand)
        CurrentDateTime = datetime.datetime.now()
        CurrentDate = CurrentDateTime.strftime("%Y%m%d")
        StartOfTheDay = datetime.datetime.combine(datetime.date.today(), datetime.time(5, 0, 0))  
        EndOfTheDay = datetime.datetime.combine(datetime.date.today(), datetime.time(23, 0, 0))
        LogonTime = CurrentDateTime + datetime.timedelta(days=1)
        Yesterday = datetime.datetime.combine(datetime.date.today(), datetime.time(23, 59, 59)) - datetime.timedelta(days=1) 
        LoopBreaker = False
        for j in range(0,5000):
            if LoopBreaker:
                break
            events = win32evtlog.ReadEventLog(hand, flags,0)
            if events:
                for event in events:
                    if event.TimeGenerated <= Yesterday:
                        LoopBreaker = True
                    elif (event.TimeGenerated.date() == datetime.date.today() 
                    and event.EventID == 4648
                    and event.SourceName == "Microsoft-Windows-Security-Auditing"
                    and event.StringInserts[8] == "localhost"
                    and event.StringInserts[5] == getpass.getuser()):
                        if event.TimeGenerated > StartOfTheDay and event.TimeGenerated < EndOfTheDay:
                            if event.TimeGenerated < LogonTime:
                                LogonTime = event.TimeGenerated

        if LogonTime > CurrentDateTime:
            LogonTime = None
        else:          
            if datetime.time(7, 30, 0) < LogonTime.time() < datetime.time(8, 0, 0):
                LogonTime = datetime.datetime.combine(datetime.date.today(), datetime.time(8, 0, 0))
            LogonTime += datetime.timedelta(hours=9)
        return LogonTime
    

class WorkTimeCounter:
    def __init__(self):
        message_map = {
                win32con.WM_DESTROY: self.OnDestroy,
                win32con.WM_COMMAND: self.OnCommand,
                win32con.WM_USER+20: self.OnTaskbarNotify
        }
        # Register the Window class.
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "TimeCounter"
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = win32gui.RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow( classAtom, "Taskbar", style, \
                0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT, \
                0, 0, hinst, None)
        win32gui.UpdateWindow(self.hwnd)
        icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
        try:
            shell_dll = os.path.join(win32api.GetSystemDirectory(), "shell32.dll")
            large, small = win32gui.ExtractIconEx(shell_dll, 265, 1)
            hicon = small[0]
            win32gui.DestroyIcon(large[0])
        except:
            hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        flags = win32gui.NIF_ICON | win32gui.NIF_MESSAGE | win32gui.NIF_TIP
        nid = (self.hwnd, 0, flags, win32con.WM_USER+20, hicon, "Starting...")
        win32gui.Shell_NotifyIcon(win32gui.NIM_ADD, nid)
        global handel
        handel = self.hwnd

    def OnDestroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0) # Terminate the app.
        global exitFlag
        exitFlag = 1
        
    def showMessage(self, title, msg):
        hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY, \
                         (self.hwnd, 0, win32gui.NIF_INFO, win32con.WM_USER+20,\
                          0, "Balloon  tooltip",msg,1,title, win32gui.NIIF_NOSOUND))

    def OnTaskbarNotify(self, hwnd, msg, wparam, lparam):
        if lparam==win32con.WM_LBUTTONDBLCLK:
            win32gui.DestroyWindow(self.hwnd)
        elif lparam==win32con.WM_RBUTTONUP:
            menu = win32gui.CreatePopupMenu()
            win32gui.AppendMenu( menu, win32con.MF_STRING, 1024, "Show timer")
            win32gui.AppendMenu( menu, win32con.MF_STRING, 1025, "Exit" )
            pos = win32gui.GetCursorPos()
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
            win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        return 1
    
    def OnCommand(self, hwnd, msg, wparam, lparam):
        id = win32api.LOWORD(wparam)
        if id == 1024:     
            TimerThread3 = MainThread(3, "Timer_Thread2", 3)
            TimerThread3.start()
        elif id == 1025:
            win32gui.DestroyWindow(self.hwnd)
        else:
            print ("Unknown command -", id)
    
if __name__ == '__main__':
    w=WorkTimeCounter()
    global LoginTime
    LogonTime = CommonResources.GetLoginTime()
    TimerThread = MainThread(1, "Timer_Thread", 2)
    TimerThread.start()
    TimerThread4 = MainThread(1, "Timer_Thread4", 4)
    TimerThread4.start()
    win32gui.PumpMessages()
os._exit(1)
