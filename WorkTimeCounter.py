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
# import json TODO

handel = None
LogonTime = None
ClockRunning = False
LogonRefreshTime = 3600
DayLength = 9
DayStart = datetime.time(5, 0, 0)
TimeBufferStart = datetime.time(7, 30, 0)
TimeBufferEnd = datetime.time(8, 0, 0)


class Timer:
    def __init__(self, master):
        self.master = master
        master.title("t")
        self.time_str = tk.StringVar()
        self.label_font = ('helvetica', 40)
        self.label = tk.Label(self.master, textvariable=self.time_str, font=self.label_font, bg='white',
                              fg='blue', relief='raised', bd=3)
        self.label.pack(fill='x', padx=5, pady=5)

    def update(self, text):
        self.time_str.set(text)


class MainThread (threading.Thread):
    def __init__(self, thread_id):
        threading.Thread.__init__(self)
        self.thread_id = thread_id

    def run(self):
        if self.thread_id == 1:
            update_status()
        if self.thread_id == 2:
            show_timer()
        if self.thread_id == 3:
            refresh_logon_time()


def update_status():
    popup_happened = 0
    while True:
        if LogonTime is not None:     
            current_date_time = datetime.datetime.now()
            diff = LogonTime - current_date_time
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY,
                                      (handel, 0, win32gui.NIF_TIP, win32con.WM_USER+20,
                                       0, CommonResources.get_formatted_time(int(diff.total_seconds()), 1)))
            if not popup_happened and diff.total_seconds() <= 0:
                popup_happened = 1
                message_popup('It is time to go home.', 'Go home!')
            time.sleep(60)
        else:
            win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY,
                                      (handel, 0, win32gui.NIF_TIP, win32con.WM_USER+20,
                                       0, 'Time not found'))
            time.sleep(LogonRefreshTime+120)
            

def refresh_logon_time():
    while True:
        time.sleep(LogonRefreshTime)
        logon_time = CommonResources.get_login_time()
        if logon_time is not None:
            global LogonTime
            LogonTime = logon_time


def show_timer():
    root = tk.Tk()
    timer_gui = Timer(root)
    if LogonTime is not None:
        def callback():
            current_date_time = datetime.datetime.now()
            diff = LogonTime - current_date_time
            timer_gui.update(CommonResources.get_formatted_time(int(diff.total_seconds())))
            root.update()
            root.after(1000, callback)
        root.after(10, callback)
    else:
        timer_gui.update('Time not found')
        root.update()
    root.mainloop()
    global ClockRunning
    ClockRunning = False


def message_popup(message, title):
    # hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
    win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY,
                              (handel, 0, win32gui.NIF_INFO, win32con.WM_USER+20,
                               0, "Balloon  tooltip", message, 1, title, win32gui.NIIF_WARNING))


class CommonResources:
    @staticmethod
    def get_formatted_time(seconds, time_format=0):
        m, s = divmod(abs(seconds), 60)
        h, m = divmod(m, 60)
        if time_format == 0:           
            if seconds >= 0:
                formatted_time = '{:d}:{:02d}:{:02d}'.format(h, m, s)
            else:
                formatted_time = '-{:d}:{:02d}:{:02d}'.format(h, m, s)
        else:
            if seconds >= -59:
                formatted_time = '{:d}:{:02d}'.format(h, m)
            else:
                formatted_time = '-{:d}:{:02d}'.format(h, m)
        return formatted_time

    @staticmethod
    def get_login_time():
        server = 'localhost'  # name of the target computer to get event logs
        log_type = 'Security'  # Log type
        hand = win32evtlog.OpenEventLog(server, log_type)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        current_date_time = datetime.datetime.now()
        start_of_the_day = datetime.datetime.combine(datetime.date.today(), DayStart)
        logon_time = current_date_time + datetime.timedelta(days=1)
        loop_breaker = False
        for j in range(0, 5000):
            if loop_breaker:
                break
            events = win32evtlog.ReadEventLog(hand, flags, 0)
            if events:
                for event in events:
                    if event.TimeGenerated < start_of_the_day:
                        loop_breaker = True
                    elif (event.EventID == 4648
                          and event.SourceName == "Microsoft-Windows-Security-Auditing"
                          and event.StringInserts[8] == "localhost"
                          and event.StringInserts[5] == getpass.getuser()):
                        if event.TimeGenerated < logon_time:
                            logon_time = event.TimeGenerated
        if logon_time > current_date_time:
            logon_time = None
        else:
            if TimeBufferStart is not None:
                if TimeBufferStart < logon_time.time() < TimeBufferEnd:
                    logon_time = datetime.datetime.combine(datetime.date.today(), TimeBufferEnd)
                logon_time += datetime.timedelta(hours=DayLength)
        return logon_time
    

