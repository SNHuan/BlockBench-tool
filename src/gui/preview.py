import customtkinter as ctk
from PIL import Image, ImageTk, ImageEnhance
import os

class ImageEditorWindow:
    def __init__(self, parent, image_path, on_image_changed=None):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("图像预览")
        self.window.minsize(400, 300)
        
        self.on_image_changed = on_image_changed
        self.image_path = image_path
        self.image = Image.open(image_path)
        
        # 创建预览区域
        self.preview_canvas = ctk.CTkCanvas(
            self.window,
            bg='#2b2b2b',
            highlightthickness=0
        )
        self.preview_canvas.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 绑定事件
        self.preview_canvas.bind('<Configure>', self.update_preview)
        
        # 初始显示
        self.update_preview()
        
        self.window.lift()
        self.window.focus_force()

    def update_preview(self, event=None):
        """更新预览图片"""
        if not self.image:
            return
            
        try:
            # 获取画布尺寸
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # 计算缩放比例
            img_width, img_height = self.image.size
            scale = min(
                canvas_width / img_width,
                canvas_height / img_height
            )
            
            # 缩放图片
            new_width = int(img_width * scale)
            new_height = int(img_height * scale)
            
            resized = self.image.resize(
                (new_width, new_height),
                Image.Resampling.LANCZOS
            )
            
            # 更新显示
            self.preview_photo = ImageTk.PhotoImage(resized)
            
            # 计算居中位置
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(
                x, y,
                anchor="nw",
                image=self.preview_photo
            )
            
        except Exception as e:
            print(f"更新预览出错：{str(e)}")