from tkinter import ttk
import tkinter as tk
import Common


class SettingsWidget:
    def __init__(self, master, global_params):
        self.master = master
        self.global_params = global_params

        master.title("Settings")
        self.f1 = ttk.Frame(self.master, style='My.TFrame', padding=(30, 10, 10, 10))  # added padding

        self.f1.pack()

        self.sod_hour_text = tk.IntVar()
        self.sod_minutes_text = tk.IntVar()
        self.len_hour_text = tk.IntVar()
        self.len_minutes_text = tk.IntVar()
        self.min_hour_text = tk.IntVar()
        self.min_minutes_text = tk.IntVar()
        self.max_hour_text = tk.IntVar()
        self.max_minutes_text = tk.IntVar()
        self.info_text = tk.StringVar()

        self.entry_list = []

        self.validate_hour = (master.register(self.on_hour_entry), '%P', 23)
        self.validate_minute = (master.register(self.on_hour_entry), '%P', 59)

        self.main_label = ttk.Label(self.f1, text="Settings", font=("Helvetica", 14))

        self.start_of_day_label = ttk.Label(self.f1, text=" Start of day:")
        self.sod_hour_value = ttk.Entry(self.f1, width=4,textvariable=self.sod_hour_text,
                                        validate="all", validatecommand=self.validate_hour)
        self.entry_list.append(self.sod_hour_value)
        self.colon_label = ttk.Label(self.f1, text=":")
        self.sod_minutes_value = ttk.Entry(self.f1, width=4,textvariable=self.sod_minutes_text,
                                           validate="all", validatecommand=self.validate_minute)
        self.entry_list.append(self.sod_minutes_value)
        self.len_time_label = ttk.Label(self.f1, text="Length of day:")
        self.len_hour_value = ttk.Entry(self.f1, width=4,textvariable=self.len_hour_text,
                                        validate="all", validatecommand=self.validate_hour)
        self.entry_list.append(self.len_hour_value)
        self.colon4_label = ttk.Label(self.f1, text=":")
        self.len_minutes_value = ttk.Entry(self.f1, width=4,textvariable=self.len_minutes_text,
                                           validate="all", validatecommand=self.validate_minute)
        self.entry_list.append(self.len_minutes_value)
        self.min_time_label = ttk.Label(self.f1, text=" Min time:")
        self.min_hour_value = ttk.Entry(self.f1, width=4,textvariable=self.min_hour_text,
                                        validate="all", validatecommand=self.validate_hour)
        self.entry_list.append(self.min_hour_value)
        self.colon2_label = ttk.Label(self.f1, text=":")
        self.min_minutes_value = ttk.Entry(self.f1, width=4,textvariable=self.min_minutes_text,
                                           validate="all", validatecommand=self.validate_minute)
        self.entry_list.append(self.min_minutes_value)
        self.max_time_label = ttk.Label(self.f1, text=" Max time:")
        self.max_hour_value = ttk.Entry(self.f1, width=4,textvariable=self.max_hour_text,
                                        validate="all", validatecommand=self.validate_hour)
        self.entry_list.append(self.max_hour_value)
        self.colon3_label = ttk.Label(self.f1, text=":")
        self.max_minutes_value = ttk.Entry(self.f1, width=4,textvariable=self.max_minutes_text,
                                           validate="all", validatecommand=self.validate_minute)
        self.entry_list.append(self.max_minutes_value)
        self.save_button = ttk.Button(self.f1, text="Save", command=self.save_click)
        self.close_button = ttk.Button(self.f1, text="Close", command=self.close_click)

        self.info_label = ttk.Label(self.f1, textvariable=self.info_text)

        self.main_label.grid(row=0, column=0, columnspan=4, pady=5)

        self.start_of_day_label.grid(row=1, column=0)
        self.sod_hour_value.grid(row=1, column=1)
        self.colon_label.grid(row=1, column=2)
        self.sod_minutes_value.grid(row=1, column=3)

        self.len_time_label.grid(row=2, column=0)
        self.len_hour_value.grid(row=2, column=1)
        self.colon4_label.grid(row=2, column=2)
        self.len_minutes_value.grid(row=2, column=3)

        self.min_time_label.grid(row=3, column=0)
        self.min_hour_value.grid(row=3, column=1)
        self.colon2_label.grid(row=3, column=2)
        self.min_minutes_value.grid(row=3, column=3)

        self.max_time_label.grid(row=4, column=0)
        self.max_hour_value.grid(row=4, column=1)
        self.colon3_label.grid(row=4, column=2)
        self.max_minutes_value.grid(row=4, column=3)

        self.info_label.grid(row=5, column=0, columnspan=4)

        self.save_button.grid(row=6, column=0, columnspan=1, padx=0, pady=15, sticky=tk.E)
        self.close_button.grid(row=6, column=1, columnspan=4, padx=0, pady=15, sticky=tk.W)

        self.sod_hour_text.set(global_params.startHour)
        self.sod_minutes_text.set(global_params.startMinute)
        self.len_hour_text.set(global_params.dayLengthHour)
        self.len_minutes_text.set(global_params.dayLengthMinute)
        self.min_hour_text.set(global_params.minTimeHour)
        self.min_minutes_text.set(global_params.minTimeMinute)
        self.max_hour_text.set(global_params.maxTimeHour)
        self.max_minutes_text.set(global_params.maxTimeMinute)

    def close_click(self):
        self.master.destroy()

    def save_click(self):
        for entry in self.entry_list:
            if not entry.get():
                entry.focus()
                self.info_text.set("Missing value")
                return
        self.save_settings()

    def save_settings(self):
        temp_dict = {"time": {}}
        temp_dict["time"]["startHour"] = self.sod_hour_text.get()
        temp_dict["time"]["startMinute"] = self.sod_minutes_text.get()
        temp_dict["time"]["dayLengthHour"] = self.len_hour_text.get()
        temp_dict["time"]["dayLengthMinute"] = self.len_minutes_text.get()
        temp_dict["time"]["minTimeHour"] = self.min_hour_text.get()
        temp_dict["time"]["minTimeMinute"] = self.min_minutes_text.get()
        temp_dict["time"]["maxTimeHour"] = self.max_hour_text.get()
        temp_dict["time"]["maxTimeMinute"] = self.max_minutes_text.get()
        settings_folder, settings_file = Common.CommonResources.get_settings_file()
        Common.CommonResources.set_global_settings(temp_dict, self.global_params)
        Common.CommonResources.write_to_file(settings_file, temp_dict)
        self.master.destroy()

    def on_hour_entry(self, full_text, number):
        # print(type(number)) somehow it passes string
        if full_text == "":
            return True
        try:
            if int(full_text) <= int(number):
                return True
            else:
                return False
        except ValueError:
            return False
