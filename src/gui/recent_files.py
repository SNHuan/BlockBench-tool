class RecentFiles:
    def __init__(self, parent, max_items=5):
        self.parent = parent
        self.max_items = max_items
        self.recent_menu = None
        self.recent_files = []
        
    def add_file(self, file_path):
        """添加新的文件到最近文件列表"""
        if file_path in self.recent_files:
            self.recent_files.remove(file_path)
        self.recent_files.insert(0, file_path)
        if len(self.recent_files) > self.max_items:
            self.recent_files.pop()
        self.update_menu()
        
    def update_menu(self):
        """更新最近文件菜单"""
        if self.recent_menu is None:
            return
        
        # 清除现有菜单项
        self.recent_menu.delete(0, 'end')
        
        if not self.recent_files:
            self.recent_menu.add_command(
                label="(无最近文件)",
                state="disabled"
            )
            return
        
        # 添加最近文件列表
        for file_path in self.recent_files:
            def open_recent(path=file_path):
                self.parent.load_image(path)
            
            self.recent_menu.add_command(
                label=os.path.basename(file_path),
                command=open_recent
            ) 