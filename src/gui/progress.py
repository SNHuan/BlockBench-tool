class ProgressDialog:
    def __init__(self, parent, title="处理中"):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title(title)
        self.dialog.geometry("300x150")
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        self.progress_bar = ctk.CTkProgressBar(self.dialog)
        self.progress_bar.pack(pady=20)
        
        self.label = ctk.CTkLabel(self.dialog, text="正在处理...")
        self.label.pack(pady=10)
        
    def update(self, value, text=None):
        """更新进度条和文本"""
        self.progress_bar.set(value)
        if text:
            self.label.configure(text=text) 