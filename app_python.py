import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
import time
from datetime import datetime
import ctypes
from ctypes import *
from ctypes import CDLL, c_int

#import random
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from collections import deque
import json
import os
from tkinter import filedialog


class ADC_Monitor_App:
    def __init__(self, root,lib,handle):
        self.root = root
        self.lib = lib
        self.handle = handle
        
        self.root = root
        self.root.title("Monitor ADC Application ADS1256")
        self.root.geometry("1388x768")
        
        
        
        # Biến lưu trữ dữ liệu ADC
        self.adc_data = (ctypes.c_double * 8)()
        self.initialize_adc_data()
        
        # Dictionary lưu trữ tên kênh và đơn vị tùy chỉnh
        self.custom_channel_names = {}
        self.custom_units = {}
        self.conversion_formulas = {}
        
        # Hệ thống cảnh báo
        self.warning_thresholds = {}
        self.warning_counts = {}
        self.warning_log_file = "warning_log.txt"
        
        # Biến trạng thái kênh
        self.status_vars = {}
        self.default_channels = ["AIN0", "AIN1", "AIN2", "AIN3", "AIN4", "AIN5", "AIN6", "AIN7"]
        for channel in self.default_channels:
            self.status_vars[channel] = tk.BooleanVar(value=True)
        
        # Khởi tạo giá trị mặc định cho cảnh báo
        self.initialize_warning_system()
        
        # Biến cho đồ thị
        self.graph_enabled_channels = {}  # Dictionary lưu trạng thái hiển thị của từng kênh
        self.graph_data = {}  # Dictionary lưu dữ liệu lịch sử của từng kênh
        self.max_data_points = 100  # Số điểm dữ liệu tối đa hiển thị
        self.time_data = deque(maxlen=self.max_data_points)  # Dữ liệu thời gian
        
        # Khởi tạo dữ liệu đồ thị cho từng kênh
        for channel in self.default_channels:
            self.graph_enabled_channels[channel] = tk.BooleanVar(value=False)  # Mặc định không hiển thị
            self.graph_data[channel] = deque(maxlen=self.max_data_points)
        
        # Bật mặc định kênh AIN0
        self.graph_enabled_channels["AIN0"].set(True)
        
        # Màu sắc cho từng kênh
        self.channel_colors = {
            "AIN0": "#FF0000",  # Đỏ
            "AIN1": "#00FF00",  # Xanh lá
            "AIN2": "#0000FF",  # Xanh dương
            "AIN3": "#FF00FF",  # Tím
            "AIN4": "#FFFF00",  # Vàng
            "AIN5": "#00FFFF",  # Cyan
            "AIN6": "#FFA500",  # Cam
            "AIN7": "#800080",  # Tím đậm
        }
        
        # Tạo menu bar
        self.create_menu_bar()
        
        # Tạo các frame chính
        self.create_header()
        self.create_channel_table()
        self.create_warning_section()
        self.create_graph_section()
        
        # Cập nhật thời gian thực và dữ liệu ADC
        self.update_time()
        self.update_adc_values()
    
    def initialize_warning_system(self):
        """Khởi tạo hệ thống cảnh báo với giá trị mặc định"""
        for channel in self.default_channels:
            self.warning_thresholds[channel] = 4.0
            self.warning_counts[channel] = 0
    
    def create_menu_bar(self):
        """Tạo menu bar với menu File và Setting"""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        # Menu File
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        #file_menu.add_command(label="New")
        #file_menu.add_command(label="Open")
        #file_menu.add_command(label="Save")
        file_menu.add_command(label="Reset", command=self.reset_app)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Menu Setting
        setting_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Setting", menu=setting_menu)
        setting_menu.add_command(label="Channel Settings", command=self.open_channel_settings)
        setting_menu.add_command(label="Conversion Formulas", command=self.open_conversion_settings)
        setting_menu.add_command(label="Warning Settings", command=self.open_warning_settings)
        setting_menu.add_command(label="Channel Status", command=self.open_channel_status_settings)
        setting_menu.add_separator()
        setting_menu.add_command(label="Save Configuration", command=self.save_configuration)
        setting_menu.add_command(label="Load Configuration", command=self.load_configuration)
    
    def open_channel_status_settings(self):
        """Mở cửa sổ cài đặt trạng thái kênh"""
        status_window = tk.Toplevel(self.root)
        status_window.title("Channel Status Settings")
        status_window.geometry("400x400")
        status_window.transient(self.root)
        status_window.grab_set()
        
        ttk.Label(status_window, 
                 text="Channel Status Settings - Turn channels ON/OFF",
                 font=("Arial", 11, "bold")).pack(pady=10)
        
        main_frame = ttk.Frame(status_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        self.status_indicators = {}
        self.status_labels = {}
        
        for channel in self.default_channels:
            channel_frame = ttk.Frame(main_frame)
            channel_frame.pack(fill='x', pady=5)
            
            indicator = tk.Canvas(channel_frame, width=20, height=20, highlightthickness=0)
            indicator.pack(side='left', padx=(0, 10))
            circle = indicator.create_oval(2, 2, 18, 18, fill='green', outline='darkgreen')
            self.status_indicators[channel] = (indicator, circle)
            
            display_name = self.custom_channel_names.get(channel, channel)
            label = ttk.Label(channel_frame, text=display_name, width=15)
            label.pack(side='left', padx=(0, 10))
            self.status_labels[channel] = label
            
            btn = ttk.Button(channel_frame, text="ON/OFF", width=8,
                           command=lambda ch=channel: self.toggle_channel_status(ch))
            btn.pack(side='left')
            
            self.update_channel_indicator(channel)
        
        help_frame = ttk.Frame(status_window)
        help_frame.pack(fill='x', padx=10, pady=10)
        ttk.Label(help_frame, 
                 text="• Green indicator: Channel is ON (active)\n"
                      "• Red indicator: Channel is OFF (inactive)\n"
                      "• Click ON/OFF to toggle channel status",
                 justify=tk.LEFT).pack(anchor='w')
        
        button_frame = ttk.Frame(status_window)
        button_frame.pack(fill='x', padx=10, pady=10)
        ttk.Button(button_frame, text="Close", command=status_window.destroy).pack(side='right')
    
    def toggle_channel_status(self, channel):
        """Chuyển đổi trạng thái kênh ON/OFF"""
        current_state = self.status_vars[channel].get()
        self.status_vars[channel].set(not current_state)
        self.update_channel_indicator(channel)
    
    def update_channel_indicator(self, channel):
        """Cập nhật màu indicator cho kênh"""
        if channel in self.status_indicators:
            indicator, circle = self.status_indicators[channel]
            is_on = self.status_vars[channel].get()
            color = 'green' if is_on else 'red'
            outline_color = 'darkgreen' if is_on else 'darkred'
            indicator.itemconfig(circle, fill=color, outline=outline_color)
    
    def open_warning_settings(self):
        """Mở cửa sổ cài đặt cảnh báo"""
        warning_window = tk.Toplevel(self.root)
        warning_window.title("Warning Settings")
        warning_window.geometry("500x500")
        warning_window.transient(self.root)
        warning_window.grab_set()
        
        ttk.Label(warning_window, 
                 text="Set warning thresholds for each channel",
                 font=("Arial", 11, "bold")).pack(pady=10)
        
        main_frame = ttk.Frame(warning_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=5)
        ttk.Label(header_frame, text="Channel", width=15).pack(side='left')
        ttk.Label(header_frame, text="Warning Threshold", width=20).pack(side='left', padx=5)
        ttk.Label(header_frame, text="Current Count", width=15).pack(side='left')
        ttk.Label(header_frame, text="Reset", width=10).pack(side='left')
        
        self.threshold_entries = {}
        
        for channel in self.default_channels:
            row_frame = ttk.Frame(main_frame)
            row_frame.pack(fill='x', pady=2)
            
            display_name = self.custom_channel_names.get(channel, channel)
            ttk.Label(row_frame, text=display_name, width=15).pack(side='left')
            
            threshold_var = tk.StringVar(value=str(self.warning_thresholds[channel]))
            entry = ttk.Entry(row_frame, width=20, textvariable=threshold_var)
            entry.pack(side='left', padx=5)
            self.threshold_entries[channel] = threshold_var
            
            count_label = ttk.Label(row_frame, text=str(self.warning_counts[channel]), width=15)
            count_label.pack(side='left')
            
            reset_btn = ttk.Button(row_frame, text="Reset", 
                                  command=lambda ch=channel, lbl=count_label: self.reset_warning_count(ch, lbl))
            reset_btn.pack(side='left', padx=5)
        
        help_frame = ttk.Frame(warning_window)
        help_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(help_frame, 
                 text="Note: Warning will be triggered when channel value exceeds the threshold.\n"
                      "Warning will be logged to file and displayed in Notification panel.",
                 justify=tk.LEFT).pack(anchor='w')
        
        button_frame = ttk.Frame(warning_window)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Apply", command=lambda: self.apply_warning_settings(warning_window)).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=warning_window.destroy).pack(side='right', padx=5)
    
    def reset_warning_count(self, channel, count_label):
        """Reset số lần cảnh báo cho kênh cụ thể"""
        self.warning_counts[channel] = 0
        count_label.config(text="0")
        self.update_warning_display()
    
    def apply_warning_settings(self, window):
        """Áp dụng cài đặt cảnh báo"""
        for channel, var in self.threshold_entries.items():
            try:
                threshold = float(var.get())
                self.warning_thresholds[channel] = threshold
            except ValueError:
                messagebox.showerror("Error", f"Invalid threshold value for {channel}")
                return
        
        window.destroy()
    
    def check_warnings(self, channel, value):
        """Kiểm tra và xử lý cảnh báo cho kênh"""
        threshold = self.warning_thresholds.get(channel, 4.0)
        
        if abs(value) > threshold:
            self.warning_counts[channel] = self.warning_counts.get(channel, 0) + 1
            self.log_warning(channel, value, threshold)
            self.add_notification(channel, value, threshold)
            self.update_warning_display()
            return True
        return False
    
    def add_notification(self, channel, value, threshold):
        """Thêm thông báo cảnh báo vào khung Notification"""
        if hasattr(self, 'notification_text'):
            timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            display_name = self.custom_channel_names.get(channel, channel)
            unit = self.custom_units.get(channel, "V")
            
            notification = f"{timestamp}: {display_name} has reach warning value {threshold} {unit}"
            
            current_text = self.notification_text.get("1.0", tk.END).strip()
            
            if current_text:
                lines = current_text.split('\n')
                if len(lines) >= 10:
                    lines = lines[:9]
                new_text = notification + '\n' + '\n'.join(lines)
            else:
                new_text = notification
            
            self.notification_text.configure(state=tk.NORMAL)
            self.notification_text.delete("1.0", tk.END)
            self.notification_text.insert("1.0", new_text)
            
            self.notification_text.tag_add("warning", "1.0", "1.end")
            self.notification_text.tag_config("warning", foreground="red")
            self.notification_text.configure(state=tk.DISABLED)
    
    def reset_app(self):
        """Reset toàn bộ dữ liệu đồ thị và bảng hiển thị"""
        # Xóa dữ liệu cũ
        for channel in self.default_channels:
            self.graph_data[channel].clear()
            self.warning_counts[channel] = 0
            self.tree.item(self.channel_items[channel], values=(channel, "0.000 V", "V"))
        
        # Reset thời gian và cảnh báo
        self.time_data.clear()
        self.update_warning_display()

        # Xóa nội dung khung Notification
        if hasattr(self, 'notification_text'):
            self.notification_text.configure(state=tk.NORMAL)
            self.notification_text.delete("1.0", tk.END)
            self.notification_text.configure(state=tk.DISABLED)

        # Làm mới lại đồ thị
        self.update_graph()


    def log_warning(self, channel, value, threshold):
        """Ghi log cảnh báo vào file"""
        try:
            with open(self.warning_log_file, "a", encoding="utf-8") as f:
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                display_name = self.custom_channel_names.get(channel, channel)
                unit = self.custom_units.get(channel, "V")
                f.write(
                    f"[{timestamp}] {display_name} - "
                    f"Value: {value:.3f} {unit}, "
                    f"Threshold: {threshold} {unit}, "
                    f"Count: {self.warning_counts[channel]}\n"
                )
        except Exception as e:
            print(f"Error writing warning log: {e}")
    
    def update_warning_display(self):
        """Cập nhật hiển thị số lần cảnh báo"""
        total_warnings = sum(self.warning_counts.values())
        if hasattr(self, 'total_warning_label'):
            self.total_warning_label.config(text=f"Number of times reach warning value: {total_warnings}")
    
    def open_channel_settings(self):
        """Mở cửa sổ cài đặt kênh"""
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Channel Settings")
        settings_window.geometry("400x500")
        settings_window.transient(self.root)
        settings_window.grab_set()
        
        notebook = ttk.Notebook(settings_window)
        notebook.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Tab Channel Names
        channel_frame = ttk.Frame(notebook)
        notebook.add(channel_frame, text="Channel Names")
        
        ttk.Label(channel_frame, text="Custom Channel Names", font=("Arial", 10, "bold")).pack(pady=10)
        
        entries_frame = ttk.Frame(channel_frame)
        entries_frame.pack(fill='both', expand=True, padx=10)
        
        self.name_entries = {}
        
        for i, channel in enumerate(self.default_channels):
            row_frame = ttk.Frame(entries_frame)
            row_frame.pack(fill='x', pady=2)
            
            ttk.Label(row_frame, text=f"{channel}:").pack(side='left', padx=5)
            entry = ttk.Entry(row_frame, width=20)
            entry.pack(side='left', padx=5, fill='x', expand=True)
            entry.insert(0, self.custom_channel_names.get(channel, channel))
            self.name_entries[channel] = entry
        
        # Tab Units
        unit_frame = ttk.Frame(notebook)
        notebook.add(unit_frame, text="Units")
        
        ttk.Label(unit_frame, text="Custom Units", font=("Arial", 10, "bold")).pack(pady=10)
        
        unit_entries_frame = ttk.Frame(unit_frame)
        unit_entries_frame.pack(fill='both', expand=True, padx=10)
        
        self.unit_entries = {}
        
        for i, channel in enumerate(self.default_channels):
            row_frame = ttk.Frame(unit_entries_frame)
            row_frame.pack(fill='x', pady=2)
            
            display_name = self.custom_channel_names.get(channel, channel)
            ttk.Label(row_frame, text=f"{display_name}:").pack(side='left', padx=5)
            entry = ttk.Entry(row_frame, width=15)
            entry.pack(side='left', padx=5, fill='x', expand=True)
            entry.insert(0, self.custom_units.get(channel, "V"))
            self.unit_entries[channel] = entry
        
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Apply", command=lambda: self.apply_channel_settings(settings_window)).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=settings_window.destroy).pack(side='right', padx=5)
    
    def open_conversion_settings(self):
        """Mở cửa sổ cài đặt công thức chuyển đổi"""
        conv_window = tk.Toplevel(self.root)
        conv_window.title("Conversion Formulas")
        conv_window.geometry("500x450")
        conv_window.transient(self.root)
        conv_window.grab_set()
        
        ttk.Label(conv_window, 
                 text="Set conversion formulas (use 'x' for voltage value)\nExample: x * 10 + 25 for temperature conversion",
                 justify=tk.CENTER).pack(pady=10)
        
        main_frame = ttk.Frame(conv_window)
        main_frame.pack(fill='both', expand=True, padx=10, pady=5)
        
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill='x', pady=5)
        ttk.Label(header_frame, text="Channel", width=15).pack(side='left')
        ttk.Label(header_frame, text="Formula", width=30).pack(side='left', padx=5)
        ttk.Label(header_frame, text="Example", width=20).pack(side='left')
        
        self.formula_entries = {}
        
        for channel in self.default_channels:
            row_frame = ttk.Frame(main_frame)
            row_frame.pack(fill='x', pady=2)
            
            display_name = self.custom_channel_names.get(channel, channel)
            ttk.Label(row_frame, text=display_name, width=15).pack(side='left')
            
            entry = ttk.Entry(row_frame, width=30)
            entry.pack(side='left', padx=5)
            entry.insert(0, self.conversion_formulas.get(channel, "x"))
            self.formula_entries[channel] = entry
            
            example_text = "x * 10 + 25" if channel == "AIN0" else "x"
            ttk.Label(row_frame, text=example_text, width=20).pack(side='left')
        
        help_frame = ttk.Frame(conv_window)
        help_frame.pack(fill='x', padx=10, pady=5)
        ttk.Label(help_frame, 
                 text="Formula examples:\n"
                      "Temperature: x * 10 + 25\n"
                      "Pressure: x * 100 + 1000\n"
                      "Leave as 'x' to keep voltage value",
                 justify=tk.LEFT).pack(anchor='w')
        
        button_frame = ttk.Frame(conv_window)
        button_frame.pack(fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Apply", command=lambda: self.apply_conversion_settings(conv_window)).pack(side='right', padx=5)
        ttk.Button(button_frame, text="Cancel", command=conv_window.destroy).pack(side='right', padx=5)
    
    def apply_channel_settings(self, window):
        """Áp dụng cài đặt kênh từ cửa sổ settings"""
        for channel, entry in self.name_entries.items():
            new_name = entry.get().strip()
            if new_name:
                self.custom_channel_names[channel] = new_name
        
        for channel, entry in self.unit_entries.items():
            new_unit = entry.get().strip()
            if new_unit:
                self.custom_units[channel] = new_unit
        
        self.update_channel_display()
        window.destroy()
    
    def apply_conversion_settings(self, window):
        """Áp dụng cài đặt công thức chuyển đổi"""
        for channel, entry in self.formula_entries.items():
            formula = entry.get().strip()
            if formula:
                self.conversion_formulas[channel] = formula
        
        window.destroy()
    
    def update_channel_display(self):
        """Cập nhật hiển thị tất cả các kênh với tên và đơn vị mới"""
        for channel, item in self.channel_items.items():
            display_name = self.custom_channel_names.get(channel, channel)
            unit = self.custom_units.get(channel, "V")
            
            current_values = list(self.tree.item(item, "values"))
            current_values[0] = display_name
            current_values[2] = unit
            self.tree.item(item, values=current_values)
    
    def initialize_adc_data(self):
        """Khởi tạo dữ liệu ADC ban đầu"""
        for i in range(8):
            self.adc_data[i] = 0.0
    
    def read_adc_data(self):
        self.lib.Select_CE0(0)
        self.lib.Get_all(self.handle,self.adc_data)
        self.lib.Select_CE0(1)
        return self.adc_data
    
    def create_header(self):
        """Tạo phần header với thông tin ứng dụng và thời gian"""
        header_frame = ttk.Frame(self.root, padding="10")
        header_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E))
        
        title_label = ttk.Label(header_frame, 
                               text="Monitor ADC Application ADS1256",
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        author_label = ttk.Label(header_frame,
                                text="made by Phan Thanh Thao - HCMUTE",
                                font=("Arial", 10))
        author_label.grid(row=1, column=0, sticky=tk.W)
        
        time_frame = ttk.Frame(header_frame)
        time_frame.grid(row=0, column=1, rowspan=2, sticky=tk.E)
        
        self.time_label = ttk.Label(time_frame, 
                                   font=("Arial", 12, "bold"),
                                   foreground="blue")
        self.time_label.grid(row=0, column=0, sticky=tk.E)
        
        self.date_label = ttk.Label(time_frame,
                                   font=("Arial", 10),
                                   foreground="darkblue")
        self.date_label.grid(row=1, column=0, sticky=tk.E)
        
        header_frame.columnconfigure(1, weight=1)
    
    def create_channel_table(self):
        """Tạo bảng hiển thị các kênh AIN0-AIN7"""
        table_frame = ttk.LabelFrame(self.root, text="Channel Values", padding="10")
        table_frame.grid(row=1, column=0, padx=(10,5), pady=5, sticky=(tk.W,tk.N,tk.S,tk.E))
        
        columns = ("Channel", "Value", "Unit")
        self.tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)
        
        self.tree.heading("Channel", text="Channel")
        self.tree.heading("Value", text="Value")
        self.tree.heading("Unit", text="Unit")
        
        self.tree.column("Channel", width=100,anchor="center")
        self.tree.column("Value", width=150,anchor="center")
        self.tree.column("Unit", width=100,anchor="center")
        
        self.channel_items = {}
        
        for i, channel in enumerate(self.default_channels):
            display_name = self.custom_channel_names.get(channel, channel)
            item = self.tree.insert("", "end", values=(display_name, "0.000 V", "V"))
            self.channel_items[channel] = item
        
        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E,tk.S,tk.N))
        
        scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        self.tree.configure(yscrollcommand=scrollbar.set)
        table_frame.rowconfigure(0, weight=1)
        table_frame.columnconfigure(0, weight=1)
    
    def create_warning_section(self):
        """Tạo phần cảnh báo"""
        warning_frame = ttk.LabelFrame(self.root, text="Warning & Status", padding="10")
        warning_frame.grid(row=1, column=1, padx=(5, 10), pady=5, sticky=(tk.N,tk.W,tk.S,tk.E))

        notification_frame = ttk.LabelFrame(warning_frame, text="Notification")
        notification_frame.grid(row=0, column=0, sticky=(tk.W, tk.E,tk.S,tk.N), pady=(0, 5))
        notification_frame.rowconfigure(0, weight=1)
        notification_frame.columnconfigure(0, weight=1)

        self.notification_text = tk.Text(notification_frame, height=10, width=60, wrap=tk.WORD, 
                                         font=("Arial", 9), state=tk.DISABLED)
        self.notification_text.grid(row=0, column=0, sticky=(tk.W, tk.E,tk.S,tk.N))
        
        notif_scrollbar = ttk.Scrollbar(notification_frame, orient="vertical", 
                                        command=self.notification_text.yview)
        notif_scrollbar.grid(row=0, column=1, sticky=(tk.W, tk.E,tk.S,tk.N))
        self.notification_text.configure(yscrollcommand=notif_scrollbar.set)
        
        count_frame = ttk.Frame(warning_frame)
        count_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=5)
        
        self.total_warning_label = ttk.Label(count_frame, 
                                           text="Number of times reach warning value: 0", 
                                           font=("Arial", 10, "bold"))
        self.total_warning_label.pack(anchor='w')
        
        warning_frame.rowconfigure(0, weight=1)
        warning_frame.rowconfigure(1, weight=0)
        warning_frame.columnconfigure(0, weight=1)
    
    def create_graph_section(self):
        """Tạo phần đồ thị với các nút chọn kênh"""
        graph_frame = ttk.LabelFrame(self.root, 
                                   text="Graph of value of each channel over time", 
                                   padding="10")
        graph_frame.grid(row=2, column=0, columnspan=2, padx=10, pady=5, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Frame chứa các nút chọn kênh
        control_frame = ttk.Frame(graph_frame)
        control_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        ttk.Label(control_frame, text="Select channels to display:", 
                 font=("Arial", 10, "bold")).pack(side='left', padx=(0, 10))
        
        # Tạo các checkbox cho từng kênh
        self.channel_checkboxes = {}
        for i, channel in enumerate(self.default_channels):
            display_name = self.custom_channel_names.get(channel, channel)
            
            # Frame cho mỗi checkbox với màu indicator
            cb_frame = ttk.Frame(control_frame)
            cb_frame.pack(side='left', padx=5)
            
            # Canvas để hiển thị màu của kênh
            color_indicator = tk.Canvas(cb_frame, width=15, height=15, highlightthickness=0)
            color_indicator.pack(side='left', padx=(0, 3))
            color_indicator.create_rectangle(0, 0, 15, 15, fill=self.channel_colors[channel], outline='black')
            
            # Checkbox
            cb = ttk.Checkbutton(cb_frame, text=display_name, 
                               variable=self.graph_enabled_channels[channel],
                               command=self.update_graph)
            cb.pack(side='left')
            self.channel_checkboxes[channel] = cb
        
        # Nút Clear All và Select All
        button_frame = ttk.Frame(control_frame)
        button_frame.pack(side='right', padx=10)
        
        ttk.Button(button_frame, text="Clear All", 
                  command=self.clear_all_channels, width=10).pack(side='left', padx=2)
        ttk.Button(button_frame, text="Select All", 
                  command=self.select_all_channels, width=10).pack(side='left', padx=2)
        
        # Frame chứa đồ thị
        plot_frame = ttk.Frame(graph_frame)
        plot_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Tạo figure và axes cho matplotlib
        self.fig = Figure(figsize=(10, 3), dpi=100)
        self.ax = self.fig.add_subplot(111)
        
        # Tạo canvas để hiển thị đồ thị
        self.canvas = FigureCanvasTkAgg(self.fig, master=plot_frame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        # Cấu hình đồ thị ban đầu
        self.ax.set_xlabel('Time (samples)', fontsize=10)
        self.ax.set_ylabel('Value', fontsize=10)
        self.ax.set_title('Channel Values Over Time', fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        self.ax.legend(loc='upper right')
        
        # Cấu hình grid weights
        graph_frame.rowconfigure(1, weight=1)
        graph_frame.columnconfigure(0, weight=1)
    
    def clear_all_channels(self):
        """Bỏ chọn tất cả các kênh"""
        for channel in self.default_channels:
            self.graph_enabled_channels[channel].set(False)
        self.update_graph()
    
    def select_all_channels(self):
        """Chọn tất cả các kênh"""
        for channel in self.default_channels:
            self.graph_enabled_channels[channel].set(True)
        self.update_graph()
    
    def update_graph(self):
        """Cập nhật đồ thị với các kênh được chọn"""
        self.ax.clear()
        
        # Vẽ lại lưới và nhãn
        self.ax.set_xlabel('Time (samples)', fontsize=10)
        self.ax.set_ylabel('Value', fontsize=10)
        self.ax.set_title('Channel Values Over Time', fontsize=12, fontweight='bold')
        self.ax.grid(True, alpha=0.3)
        
        # Vẽ các kênh được chọn
        legend_items = []
        for channel in self.default_channels:
            if self.graph_enabled_channels[channel].get() and len(self.graph_data[channel]) > 0:
                display_name = self.custom_channel_names.get(channel, channel)
                unit = self.custom_units.get(channel, "V")
                
                # Vẽ đường cho kênh này
                line, = self.ax.plot(list(self.graph_data[channel]), 
                                    color=self.channel_colors[channel],
                                    linewidth=2,
                                    label=f"{display_name} ({unit})",
                                    marker='o' if len(self.graph_data[channel]) < 20 else None,
                                    markersize=4)
                legend_items.append(line)
        
        # Hiển thị legend nếu có kênh được chọn
        if legend_items:
            self.ax.legend(loc='upper right', fontsize=9)
        else:
            # Hiển thị thông báo nếu không có kênh nào được chọn
            self.ax.text(0.5, 0.5, 'No channel selected\nSelect channels above to display', 
                        ha='center', va='center', transform=self.ax.transAxes,
                        fontsize=12, color='gray')
        
        self.canvas.draw()
    
    def update_time(self):
        """Cập nhật thời gian và ngày tháng thực tế"""
        current_time = time.strftime("%H:%M:%S")
        current_date = datetime.now().strftime("%d/%m/%Y")
        
        self.time_label.config(text=current_time)
        self.date_label.config(text=current_date)
        
        self.root.after(1000, self.update_time)
    


    def save_configuration(self):
        """Lưu toàn bộ cấu hình vào file JSON"""
        try:
            # Mở dialog để chọn nơi lưu file
            file_path = filedialog.asksaveasfilename(
                defaultextension=".json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Save Configuration",
                initialfile="adc_config.json"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Tạo dictionary chứa toàn bộ cấu hình
            config = {
                "custom_channel_names": self.custom_channel_names,
                "custom_units": self.custom_units,
                "conversion_formulas": self.conversion_formulas,
                "warning_thresholds": self.warning_thresholds,
                "channel_status": {channel: var.get() for channel, var in self.status_vars.items()},
                "graph_enabled_channels": {channel: var.get() for channel, var in self.graph_enabled_channels.items()}
            }
            
            # Lưu vào file JSON
            with open(file_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=4, ensure_ascii=False)
            
            messagebox.showinfo("Success", f"Configuration saved successfully to:\n{file_path}")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save configuration:\n{str(e)}")

    def load_configuration(self):
        """Load cấu hình từ file JSON"""
        try:
            # Mở dialog để chọn file
            file_path = filedialog.askopenfilename(
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
                title="Load Configuration"
            )
            
            if not file_path:
                return  # User cancelled
            
            # Kiểm tra file tồn tại
            if not os.path.exists(file_path):
                messagebox.showerror("Error", "Configuration file not found!")
                return
            
            # Đọc file JSON
            with open(file_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # Load custom channel names
            if "custom_channel_names" in config:
                self.custom_channel_names = config["custom_channel_names"]
            
            # Load custom units
            if "custom_units" in config:
                self.custom_units = config["custom_units"]
            
            # Load conversion formulas
            if "conversion_formulas" in config:
                self.conversion_formulas = config["conversion_formulas"]
            
            # Load warning thresholds
            if "warning_thresholds" in config:
                self.warning_thresholds = {k: float(v) for k, v in config["warning_thresholds"].items()}
            
            # Load channel status
            if "channel_status" in config:
                for channel, status in config["channel_status"].items():
                    if channel in self.status_vars:
                        self.status_vars[channel].set(status)
            
            # Load graph enabled channels
            if "graph_enabled_channels" in config:
                for channel, status in config["graph_enabled_channels"].items():
                    if channel in self.graph_enabled_channels:
                        self.graph_enabled_channels[channel].set(status)
            
            # Cập nhật hiển thị
            self.update_channel_display()
            self.update_graph()
            
            # Reset application sau khi load
            self.reset_app()
            
            messagebox.showinfo("Success", "Configuration loaded successfully!")
            
        except json.JSONDecodeError:
            messagebox.showerror("Error", "Invalid configuration file format!")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to load configuration:\n{str(e)}")


    def apply_conversion_formula(self, voltage, channel):
        """Áp dụng công thức chuyển đổi cho giá trị điện áp"""
        formula = self.conversion_formulas.get(channel, "x")
        
        if formula == "x" or not formula:
            return voltage
        
        try:
            expression = formula.replace('x', str(voltage))
            result = eval(expression)
            return result
        except:
            return voltage
    
    def update_adc_values(self):
        """Đọc dữ liệu từ ADC và cập nhật vào bảng và đồ thị"""
        adc_data = self.read_adc_data()
        
        # Thêm timestamp cho đồ thị
        if len(self.time_data) == 0:
            self.time_data.append(0)
        else:
            self.time_data.append(self.time_data[-1] + 1)
        
        for i, channel in enumerate(self.default_channels):
            if self.status_vars[channel].get():
                voltage = adc_data[i]
                converted_value = self.apply_conversion_formula(voltage, channel)
                
                self.check_warnings(channel, converted_value)
                
                display_name = self.custom_channel_names.get(channel, channel)
                unit = self.custom_units.get(channel, "V")
                formatted_value = f"{converted_value:.3f} {unit}"
                
                item = self.channel_items[channel]
                self.tree.item(item, values=(display_name, formatted_value, unit))
                
                # Thêm dữ liệu vào graph_data
                self.graph_data[channel].append(converted_value)
            else:
                display_name = self.custom_channel_names.get(channel, channel)
                unit = self.custom_units.get(channel, "V")
                
                item = self.channel_items[channel]
                self.tree.item(item, values=(display_name, "--", unit))
                
                # Thêm None hoặc giữ giá trị cuối cho kênh OFF
                if len(self.graph_data[channel]) > 0:
                    self.graph_data[channel].append(self.graph_data[channel][-1])
                else:
                    self.graph_data[channel].append(0)
        
        # Cập nhật đồ thị
        self.update_graph()
        
        # Lên lịch cập nhật tiếp theo (500ms)
        self.root.after(500, self.update_adc_values)

def main():
    
    #import .so file
    lib = CDLL ("./libads1256.so")
    #configure argument 
    lib.Set_up_ads1256.restype = c_int
    lib.Select_CE0.restype = c_int
    lib.wait_DRDY.restype = None
    lib.gpio_clean.restype = None
    lib.gpio_clean()
    handle = lib.Set_up_ads1256()
    lib.RREG_func.argtypes = [c_uint,POINTER(c_char),POINTER(c_char),c_uint,c_uint]
    lib.RREG_func.restype = c_int
    lib.Get_all.argtypes = [c_uint,POINTER(c_double)]
    lib.Get_all.restype = c_int
    
    root = tk.Tk()
    app = ADC_Monitor_App(root,lib,handle)
    
    # Cấu hình resize
    root.grid_rowconfigure(1, weight=1)
    root.grid_rowconfigure(2, weight=2)
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    
    root.mainloop()

if __name__ == "__main__":
    main()
