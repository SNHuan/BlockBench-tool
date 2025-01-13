import customtkinter as ctk

class ProgressDialog:
    def __init__(self, parent, message, maximum=100):
        """初始化进度对话框
        
        Args:
            parent: 父窗口
            message: 显示的消息
            maximum: 进度条最大值
        """
        self.window = ctk.CTkToplevel(parent)
        self.window.title("处理中")
        self.window.geometry("300x150")
        self.window.resizable(False, False)
        
        # 使窗口居中
        self.window.transient(parent)
        self.window.grab_set()
        
        x = parent.winfo_x() + parent.winfo_width()//2 - 150
        y = parent.winfo_y() + parent.winfo_height()//2 - 75
        self.window.geometry(f"+{x}+{y}")
        
        # 消息标签
        self.message = ctk.CTkLabel(
            self.window,
            text=message,
            font=ctk.CTkFont(size=14)
        )
        self.message.pack(pady=20)
        
        # 进度条
        self.progress = ctk.CTkProgressBar(self.window)
        self.progress.pack(fill="x", padx=20, pady=10)
        self.progress.set(0)
        
        self.maximum = maximum
        
        # 更新界面
        self.window.update()
    
    def update(self, value):
        """更新进度
        
        Args:
            value: 当前进度值
        """
        self.progress.set(value / self.maximum)
        self.window.update()
    
    def destroy(self):
        """销毁对话框"""
        self.window.destroy() 