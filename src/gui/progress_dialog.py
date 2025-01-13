import customtkinter as ctk

class ProgressDialog:
    def __init__(self, parent):
        self.parent = parent
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("处理中")
        self.dialog.geometry("300x150")
        
        # 使窗口居中
        self.center_window()
        
        # 设置为模态窗口
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # 创建进度条
        self.progress_bar = ctk.CTkProgressBar(self.dialog)
        self.progress_bar.pack(padx=20, pady=(20, 10), fill="x")
        self.progress_bar.set(0)
        
        # 创建状态标签
        self.status_label = ctk.CTkLabel(
            self.dialog,
            text="准备中...",
            font=("Arial", 12)
        )
        self.status_label.pack(pady=10)
        
        # 标记对话框状态
        self.is_active = True
        
        # 更新UI
        self.dialog.update()
    
    def set_progress(self, value, status=None):
        """设置进度和状态"""
        if not self.is_active:
            return
            
        try:
            self.progress_bar.set(value / 100)
            if status:
                self.status_label.configure(text=status)
            self.dialog.update()
        except Exception:
            self.is_active = False
    
    def center_window(self):
        """窗口居中"""
        self.dialog.update()
        width = self.dialog.winfo_width()
        height = self.dialog.winfo_height()
        screen_width = self.dialog.winfo_screenwidth()
        screen_height = self.dialog.winfo_screenheight()
        
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        
        self.dialog.geometry(f"+{x}+{y}")
    
    def destroy(self):
        """关闭对话框"""
        if self.is_active:
            try:
                self.dialog.grab_release()
                self.dialog.destroy()
            except Exception:
                pass
            finally:
                self.is_active = False 