import customtkinter as ctk
import cv2
import numpy as np
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
from tkinter import filedialog
import os
from tkinterdnd2 import DND_FILES

class PreviewWindow:
    def __init__(self, parent, image_path):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("预览")
        self.dialog.geometry("1000x800")
        
        # 初始化播放控制变量（移到最前面）
        self.is_playing = False
        self.current_speed = 1.0
        self.current_frame = 0
        self.animation_after_id = None
        self.is_gif = False
        
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.dialog)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=5)
        
        # 创建工具栏
        self.create_toolbar()
        
        # 创建预览区域
        self.preview_frame = ctk.CTkFrame(self.main_frame, fg_color="#2b2b2b")
        self.preview_frame.pack(fill="both", expand=True, padx=5, pady=5)
        
        self.canvas = ctk.CTkCanvas(
            self.preview_frame,
            bg='#2b2b2b',
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        
        # 初始化默认值
        self.DEFAULT_VALUES = {
            'scale': 1.0,
            'brightness': 0,
            'contrast': 1.0,
            'rotation': 0,
            'saturation': 1.0,
            'sharpness': 1.0,
            'hue': 0
        }
        
        # 图像处理变量
        self.image_path = image_path
        self.scale = self.DEFAULT_VALUES['scale']
        self.brightness = self.DEFAULT_VALUES['brightness']
        self.contrast = self.DEFAULT_VALUES['contrast']
        self.rotation = self.DEFAULT_VALUES['rotation']
        self.saturation = self.DEFAULT_VALUES['saturation']
        self.sharpness = self.DEFAULT_VALUES['sharpness']
        self.hue = self.DEFAULT_VALUES['hue']
        
        # 鼠标事件绑定
        self.canvas.bind('<Configure>', self.on_resize)
        self.canvas.bind('<MouseWheel>', self.on_mousewheel)
        self.canvas.bind('<Control-MouseWheel>', self.on_ctrl_mousewheel)
        
        # 创建信息面板
        self.create_info_panel()
        
        # 设置快捷键
        self.setup_shortcuts()
        
        # 设置拖放功能（移到这里）
        self.setup_drag_drop()
        
        # 加载图片
        self.load_image()
        
        # 窗口居中
        self.center_window()
        
    def create_toolbar(self):
        """创建工具栏"""
        # 创建顶部工具栏框架
        self.toolbar = ctk.CTkFrame(self.main_frame, fg_color="#1f1f1f", height=40)
        self.toolbar.pack(fill="x", padx=5, pady=(5, 0))
        self.toolbar.pack_propagate(False)  # 固定高度
        
        # 左侧控制区
        left_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        left_frame.pack(side="left", fill="x", expand=True, padx=10, pady=5)
        
        # 缩放显示
        zoom_label = ctk.CTkLabel(
            left_frame,
            text="缩放:",
            font=("Arial", 12)
        )
        zoom_label.pack(side="left", padx=(0, 5))
        
        self.zoom_label = ctk.CTkLabel(
            left_frame,
            text="100%",
            width=50,
            font=("Arial", 12)
        )
        self.zoom_label.pack(side="left", padx=(0, 20))
        
        # 创建滑块控制区
        sliders_frame = ctk.CTkFrame(self.main_frame, fg_color="#1f1f1f", height=40)
        sliders_frame.pack(fill="x", padx=5, pady=(5, 0))
        sliders_frame.pack_propagate(False)
        
        # 亮度控制
        bright_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        bright_frame.pack(side="left", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            bright_frame,
            text="亮度:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 5))
        
        self.brightness_slider = ctk.CTkSlider(
            bright_frame,
            from_=-100,
            to=100,
            number_of_steps=200,
            command=self.on_brightness_change,
            width=150
        )
        self.brightness_slider.pack(side="left")
        self.brightness_slider.set(0)
        
        # 对比度控制
        contrast_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        contrast_frame.pack(side="left", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            contrast_frame,
            text="对比度:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 5))
        
        self.contrast_slider = ctk.CTkSlider(
            contrast_frame,
            from_=0.5,
            to=1.5,
            number_of_steps=100,
            command=self.on_contrast_change,
            width=150
        )
        self.contrast_slider.pack(side="left")
        self.contrast_slider.set(1.0)
        
        # 饱和度控制
        saturation_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        saturation_frame.pack(side="left", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            saturation_frame,
            text="饱和度:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 5))
        
        self.saturation_slider = ctk.CTkSlider(
            saturation_frame,
            from_=0.0,
            to=2.0,
            number_of_steps=100,
            command=self.on_saturation_change,
            width=150
        )
        self.saturation_slider.pack(side="left")
        self.saturation_slider.set(1.0)
        
        # 色相控制
        hue_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        hue_frame.pack(side="left", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            hue_frame,
            text="色相:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 5))
        
        self.hue_slider = ctk.CTkSlider(
            hue_frame,
            from_=-180,  # 色相范围 -180 到 180 度
            to=180,
            number_of_steps=360,
            command=self.on_hue_change,
            width=150
        )
        self.hue_slider.pack(side="left")
        self.hue_slider.set(0)
        
        # 在饱和度控制后添加锐化控制
        sharpness_frame = ctk.CTkFrame(sliders_frame, fg_color="transparent")
        sharpness_frame.pack(side="left", expand=True, padx=10, pady=5)
        
        ctk.CTkLabel(
            sharpness_frame,
            text="锐化:",
            font=("Arial", 12)
        ).pack(side="left", padx=(0, 5))
        
        self.sharpness_slider = ctk.CTkSlider(
            sharpness_frame,
            from_=0.0,
            to=2.0,
            number_of_steps=100,
            command=self.on_sharpness_change,
            width=150
        )
        self.sharpness_slider.pack(side="left")
        self.sharpness_slider.set(1.0)
        
        # 右侧按钮区
        right_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        right_frame.pack(side="right", padx=10, pady=5)
        
        # 旋转按钮
        ctk.CTkButton(
            right_frame,
            text="↺",
            width=40,
            height=30,
            command=lambda: self.rotate(-90)
        ).pack(side="left", padx=2)
        
        ctk.CTkButton(
            right_frame,
            text="↻",
            width=40,
            height=30,
            command=lambda: self.rotate(90)
        ).pack(side="left", padx=2)
        
        # 重置按钮
        ctk.CTkButton(
            right_frame,
            text="重置",
            width=60,
            height=30,
            command=self.reset_all
        ).pack(side="left", padx=2)
        
        # 保存按钮
        ctk.CTkButton(
            right_frame,
            text="保存",
            width=60,
            height=30,
            command=self.save_image
        ).pack(side="left", padx=2)
        
        # 添加播放控制区
        play_frame = ctk.CTkFrame(self.toolbar, fg_color="transparent")
        play_frame.pack(side="right", padx=10)
        
        self.play_btn = ctk.CTkButton(
            play_frame,
            text="▶",
            width=40,
            height=30,
            command=self.toggle_play
        )
        self.play_btn.pack(side="left", padx=2)
        
        # 添加帧率控制
        self.speed_var = ctk.StringVar(value="1x")
        self.speed_menu = ctk.CTkOptionMenu(
            play_frame,
            values=["0.5x", "1x", "2x"],
            variable=self.speed_var,
            width=60,
            command=self.on_speed_change
        )
        self.speed_menu.pack(side="left", padx=2)
        
    def load_image(self):
        """加载图片"""
        try:
            # 先尝试用 PIL 打开图片
            pil_image = Image.open(self.image_path)
            
            # 如果是 GIF，获取第一帧
            if getattr(pil_image, "is_animated", False):
                self.is_gif = True
                self.frame_count = pil_image.n_frames
                self.current_frame = 0
                self.frames = []
                
                # 预加载所有帧
                for frame in range(self.frame_count):
                    pil_image.seek(frame)
                    # 转换为 RGB 模式
                    frame_rgb = pil_image.convert('RGB')
                    # 转换为 numpy 数组
                    frame_array = np.array(frame_rgb)
                    self.frames.append(frame_array)
                
                self.original = self.frames[0]
                
                # 获取帧延迟时间
                self.frame_delay = pil_image.info.get('duration', 100)  # 默认 100ms
                
                # 开始动画
                self.play_animation()
            else:
                self.is_gif = False
                # 如果是普通图片，直接转换为 numpy 数组
                pil_image = pil_image.convert('RGB')
                self.original = np.array(pil_image)
            
            self.update_preview()
            
        except Exception as e:
            CTkMessagebox(
                title="错误",
                message=f"无法加载图片：{str(e)}",
                icon="cancel"
            )
    
    def play_animation(self):
        """播放 GIF 动画"""
        try:
            # 如果存在之前的动画定时器，先取消它
            if hasattr(self, 'animation_after_id') and self.animation_after_id:
                self.dialog.after_cancel(self.animation_after_id)
                self.animation_after_id = None
            
            if self.is_gif and self.is_playing:
                self.current_frame = (self.current_frame + 1) % self.frame_count
                self.original = self.frames[self.current_frame]
                self.update_preview()
                self.update_info()  # 更新帧数显示
                
                # 使用当前的播放速度
                current_delay = int(self.frame_delay * self.current_speed)
                self.animation_after_id = self.dialog.after(current_delay, self.play_animation)
        except Exception as e:
            print(f"播放动画时出错：{str(e)}")
    
    def update_preview(self):
        """更新预览"""
        if not hasattr(self, 'original') or self.original is None:
            return
        
        try:
            # 应用图像处理
            img = self.original.copy()
            
            # 色相调整
            if self.hue != 0:
                # 转换到HSV色彩空间
                hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
                # 调整色相通道
                hsv[:, :, 0] = (hsv[:, :, 0] + self.hue) % 180
                img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            
            # 亮度和对比度
            img = cv2.convertScaleAbs(
                img,
                alpha=self.contrast,
                beta=self.brightness
            )
            
            # 饱和度
            if self.saturation != 1.0:
                hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
                hsv[:, :, 1] = hsv[:, :, 1] * self.saturation
                hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
                img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
            
            # 锐化
            if self.sharpness != 1.0:
                kernel = np.array([[-1,-1,-1],
                                 [-1, 9,-1],
                                 [-1,-1,-1]]) * self.sharpness
                img = cv2.filter2D(img, -1, kernel)
            
            # 旋转
            if self.rotation != 0:
                center = (img.shape[1] // 2, img.shape[0] // 2)
                matrix = cv2.getRotationMatrix2D(center, self.rotation, 1.0)
                img = cv2.warpAffine(img, matrix, (img.shape[1], img.shape[0]))
            
            # 缩放
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                # 计算缩放比例
                scale_x = canvas_width / img.shape[1]
                scale_y = canvas_height / img.shape[0]
                scale = min(scale_x, scale_y) * self.scale
                
                if scale != 1:
                    new_width = int(img.shape[1] * scale)
                    new_height = int(img.shape[0] * scale)
                    img = cv2.resize(
                        img,
                        (new_width, new_height),
                        interpolation=cv2.INTER_LANCZOS4
                    )
            
            # 转换为PhotoImage
            img = Image.fromarray(img)
            self.photo = ImageTk.PhotoImage(img)
            
            # 更新画布
            self.canvas.delete("all")
            self.canvas.create_image(
                canvas_width//2,
                canvas_height//2,
                image=self.photo,
                anchor="center"
            )
            
            # 更新缩放标签
            self.zoom_label.configure(text=f"{int(self.scale * 100)}%")
            
        except Exception as e:
            print(f"更新预览时出错：{str(e)}")
    
    def on_resize(self, event):
        """窗口大小改变时更新预览"""
        self.update_preview()
    
    def on_mousewheel(self, event):
        """鼠标滚轮缩放"""
        if event.delta > 0:
            self.scale *= 1.1
        else:
            self.scale /= 1.1
        self.update_preview()
    
    def on_ctrl_mousewheel(self, event):
        """Ctrl+滚轮旋转"""
        if event.delta > 0:
            self.rotate(5)
        else:
            self.rotate(-5)
    
    def on_brightness_change(self, value):
        """亮度改变"""
        self.brightness = float(value)
        self.update_preview()
    
    def on_contrast_change(self, value):
        """对比度改变"""
        self.contrast = float(value)
        self.update_preview()
    
    def rotate(self, angle):
        """旋转图片"""
        self.rotation = (self.rotation + angle) % 360
        self.update_preview()
    
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
    
    def reset_all(self):
        """重置所有参数为默认值"""
        self.scale = self.DEFAULT_VALUES['scale']
        self.brightness = self.DEFAULT_VALUES['brightness']
        self.contrast = self.DEFAULT_VALUES['contrast']
        self.rotation = self.DEFAULT_VALUES['rotation']
        self.saturation = self.DEFAULT_VALUES['saturation']
        self.sharpness = self.DEFAULT_VALUES['sharpness']
        self.hue = self.DEFAULT_VALUES['hue']
        
        # 重置所有滑块
        self.brightness_slider.set(self.brightness)
        self.contrast_slider.set(self.contrast)
        self.saturation_slider.set(self.saturation)
        self.sharpness_slider.set(self.sharpness)
        self.hue_slider.set(self.hue)
        
        self.update_preview()
        
    def save_image(self):
        """保存当前图片"""
        try:
            # 根据原始图片是否为GIF提供不同的保存选项
            if self.is_gif:
                save_options = [
                    ("精灵图 PNG", "*.png"),
                    ("GIF 动画", "*.gif")
                ]
            else:
                save_options = [
                    ("PNG 文件", "*.png"),
                    ("JPEG 文件", "*.jpg"),
                    ("所有文件", "*.*")
                ]
            
            file_path = filedialog.asksaveasfilename(
                defaultextension=".png",
                filetypes=save_options
            )
            
            if not file_path:
                return
            
            # 如果是GIF且用户选择保存为GIF
            if self.is_gif and file_path.lower().endswith('.gif'):
                # 创建新的GIF
                processed_frames = []
                for frame in self.frames:
                    img = frame.copy()
                    
                    # 应用所有图像处理效果
                    if self.hue != 0:
                        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
                        hsv[:, :, 0] = (hsv[:, :, 0] + self.hue) % 180
                        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
                    
                    if self.contrast != 1.0 or self.brightness != 0:
                        img = cv2.convertScaleAbs(img, alpha=self.contrast, beta=self.brightness)
                    
                    if self.saturation != 1.0:
                        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
                        hsv[:, :, 1] = hsv[:, :, 1] * self.saturation
                        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
                        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
                    
                    if self.rotation != 0:
                        center = (img.shape[1] // 2, img.shape[0] // 2)
                        matrix = cv2.getRotationMatrix2D(center, self.rotation, 1.0)
                        img = cv2.warpAffine(img, matrix, (img.shape[1], img.shape[0]))
                    
                    processed_frames.append(Image.fromarray(img))
                
                # 保存GIF
                processed_frames[0].save(
                    file_path,
                    save_all=True,
                    append_images=processed_frames[1:],
                    duration=self.frame_delay,
                    loop=0
                )
                
            # 如果是GIF且用户选择保存为PNG（精灵图）
            elif self.is_gif and file_path.lower().endswith('.png'):
                # 创建精灵图
                total_width = self.frames[0].shape[1] * len(self.frames)
                height = self.frames[0].shape[0]
                sprite_sheet = np.zeros((height, total_width, 3), dtype=np.uint8)
                
                for i, frame in enumerate(self.frames):
                    img = frame.copy()
                    
                    # 应用所有图像处理效果
                    if self.hue != 0:
                        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
                        hsv[:, :, 0] = (hsv[:, :, 0] + self.hue) % 180
                        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
                    
                    if self.contrast != 1.0 or self.brightness != 0:
                        img = cv2.convertScaleAbs(img, alpha=self.contrast, beta=self.brightness)
                    
                    if self.saturation != 1.0:
                        hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
                        hsv[:, :, 1] = hsv[:, :, 1] * self.saturation
                        hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
                        img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
                    
                    if self.rotation != 0:
                        center = (img.shape[1] // 2, img.shape[0] // 2)
                        matrix = cv2.getRotationMatrix2D(center, self.rotation, 1.0)
                        img = cv2.warpAffine(img, matrix, (img.shape[1], img.shape[0]))
                    
                    # 将帧添加到精灵图中
                    sprite_sheet[:, i*img.shape[1]:(i+1)*img.shape[1]] = img
                
                # 保存精灵图
                Image.fromarray(sprite_sheet).save(file_path)
                
            # 如果是普通图片
            else:
                img = self.original.copy()
                
                # 应用所有图像处理效果
                if self.hue != 0:
                    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
                    hsv[:, :, 0] = (hsv[:, :, 0] + self.hue) % 180
                    img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
                
                if self.contrast != 1.0 or self.brightness != 0:
                    img = cv2.convertScaleAbs(img, alpha=self.contrast, beta=self.brightness)
                
                if self.saturation != 1.0:
                    hsv = cv2.cvtColor(img, cv2.COLOR_RGB2HSV).astype(np.float32)
                    hsv[:, :, 1] = hsv[:, :, 1] * self.saturation
                    hsv[:, :, 1] = np.clip(hsv[:, :, 1], 0, 255)
                    img = cv2.cvtColor(hsv.astype(np.uint8), cv2.COLOR_HSV2RGB)
                
                if self.rotation != 0:
                    center = (img.shape[1] // 2, img.shape[0] // 2)
                    matrix = cv2.getRotationMatrix2D(center, self.rotation, 1.0)
                    img = cv2.warpAffine(img, matrix, (img.shape[1], img.shape[0]))
                
                Image.fromarray(img).save(file_path)
            
            CTkMessagebox(
                title="成功",
                message="图片已保存",
                icon="check"
            )
            
        except Exception as e:
            CTkMessagebox(
                title="错误",
                message=f"保存图片时出错：{str(e)}",
                icon="cancel"
            )
            
    def on_saturation_change(self, value):
        """饱和度改变"""
        self.saturation = float(value)
        self.update_preview()
        
    def on_sharpness_change(self, value):
        """锐化改变"""
        self.sharpness = float(value)
        self.update_preview()
        
    def on_hue_change(self, value):
        """色相改变"""
        self.hue = float(value)
        self.update_preview()
        
    def toggle_play(self):
        """切换播放状态"""
        if hasattr(self, 'is_playing'):
            self.is_playing = not self.is_playing
            self.play_btn.configure(text="⏸" if self.is_playing else "▶")
            
            if self.is_playing:
                self.play_animation()
            else:
                # 停止动画
                if self.animation_after_id:
                    self.dialog.after_cancel(self.animation_after_id)
                    self.animation_after_id = None
    
    def on_speed_change(self, value):
        """改变播放速度"""
        speed_map = {
            "0.5x": 2.0,
            "1x": 1.0,
            "2x": 0.5
        }
        self.current_speed = speed_map[value]
        
        # 如果当前正在播放，重新开始播放以应用新速度
        if hasattr(self, 'is_playing') and self.is_playing:
            # 重新启动动画（会自动取消旧的动画）
            self.play_animation()
    
    def create_info_panel(self):
        """创建信息面板"""
        self.info_frame = ctk.CTkFrame(self.main_frame, fg_color="#1f1f1f", height=30)
        self.info_frame.pack(fill="x", padx=5, pady=(0, 5))
        self.info_frame.pack_propagate(False)
        
        # 图片尺寸信息
        self.size_label = ctk.CTkLabel(
            self.info_frame,
            text="尺寸: --x--",
            font=("Arial", 12)
        )
        self.size_label.pack(side="left", padx=10)
        
        # 帧数信息
        self.frame_label = ctk.CTkLabel(
            self.info_frame,
            text="帧数: --/--",
            font=("Arial", 12)
        )
        self.frame_label.pack(side="left", padx=10)
        
        # 文件大小信息
        self.size_info_label = ctk.CTkLabel(
            self.info_frame,
            text="文件大小: --",
            font=("Arial", 12)
        )
        self.size_info_label.pack(side="left", padx=10)

    def update_info(self):
        """更新信息显示"""
        if hasattr(self, 'original'):
            # 更新尺寸信息
            height, width = self.original.shape[:2]
            self.size_label.configure(text=f"尺寸: {width}x{height}")
            
            # 更新帧数信息
            if hasattr(self, 'frame_count'):
                self.frame_label.configure(
                    text=f"帧数: {self.current_frame + 1}/{self.frame_count}"
                )
            
            # 更新文件大小信息
            file_size = os.path.getsize(self.image_path)
            size_str = self.format_size(file_size)
            self.size_info_label.configure(text=f"文件大小: {size_str}")

    @staticmethod
    def format_size(size):
        """格式化文件大小显示"""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB" 

    def setup_shortcuts(self):
        """设置键盘快捷键"""
        self.dialog.bind('<Control-s>', lambda e: self.save_image())
        self.dialog.bind('<Control-r>', lambda e: self.reset_all())
        self.dialog.bind('<space>', lambda e: self.toggle_play())
        self.dialog.bind('<Left>', lambda e: self.prev_frame())
        self.dialog.bind('<Right>', lambda e: self.next_frame())
        self.dialog.bind('<Control-plus>', lambda e: self.zoom(1.1))
        self.dialog.bind('<Control-minus>', lambda e: self.zoom(0.9)) 

    def setup_drag_drop(self):
        """设置拖放功能"""
        try:
            # 为预览窗口添加拖放绑定
            self.dialog.drop_target_register(DND_FILES)
            self.dialog.dnd_bind('<<Drop>>', self.on_drop)
            
            # 为预览画布添加拖放绑定
            self.preview_canvas.drop_target_register(DND_FILES)
            self.preview_canvas.dnd_bind('<<Drop>>', self.on_drop)
            
            # 为预览框架添加拖放绑定
            self.preview_frame.drop_target_register(DND_FILES)
            self.preview_frame.dnd_bind('<<Drop>>', self.on_drop)
        except Exception as e:
            print(f"设置拖放功能时出错：{str(e)}")

    def on_drop(self, event):
        """处理文件拖放"""
        try:
            file_path = event.data
            
            # 移除可能的大括号和引号
            file_path = file_path.strip('{}')
            file_path = file_path.strip('"')
            
            # 检查文件类型
            if file_path.lower().endswith(('.png', '.gif', '.jpg', '.jpeg')):
                self.image_path = file_path
                self.load_image()
                # 更新信息显示
                self.update_info()
                # 重置所有滑块
                self.reset_all()
            else:
                CTkMessagebox(
                    title="错误",
                    message="不支持的文件格式。请使用 PNG、GIF 或 JPEG 格式的图片。",
                    icon="cancel"
                )
        except Exception as e:
            CTkMessagebox(
                title="错误",
                message=f"无法加载图片：{str(e)}",
                icon="cancel"
            ) 