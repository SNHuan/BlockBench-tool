import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
import os

class BatchProcessDialog:
    def __init__(self, parent, process_callback):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("批量处理")
        self.dialog.geometry("500x400")
        
        self.process_callback = process_callback
        self.files = []
        
        # 创建文件列表
        self.list_frame = ctk.CTkFrame(self.dialog)
        self.list_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.file_listbox = tk.Listbox(
            self.list_frame,
            selectmode="extended",
            bg="#2b2b2b",
            fg="white",
            selectbackground="#1f538d"
        )
        self.file_listbox.pack(fill="both", expand=True)
        
        # 创建按钮
        self.button_frame = ctk.CTkFrame(self.dialog)
        self.button_frame.pack(fill="x", padx=10, pady=5)
        
        self.add_btn = ctk.CTkButton(
            self.button_frame,
            text="添加文件",
            command=self.add_files
        )
        self.add_btn.pack(side="left", padx=5)
        
        self.remove_btn = ctk.CTkButton(
            self.button_frame,
            text="移除选中",
            command=self.remove_selected
        )
        self.remove_btn.pack(side="left", padx=5)
        
        self.process_btn = ctk.CTkButton(
            self.button_frame,
            text="开始处理",
            command=self.process_files
        )
        self.process_btn.pack(side="right", padx=5)
        
    def add_files(self):
        files = filedialog.askopenfilenames(
            filetypes=[
                ("图片文件", "*.png;*.gif;*.jpg;*.jpeg"),
                ("所有文件", "*.*")
            ]
        )
        for file in files:
            if file not in self.files:
                self.files.append(file)
                self.file_listbox.insert("end", os.path.basename(file))
                
    def remove_selected(self):
        selected = self.file_listbox.curselection()
        for index in reversed(selected):
            self.file_listbox.delete(index)
            self.files.pop(index)
            
    def process_files(self):
        total = len(self.files)
        for i, file in enumerate(self.files, 1):
            try:
                self.process_callback(file)
            except Exception as e:
                print(f"处理文件 {file} 时出错: {e}")
        self.dialog.destroy() 