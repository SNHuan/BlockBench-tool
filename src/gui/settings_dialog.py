import customtkinter as ctk
from ..utils.settings import Settings

class SettingsDialog:
    def __init__(self, parent):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("设置")
        self.dialog.geometry("400x500")
        
        # 创建设置项
        self.create_settings_ui()
        
    def create_settings_ui(self):
        # 最大帧数设置
        frame = ctk.CTkFrame(self.dialog)
        frame.pack(fill="x", padx=10, pady=5)
        
        label = ctk.CTkLabel(frame, text="最大帧数:")
        label.pack(side="left", padx=5)
        
        self.max_frames_entry = ctk.CTkEntry(frame)
        self.max_frames_entry.insert(0, str(Settings.DEFAULT_CONFIG["max_frames"]))
        self.max_frames_entry.pack(side="right", padx=5)
        
        # 帧间隔设置
        frame = ctk.CTkFrame(self.dialog)
        frame.pack(fill="x", padx=10, pady=5)
        
        label = ctk.CTkLabel(frame, text="最小帧间隔(秒):")
        label.pack(side="left", padx=5)
        
        self.min_interval_entry = ctk.CTkEntry(frame)
        self.min_interval_entry.insert(0, str(Settings.DEFAULT_CONFIG["min_frame_interval"]))
        self.min_interval_entry.pack(side="right", padx=5)
        
        # 保存按钮
        self.save_btn = ctk.CTkButton(
            self.dialog,
            text="保存设置",
            command=self.save_settings
        )
        self.save_btn.pack(pady=20)
        
    def save_settings(self):
        try:
            max_frames = int(self.max_frames_entry.get())
            min_interval = float(self.min_interval_entry.get())
            
            if max_frames <= 0:
                raise ValueError("最大帧数必须大于0")
            if min_interval <= 0:
                raise ValueError("最小帧间隔必须大于0")
            
            # 更新设置
            Settings.DEFAULT_CONFIG["max_frames"] = max_frames
            Settings.DEFAULT_CONFIG["min_frame_interval"] = min_interval
            
            self.dialog.destroy()
            
        except ValueError as e:
            CTkMessagebox(
                title="错误",
                message=str(e),
                icon="cancel"
            ) 