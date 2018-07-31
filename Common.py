import os
import datetime
import win32evtlog
import getpass
import json


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
    def get_login_time(global_params):
        dayStart = datetime.time(global_params.startHour, global_params.startMinute)
        minStartTime = datetime.time(global_params.minTimeHour, global_params.minTimeMinute)
        print(minStartTime)
        timeBuffer = (datetime.datetime.combine(datetime.date.today(), minStartTime)
                      - datetime.timedelta(minutes=30)).time()
        server = 'localhost'  # name of the target computer to get event logs
        log_type = 'Security'  # Log type
        hand = win32evtlog.OpenEventLog(server, log_type)
        flags = win32evtlog.EVENTLOG_BACKWARDS_READ | win32evtlog.EVENTLOG_SEQUENTIAL_READ
        current_date_time = datetime.datetime.now()
        start_of_the_day = datetime.datetime.combine(datetime.date.today(), dayStart)
        logon_time = current_date_time + datetime.timedelta(days=1)
        loop_breaker = False
        for j in range(0, 5000):
            if loop_breaker:
                break
            try:
                events = win32evtlog.ReadEventLog(hand, flags, 0)
            except pywintypes.error:
                print("error")  # TODO log the error
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
            if minStartTime is not None:
                if timeBuffer < logon_time.time() < minStartTime:
                    logon_time = datetime.datetime.combine(datetime.date.today(), minStartTime)
            logon_time += datetime.timedelta(hours=global_params.dayLengthHour, minutes=global_params.dayLengthMinute)
        return logon_time

    @staticmethod
    def write_to_file(settings_file, settings_dict):
        print() # TODO delete
        with open(settings_file, 'w') as outfile:
            json.dump(settings_dict, outfile)

    @staticmethod
    def get_settings_file():
        app_data = os.getenv('APPDATA')
        settings_folder = app_data + "\WorkTimeCounter"
        settings_file = settings_folder + "\settings.json"
        return settings_folder, settings_file

    @staticmethod
    def get_setting_dictionary(global_params):
        settings_dict = {"time": {}}
        settings_dict["time"]["startHour"] = global_params.startHour
        settings_dict["time"]["startMinute"] = global_params.startMinute
        settings_dict["time"]["dayLengthHour"] = global_params.dayLengthHour
        settings_dict["time"]["dayLengthMinute"] = global_params.dayLengthMinute
        settings_dict["time"]["minTimeHour"] = global_params.minTimeHour
        settings_dict["time"]["minTimeMinute"] = global_params.minTimeMinute
        settings_dict["time"]["maxTimeHour"] = global_params.maxTimeHour
        settings_dict["time"]["maxTimeMinute"] = global_params.maxTimeMinute
        return settings_dict

    @staticmethod
    def set_global_settings(temp_dict, global_params):
        global_params.startHour = temp_dict["time"]["startHour"]
        global_params.startMinute = temp_dict["time"]["startMinute"]
        global_params.dayLengthHour = temp_dict["time"]["dayLengthHour"]
        global_params.dayLengthMinute = temp_dict["time"]["dayLengthMinute"]
        global_params.minTimeHour = temp_dict["time"]["minTimeHour"]
        global_params.minTimeMinute = temp_dict["time"]["minTimeMinute"]
        global_params.maxTimeHour = temp_dict["time"]["maxTimeHour"]
        global_params.maxTimeMinute = temp_dict["time"]["maxTimeMinute"]