class WorkTimeCounter:
    def __init__(self):
        message_map = {
                win32con.WM_DESTROY: self.on_destroy,
                win32con.WM_COMMAND: self.on_command,
                win32con.WM_USER+20: self.on_taskbar_notify
        }
        # Register the Window class.
        wc = win32gui.WNDCLASS()
        hinst = wc.hInstance = win32api.GetModuleHandle(None)
        wc.lpszClassName = "TimeCounter"
        wc.lpfnWndProc = message_map # could also specify a wndproc.
        classAtom = win32gui.RegisterClass(wc)
        # Create the Window.
        style = win32con.WS_OVERLAPPED | win32con.WS_SYSMENU
        self.hwnd = win32gui.CreateWindow(classAtom, "Taskbar", style,
                                          0, 0, win32con.CW_USEDEFAULT, win32con.CW_USEDEFAULT,
                                          0, 0, hinst, None)
        win32gui.UpdateWindow(self.hwnd)
        # icon_flags = win32con.LR_LOADFROMFILE | win32con.LR_DEFAULTSIZE
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

    def on_destroy(self, hwnd, msg, wparam, lparam):
        nid = (self.hwnd, 0)
        win32gui.Shell_NotifyIcon(win32gui.NIM_DELETE, nid)
        win32gui.PostQuitMessage(0)  # Terminate the app.
        global exitFlag
        exitFlag = 1
        
    def show_message(self, title, msg):
        # hicon = win32gui.LoadIcon(0, win32con.IDI_APPLICATION)
        win32gui.Shell_NotifyIcon(win32gui.NIM_MODIFY,
                                  (self.hwnd, 0, win32gui.NIF_INFO, win32con.WM_USER+20,
                                   0, "Balloon  tooltip", msg, 1, title, win32gui.NIIF_NOSOUND))

    def on_taskbar_notify(self, hwnd, msg, wparam, lparam):
        if lparam == win32con.WM_LBUTTONDBLCLK:
            win32gui.DestroyWindow(self.hwnd)
        elif lparam == win32con.WM_RBUTTONUP:
            menu = win32gui.CreatePopupMenu()
            win32gui.AppendMenu(menu, win32con.MF_STRING, 1024, "Show timer")
            win32gui.AppendMenu(menu, win32con.MF_STRING, 1025, "Exit")
            pos = win32gui.GetCursorPos()
            win32gui.SetForegroundWindow(self.hwnd)
            win32gui.TrackPopupMenu(menu, win32con.TPM_LEFTALIGN, pos[0], pos[1], 0, self.hwnd, None)
            win32gui.PostMessage(self.hwnd, win32con.WM_NULL, 0, 0)
        return 1
    
    def on_command(self, hwnd, msg, wparam, lparam):
        command_id = win32api.LOWORD(wparam)
        if command_id == 1024:
            global ClockRunning
            if not ClockRunning:  # tkinter is not thread safe.
                timer_thread2 = MainThread(2)
                timer_thread2.start()
                ClockRunning = True
        elif command_id == 1025:
            win32gui.DestroyWindow(self.hwnd)
        else:
            print("Unknown command -", command_id)


if __name__ == '__main__':
    w = WorkTimeCounter()
    LogonTime = CommonResources.get_login_time()
    timer_thread = MainThread(1)
    timer_thread.start()
    timer_thread3 = MainThread(3)
    timer_thread3.start()
    win32gui.PumpMessages()
os._exit(1)

