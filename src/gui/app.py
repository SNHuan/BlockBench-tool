# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
import os
from tkinterdnd2 import TkinterDnD, DND_FILES
import json
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.utils.image_processor import ImageProcessor
from src.models.geometry import GeometryGenerator
from src.models.animation import AnimationGenerator
from ..gui.preview import ImageEditorWindow
from .progress_dialog import ProgressDialog
from .batch_process import BatchProcessDialog
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import threading
import queue
import numpy as np
import cv2
from PIL import ImageDraw
import imageio.v3 as iio

class AnimationGeneratorApp:
    def __init__(self):
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 创建主窗口
        self.root = TkinterDnD.Tk()
        self.root.title("BlockBench 模型动画生成器")
        
        # 设置窗口最小尺寸
        self.root.minsize(900, 600)
        
        # 获取屏幕尺寸和计算窗口大小
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(int(screen_width * 0.7), 1200)
        window_height = min(int(screen_height * 0.7), 800)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 设置窗口背景色
        self.root.configure(bg='#1a1a1a')
        
        # 创建主框架
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color='#1a1a1a',  # 深黑色背景
            corner_radius=0
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # 创建左右分栏
        self.left_panel = ctk.CTkFrame(
            self.main_frame,
            width=300,
            fg_color='#242424',  # 稍微浅一点的深色
            corner_radius=0
        )
        self.left_panel.pack(side="left", fill="y", padx=10, pady=10)
        self.left_panel.pack_propagate(False)
        
        self.right_panel = ctk.CTkFrame(
            self.main_frame,
            fg_color='#242424',
            corner_radius=0
        )
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(0, 10), pady=10)
        
        # 创建界面元素
        self.create_menu()
        self.create_left_panel()
        self.create_right_panel()
        
        # 设置拖放功能
        self.setup_drag_drop()
        
        # 绑定窗口大小改变事件
        self.root.bind('<Configure>', self.on_window_resize)
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 初始化图像相关属性
        self.image = None
        self.image_path = None
        self.frames = []
        self.frame_durations = []
        self.current_frame = 0
        self.is_playing = False
        self.frame_delay = 100
        self.animation_after_id = None
        self.preview_photo = None
        
        # 初始化线程池和帧缓存
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.frame_queue = queue.Queue(maxsize=30)
        self.preload_thread = None
        self.frame_cache = {}
        self.current_size = None
        self.background_cache = {}
        
        # 创建后台线程池
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.frame_queue = queue.Queue(maxsize=30)

    def setup_window(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = TkinterDnD.Tk()
        self.root.title("BlockBench 工具")
        self.root.geometry("900x600")
        
        # 设置最小窗口大小
        self.root.minsize(800, 500)
        
        # 移除默认的白色边框
        self.root.configure(bg='#2b2b2b')
        
        # 创建主框架，使用深色背景
        self.main_frame = ctk.CTkFrame(
            self.root,
            fg_color='#2b2b2b',  # 深色背景
            corner_radius=0  # 移除圆角
        )
        self.main_frame.pack(fill="both", expand=True)
        
        # 创建左右分栏，添加一点间距
        self.left_panel = ctk.CTkFrame(
            self.main_frame,
            width=300,
            fg_color='#242424',  # 稍微浅一点的深色
            corner_radius=0
        )
        self.left_panel.pack(side="left", fill="y", padx=(10, 5), pady=10)
        self.left_panel.pack_propagate(False)
        
        self.right_panel = ctk.CTkFrame(
            self.main_frame,
            fg_color='#242424',
            corner_radius=0
        )
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 10), pady=10)

    def setup_ui(self):
        # 左侧面板内容
        self.create_left_panel()
        # 右侧面板内容
        self.create_right_panel()
        # 创建菜单栏
        self.create_menu()
        
        # 设置拖放功能
        self.setup_drag_drop()

    def create_left_panel(self):
        # 标题区域
        title_frame = ctk.CTkFrame(
            self.left_panel,
            fg_color='transparent'
        )
        title_frame.pack(fill="x", pady=(15, 20))
        
        title = ctk.CTkLabel(
            title_frame,
            text="BlockBench\n模型动画生成器",
            font=ctk.CTkFont(size=20, weight="bold"),
            justify="center"
        )
        title.pack()
        
        # 图片上传区
        upload_frame = ctk.CTkFrame(
            self.left_panel,
            fg_color='#2b2b2b',
            corner_radius=6
        )
        upload_frame.pack(fill="x", padx=15, pady=10)
        
        self.upload_btn = ctk.CTkButton(
            upload_frame,
            text="选择图片",
            command=self.upload_image,
            height=38,
            fg_color='#1f538d',
            hover_color='#1a4578'
        )
        self.upload_btn.pack(fill="x", padx=10, pady=(10, 5))
        
        self.file_label = ctk.CTkLabel(
            upload_frame,
            text="拖放图片到此处\n或点击上方按钮选择",
            wraplength=250,
            justify="center",
            text_color='#8b8b8b'  # 浅灰色文字
        )
        self.file_label.pack(pady=10)
        
        # 参数设置区
        settings_frame = ctk.CTkFrame(self.left_panel)
        settings_frame.pack(fill="x", padx=15, pady=10)
        
        ctk.CTkLabel(
            settings_frame,
            text="参数设置",
            font=ctk.CTkFont(size=14)
        ).pack(pady=5)
        
        # 添加参数输入框
        self.create_parameter_inputs(settings_frame)
        
        # 生成按钮
        self.generate_btn = ctk.CTkButton(
            self.left_panel,
            text="生成动画",
            command=self.generate_animation,
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45
        )
        self.generate_btn.pack(fill="x", padx=15, pady=20)
        
        # 添加状态栏和进度条
        self.status_frame = ctk.CTkFrame(self.left_panel)
        self.status_frame.pack(fill="x", padx=15, pady=(0, 10))
        
        self.status_label = ctk.CTkLabel(
            self.status_frame,
            text="就绪",
            font=ctk.CTkFont(size=12)
        )
        self.status_label.pack(side="left", padx=5)
        
        self.progress_bar = ctk.CTkProgressBar(self.status_frame)
        self.progress_bar.pack(fill="x", padx=5, pady=5)
        self.progress_bar.set(0)
        self.progress_bar.pack_forget()  # 默认隐藏进度条

    def create_right_panel(self):
        # 预览区标题栏
        preview_header = ctk.CTkFrame(
            self.right_panel,
            fg_color='transparent',
            height=40
        )
        preview_header.pack(fill="x")
        preview_header.pack_propagate(False)
        
        # 左侧标题
        ctk.CTkLabel(
            preview_header,
            text="预览",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=15)
        
        # 播放控制区域
        self.play_frame = ctk.CTkFrame(preview_header, fg_color='transparent')
        self.play_frame.pack(side="right", padx=15)
        
        # 预览画布区域
        self.preview_frame = ctk.CTkFrame(
            self.right_panel,
            fg_color='#2b2b2b',
            corner_radius=0
        )
        self.preview_frame.pack(fill="both", expand=True, pady=10)
        
        self.preview_canvas = ctk.CTkCanvas(
            self.preview_frame,
            bg='#2b2b2b',
            highlightthickness=0
        )
        self.preview_canvas.pack(fill="both", expand=True)
        
        # 初始化播放相关属性
        self.current_frame = 0
        self.is_playing = False
        self.frame_delay = 100
        self.animation_after_id = None

    def create_play_controls(self):
        """创建播放控制按钮"""
        # 先清除现有的控件
        for widget in self.play_frame.winfo_children():
            widget.destroy()
        
        # 播放/暂停按钮
        self.play_btn = ctk.CTkButton(
            self.play_frame,
            text="播放",
            width=60,
            command=self.toggle_play,
            fg_color='#1f538d',
            hover_color='#1a4578'
        )
        self.play_btn.pack(side="left", padx=2)
        
        # 帧控制按钮
        self.prev_btn = ctk.CTkButton(
            self.play_frame,
            text="◀",
            width=30,
            command=self.prev_frame,
            fg_color='#1f538d',
            hover_color='#1a4578'
        )
        self.prev_btn.pack(side="left", padx=2)
        
        self.next_btn = ctk.CTkButton(
            self.play_frame,
            text="▶",
            width=30,
            command=self.next_frame,
            fg_color='#1f538d',
            hover_color='#1a4578'
        )
        self.next_btn.pack(side="left", padx=2)
        
        # 帧计数器
        self.frame_label = ctk.CTkLabel(
            self.play_frame,
            text=f"帧: 1/{self.image.n_frames}"
        )
        self.frame_label.pack(side="left", padx=5)
        
        # 播放速度控制
        speed_frame = ctk.CTkFrame(self.play_frame, fg_color='transparent')
        speed_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(speed_frame, text="速度:").pack(side="left")
        self.speed_entry = ctk.CTkEntry(speed_frame, width=50)
        self.speed_entry.insert(0, "1.0")
        self.speed_entry.pack(side="left", padx=2)
        ctk.CTkLabel(speed_frame, text="x").pack(side="left")
        
        # 绑定速度输入框的按键事件
        self.speed_entry.bind('<KeyRelease>', self.update_speed)

    def toggle_play(self):
        """切换播放/暂停状态"""
        if not hasattr(self, 'image') or not hasattr(self.image, "n_frames"):
            return
        
        self.is_playing = not self.is_playing
        self.play_btn.configure(
            text="暂停" if self.is_playing else "播放",
            fg_color='#c93434' if self.is_playing else '#1f538d',
            hover_color='#a82c2c' if self.is_playing else '#1a4578'
        )
        
        # 禁用/启用帧控制按钮
        state = "disabled" if self.is_playing else "normal"
        self.prev_btn.configure(state=state)
        self.next_btn.configure(state=state)
        
        if self.is_playing:
            self.play_animation()
        else:
            if self.animation_after_id:
                self.root.after_cancel(self.animation_after_id)
                self.animation_after_id = None

    def play_animation(self):
        """播放动画"""
        if not self.is_playing or not self.frames:
            return
        
        try:
            # 更新预览
            self.update_preview()
            
            # 更新帧计数器
            self.frame_label.configure(
                text=f"帧: {self.current_frame + 1}/{len(self.frames)}"
            )
            
            # 计算下一帧
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            
            # 获取当前帧延迟
            delay = int(self.frame_durations[self.current_frame] / float(self.speed_entry.get()))
            
            # 继续播放
            self.animation_after_id = self.root.after(delay, self.play_animation)
            
        except Exception as e:
            print(f"播放出错：{str(e)}")
            self.toggle_play()

    def prev_frame(self):
        """显示上一帧"""
        if not hasattr(self, 'image') or not hasattr(self.image, "n_frames"):
            return
        
        self.current_frame = (self.current_frame - 1) % self.image.n_frames
        self.image.seek(self.current_frame)
        self.update_preview()
        self.frame_label.configure(text=f"帧: {self.current_frame + 1}/{self.image.n_frames}")

    def next_frame(self):
        """显示下一帧"""
        if not hasattr(self, 'image') or not hasattr(self.image, "n_frames"):
            return
        
        self.current_frame = (self.current_frame + 1) % self.image.n_frames
        self.image.seek(self.current_frame)
        self.update_preview()
        self.frame_label.configure(text=f"帧: {self.current_frame + 1}/{self.image.n_frames}")

    def create_menu(self):
        """创建菜单栏"""
        menu_bar = tk.Menu(self.root)
        self.root.config(menu=menu_bar)
        
        # 文件菜单
        file_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="文件", menu=file_menu)
        file_menu.add_command(label="打开图片", command=self.upload_image)
        file_menu.add_command(label="批量处理", command=self.show_batch_process)
        file_menu.add_separator()
        file_menu.add_command(label="退出", command=self.root.quit)
        
        # 编辑菜单
        edit_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="编辑", menu=edit_menu)
        edit_menu.add_command(label="设置", command=self.show_settings)
        
        # 视图菜单
        view_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="视图", menu=view_menu)
        view_menu.add_command(label="预览", command=self.show_preview)
        
        # 帮助菜单
        help_menu = tk.Menu(menu_bar, tearoff=0)
        menu_bar.add_cascade(label="帮助", menu=help_menu)
        help_menu.add_command(label="使用说明", command=self.show_help)
        help_menu.add_command(label="关于", command=self.show_about)

    def show_help(self):
        """显示使用说明"""
        help_text = """
使用说明：
1. 选择动画类型（普通/圆形）
2. 上传图片文件
3. 设置相关参数
4. 点击生成按钮
        """
        CTkMessagebox(
            title="使用说明",
            message=help_text,
            icon="info"
        )

    def show_about(self):
        """显示关于信息"""
        about_text = """
BlockBench 模型动画生成器 v1.0

一个用于生成 BlockBench 模型动画的工具。
支持普通动画和圆形动画，可以处理精灵图和GIF文件。

作者：Your Name
    """
        CTkMessagebox(
            title="关于",
            message=about_text,
            icon="info"
        )

    def show_preview(self):
        """显示预览窗口"""
        if not hasattr(self, 'image_path') or not self.image_path:
            CTkMessagebox(
                title="错误",
                message="请先选择图片文件",
                icon="cancel"
            )
            return
        ImageEditorWindow(self.root, self.image_path, self.on_preview_image_changed)

    def on_preview_image_changed(self, new_image_path):
        """预览窗口图片改变时的回调"""
        try:
            # 更新当前图片
            self.image = Image.open(new_image_path)
            
            # 更新预览
            self.update_preview()
        except Exception as e:
            CTkMessagebox(
                title="错误",
                message=f"更新预览失败：{str(e)}",
                icon="cancel"
            )

    def show_batch_process(self):
        BatchProcessDialog(self.root, self.process_single_file)

    def process_single_file(self, file_path):
        """处理单个文件"""
        self.image_path = file_path
        self.image = Image.open(file_path)
        self.auto_fill_image_info()
        self.generate_animation()

    def run(self):
        self.root.mainloop()

    def generate_geometry(self, params):
        """根据参数生成几何体"""
        if params["animation_type"] == "圆形动画":
            return GeometryGenerator.create_circle_geometry(
                params["texture_width"],
                params["texture_height"],
                params["frame_count"],
                params["rotation_angle"]
            )
        else:
            return GeometryGenerator.create_normal_geometry(
                params["texture_width"],
                params["texture_height"],
                params["frame_count"]
            )

    def show_settings(self):
        """显示设置对话框"""
        from .settings_dialog import SettingsDialog
        SettingsDialog(self.root)

    def setup_drag_drop(self):
        """设置拖放功能"""
        try:
            # 为主窗口添加拖放绑定
            self.root.drop_target_register(DND_FILES)
            self.root.dnd_bind('<<Drop>>', self.on_drop)
            
            # 为左侧面板添加拖放绑定
            self.left_panel.drop_target_register(DND_FILES)
            self.left_panel.dnd_bind('<<Drop>>', self.on_drop)
            
            # 为上传区域添加拖放绑定
            self.file_label.drop_target_register(DND_FILES)
            self.file_label.dnd_bind('<<Drop>>', self.on_drop)
            
            # 为预览区域添加拖放绑定（如果存在）
            if hasattr(self, 'canvas'):
                self.canvas.drop_target_register(DND_FILES)
                self.canvas.dnd_bind('<<Drop>>', self.on_drop)
            
        except Exception as e:
            print(f"设置拖放功能时出错：{str(e)}")

    def on_drop(self, event):
        """处理文件拖放"""
        file_path = event.data
        
        # 移除可能的大括号和引号
        file_path = file_path.strip('{}')
        file_path = file_path.strip('"')
        
        # 检查文件类型
        if file_path.lower().endswith(('.png', '.gif', '.jpg', '.jpeg')):
            try:
                self.image_path = file_path
                self.image = Image.open(file_path)
                
                filename = os.path.basename(file_path)
                self.file_label.configure(text=filename)
                
                # 自动填充图片信息
                self.auto_fill_image_info()
                
                # 更新预览
                self.update_preview()
                
            except Exception as e:
                CTkMessagebox(
                    title="错误",
                    message=f"无法加载图片：{str(e)}",
                    icon="cancel"
                )
        else:
            CTkMessagebox(
                title="错误",
                message="不支持的文件格式。请使用 PNG、GIF 或 JPEG 格式的图片。",
                icon="cancel"
            )

    def create_preview_area(self):
        # 创建右侧预览区
        preview_frame = ctk.CTkFrame(self.main_frame, fg_color="#1E1E1E")
        preview_frame.pack(side="right", fill="both", expand=True, padx=0, pady=0)
        
        # 预览标题
        preview_label = ctk.CTkLabel(
            preview_frame,
            text="预览",
            font=("Arial", 14, "bold")
        )
        preview_label.pack(anchor="w", padx=15, pady=10)
        
        # 预览画布
        self.preview_canvas = ctk.CTkCanvas(
            preview_frame,
            bg='#2D2D2D',
            highlightthickness=0
        )
        self.preview_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))

    def create_status_bar(self):
        self.status_bar = ctk.CTkFrame(
            self.main_frame,
            height=25,
            fg_color="#007ACC"
        )
        self.status_bar.pack(fill="x", side="bottom")
        
        self.status_label = ctk.CTkLabel(
            self.status_bar,
            text="就绪",
            text_color="#FFFFFF"
        )
        self.status_label.pack(side="left", padx=10)

    def create_parameter_inputs(self, parent):
        self.entries = {}
        
        # 创建输入框组
        input_group = ctk.CTkFrame(parent)
        input_group.pack(fill="x", padx=5, pady=5)
        
        # 基本参数
        params = [
            ("名称", "texture_name", ""),
            ("宽度", "texture_width", "32"),
            ("高度", "texture_height", "32"),
            ("帧数", "frame_count", "8"),
            ("动画速度(秒)", "animation_speed", "0.1")
        ]
        
        for label, key, default in params:
            frame = ctk.CTkFrame(input_group)
            frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                frame, text=label, width=80
            ).pack(side="left", padx=5)
            
            entry = ctk.CTkEntry(frame)
            entry.pack(side="right", fill="x", expand=True, padx=5)
            entry.insert(0, default)
            self.entries[key] = entry
        
        # 添加旋转角度输入框（默认隐藏）
        self.rotation_frame = ctk.CTkFrame(input_group)
        
        ctk.CTkLabel(
            self.rotation_frame,
            text="旋转角度",
            width=80
        ).pack(side="left", padx=5)
        
        self.entries["rotation_angle"] = ctk.CTkEntry(self.rotation_frame)
        self.entries["rotation_angle"].insert(0, "360")  # 默认360度旋转
        self.entries["rotation_angle"].pack(side="right", fill="x", expand=True, padx=5)
        
        # 添加循环选项
        loop_frame = ctk.CTkFrame(input_group)
        loop_frame.pack(fill="x", pady=2)
        
        self.loop_var = tk.BooleanVar(value=False)
        self.loop_checkbox = ctk.CTkCheckBox(
            loop_frame,
            text="循环动画",
            variable=self.loop_var,
            onvalue=True,
            offvalue=False
        )
        self.loop_checkbox.pack(side="left", padx=5)
        
        # 动画类型选择（移到最下方）
        type_frame = ctk.CTkFrame(input_group)
        type_frame.pack(fill="x", pady=(10, 2))
        
        ctk.CTkLabel(
            type_frame,
            text="动画类型",
            font=ctk.CTkFont(size=12)
        ).pack(pady=(0, 5))
        
        self.animation_type = ctk.CTkSegmentedButton(
            type_frame,
            values=["普通动画", "圆形动画"],
            command=self.on_animation_type_change,
            selected_color='#1f538d',
            unselected_color='#2b2b2b'
        )
        self.animation_type.pack(fill="x", padx=5, pady=(0, 5))
        self.animation_type.set("普通动画")

    def on_animation_type_change(self, value):
        """动画类型改变时的回调"""
        if value == "圆形动画":
            # 显示旋转角度输入框
            self.rotation_frame.pack(fill="x", pady=2)
        else:
            # 隐藏旋转角度输入框
            self.rotation_frame.pack_forget()

    def upload_image(self):
        """上传图片"""
        # 停止当前播放
        if self.is_playing:
            self.toggle_play()
        
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("图片文件", "*.png;*.gif;*.jpg;*.jpeg"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                self.image_path = file_path
                self.image = Image.open(file_path)
                
                # 清除之前的缓存
                self.frames = []
                self.frame_durations = []
                self.frame_cache.clear()
                self.current_size = None
                
                # 如果是 GIF，加载所有帧并自动填充参数
                if getattr(self.image, "is_animated", False):
                    # 创建进度对话框
                    progress = ProgressDialog(
                        parent=self.root,
                        message="正在加载图片帧...",
                        maximum=self.image.n_frames
                    )
                    
                    # 读取所有帧
                    total_duration = 0
                    for i in range(self.image.n_frames):
                        self.image.seek(i)
                        # 复制当前帧并转换为 RGBA 模式
                        frame = self.image.convert('RGBA')
                        self.frames.append(frame.copy())
                        # 获取帧延迟，默认为 100ms
                        duration = self.image.info.get('duration', 100)
                        self.frame_durations.append(duration)
                        total_duration += duration
                        progress.update(i + 1)
                    
                    progress.destroy()
                    
                    # 自动填充参数
                    self.auto_fill_parameters(
                        frame_count=self.image.n_frames,
                        width=self.image.width,
                        height=self.image.height,
                        avg_duration=total_duration / self.image.n_frames
                    )
                    
                    # 重置到第一帧
                    self.image.seek(0)
                    self.current_frame = 0
                    
                    # 创建播放控制
                    self.create_play_controls()
                else:
                    # 普通图片只有一帧
                    self.frames = [self.image]
                    self.frame_durations = [100]
                    self.current_frame = 0
                    
                    # 自动填充参数
                    self.auto_fill_parameters(
                        frame_count=1,
                        width=self.image.width,
                        height=self.image.height,
                        avg_duration=100
                    )
                    
                    # 清除播放控制
                    for widget in self.play_frame.winfo_children():
                        widget.destroy()
                
                # 更新文件名显示
                filename = os.path.basename(file_path)
                self.file_label.configure(text=filename)
                
                # 更新预览
                self.update_preview()
                
            except Exception as e:
                CTkMessagebox(
                    title="错误",
                    message=f"无法加载图片：{str(e)}",
                    icon="cancel"
                )

    def auto_fill_parameters(self, frame_count, width, height, avg_duration):
        """自动填充参数设置
        
        Args:
            frame_count (int): 帧数
            width (int): 图片宽度
            height (int): 图片高度
            avg_duration (float): 平均帧持续时间(ms)
        """
        try:
            # 填充纹理名称（使用文件名，不含扩展名）
            texture_name = os.path.splitext(os.path.basename(self.image_path))[0]
            self.entries["texture_name"].delete(0, tk.END)
            self.entries["texture_name"].insert(0, texture_name)
            
            # 填充尺寸
            self.entries["texture_width"].delete(0, tk.END)
            self.entries["texture_width"].insert(0, str(width))
            
            self.entries["texture_height"].delete(0, tk.END)
            self.entries["texture_height"].insert(0, str(height))
            
            # 填充帧数
            self.entries["frame_count"].delete(0, tk.END)
            self.entries["frame_count"].insert(0, str(frame_count))
            
            # 填充动画速度（将毫秒转换为秒）
            animation_speed = avg_duration / 1000
            self.entries["animation_speed"].delete(0, tk.END)
            self.entries["animation_speed"].insert(0, f"{animation_speed:.3f}")
            
            # 如果是多帧图像，默认选择循环动画
            if frame_count > 1:
                self.loop_var.set(True)
            
        except Exception as e:
            print(f"自动填充参数出错：{str(e)}")

    def auto_fill_image_info(self):
        """自动填充图片信息"""
        if not self.image:
            return
        
        width, height = self.image.size
        name = os.path.splitext(os.path.basename(self.image_path))[0]
        
        # 填充输入框
        self.entries["texture_name"].delete(0, "end")
        self.entries["texture_name"].insert(0, name)
        
        self.entries["texture_width"].delete(0, "end")
        self.entries["texture_height"].delete(0, "end")
        self.entries["texture_width"].insert(0, str(width))
        self.entries["texture_height"].insert(0, str(height))
        
        # 如果是GIF，自动设置帧数
        frame_count = getattr(self.image, "n_frames", 1)
        self.entries["frame_count"].delete(0, "end")
        self.entries["frame_count"].insert(0, str(frame_count))

    def update_preview(self):
        """更新预览图片"""
        if not self.frames:
            return
            
        try:
            # 获取画布尺寸
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # 获取当前帧
            current_frame = self.frames[self.current_frame]
            
            # 计算缩放比例
            scale_x = canvas_width / current_frame.width
            scale_y = canvas_height / current_frame.height
            scale = min(scale_x, scale_y)
            
            # 计算新尺寸
            new_width = int(current_frame.width * scale)
            new_height = int(current_frame.height * scale)
            
            # 缩放图片
            resized = current_frame.resize(
                (new_width, new_height),
                Image.Resampling.NEAREST
            )
            
            # 创建 PhotoImage
            self.preview_photo = ImageTk.PhotoImage(resized)
            
            # 计算居中位置
            x = (canvas_width - new_width) // 2
            y = (canvas_height - new_height) // 2
            
            # 创建背景
            bg = self.create_checkerboard_background(canvas_width, canvas_height)
            
            # 更新显示
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(0, 0, anchor="nw", image=bg)
            self.preview_canvas.create_image(x, y, anchor="nw", image=self.preview_photo)
            
        except Exception as e:
            print(f"更新预览出错：{str(e)}")

    def draw_transparency_grid(self, x, y, width, height):
        """绘制透明背景网格
        
        Args:
            x (int): 网格起始x坐标
            y (int): 网格起始y坐标
            width (int): 网格总宽度
            height (int): 网格总高度
        """
        try:
            # 确保所有参数都是整数
            x = int(x)
            y = int(y)
            width = int(width)
            height = int(height)
            
            # 固定网格大小
            grid_size = 8
            
            # 计算网格范围
            rows = height // grid_size + 1
            cols = width // grid_size + 1
            
            # 创建网格
            for row in range(rows):
                for col in range(cols):
                    # 计算当前网格块的位置
                    grid_x = x + col * grid_size
                    grid_y = y + row * grid_size
                    
                    # 计算实际绘制的大小（处理边缘情况）
                    actual_width = min(grid_size, x + width - grid_x)
                    actual_height = min(grid_size, y + height - grid_y)
                    
                    if actual_width <= 0 or actual_height <= 0:
                        continue
                    
                    # 交替填充颜色
                    color = '#2b2b2b' if (row + col) % 2 == 0 else '#363636'
                    
                    # 绘制网格块
                    self.preview_canvas.create_rectangle(
                        grid_x, grid_y,
                        grid_x + actual_width,
                        grid_y + actual_height,
                        fill=color,
                        outline="",
                        tags="grid"
                    )
            
            # 将网格移到图片下方
            self.preview_canvas.tag_lower("grid")
            
        except Exception as e:
            print(f"绘制网格出错：{str(e)}")

    def generate_animation(self):
        """生成动画"""
        # 验证输入
        params = self.validate_inputs()
        if not params:
            return
        
        try:
            # 显示进度
            self.update_status("正在准备...", 0)
            
            # 1. 验证图片
            if not hasattr(self, 'image_path') or not self.image:
                raise ValueError("请先选择图片文件")
            
            self.update_status("正在处理图片...", 20)
            
            # 2. 创建输出目录
            models_dir = os.path.join(os.getcwd(), "models")
            os.makedirs(models_dir, exist_ok=True)
            
            # 创建模型专属文件夹
            model_dir = os.path.join(models_dir, params['texture_name'])
            os.makedirs(model_dir, exist_ok=True)
            
            # 3. 生成几何体
            self.update_status("正在生成几何体...", 40)
            geometry = self.generate_geometry(params)
            
            # 4. 生成动画
            self.update_status("正在生成动画...", 60)
            animation = AnimationGenerator.create_animation(
                params["frame_count"],
                params["animation_type"] == "圆形动画",
                frame_time=params["animation_speed"],
                loop=params["loop"]
            )
            
            # 5. 保存文件
            self.update_status("正在保存文件...", 80)
            
            # 保存几何体文件
            geometry_file = os.path.join(model_dir, f"{params['texture_name']}_geometry.json")
            with open(geometry_file, 'w', encoding='utf-8') as f:
                json.dump(geometry, f, indent=4, ensure_ascii=False)
            
            # 保存动画文件
            animation_file = os.path.join(model_dir, f"{params['texture_name']}_animation.json")
            with open(animation_file, 'w', encoding='utf-8') as f:
                json.dump(animation, f, indent=4, ensure_ascii=False)
            
            # 使用当前显示的图片（可能是编辑后的）来生成精灵图
            image_processor = ImageProcessor()
            output_image = os.path.join(model_dir, f"{params['texture_name']}.png")
            
            # 如果存在缓存的编辑后图片，使用它
            cache_dir = os.path.join(os.getcwd(), "cache")
            edited_image_path = os.path.join(cache_dir, f"edited_{os.path.basename(self.image_path)}")
            
            if os.path.exists(edited_image_path):
                source_image = edited_image_path
            else:
                source_image = self.image_path
            
            image_processor.process_image(
                source_image,
                output_image,
                params["frame_count"]
            )
            
            self.update_status("完成！", 100)
            
            # 显示成功消息
            CTkMessagebox(
                title="成功",
                message=f"动画已生成！\n文件保存在：{model_dir}",
                icon="check"
            )
            
            # 重置状态
            self.update_status("就绪")
            
        except Exception as e:
            self.update_status("生成失败")
            CTkMessagebox(
                title="错误",
                message=f"生成动画时出错：{str(e)}",
                icon="cancel"
            )

    def validate_inputs(self):
        """验证输入参数"""
        try:
            # 获取并验证输入
            texture_name = self.entries["texture_name"].get().strip()
            if not texture_name:
                raise ValueError("请输入名称")
            
            texture_width = int(self.entries["texture_width"].get())
            if texture_width <= 0:
                raise ValueError("宽度必须大于0")
            
            texture_height = int(self.entries["texture_height"].get())
            if texture_height <= 0:
                raise ValueError("高度必须大于0")
            
            frame_count = int(self.entries["frame_count"].get())
            if frame_count <= 0:
                raise ValueError("帧数必须大于0")
            
            animation_speed = float(self.entries["animation_speed"].get())
            if animation_speed <= 0:
                raise ValueError("动画速度必须大于0")
            
            # 如果是圆形动画，验证旋转角度
            if self.animation_type.get() == "圆形动画":
                rotation_angle = float(self.entries["rotation_angle"].get())
                if rotation_angle <= 0:
                    raise ValueError("旋转角度必须大于0")
            else:
                rotation_angle = 0
            
            return {
                "texture_name": texture_name,
                "texture_width": texture_width,
                "texture_height": texture_height,
                "frame_count": frame_count,
                "animation_type": self.animation_type.get(),
                "animation_speed": animation_speed,
                "loop": self.loop_var.get(),
                "rotation_angle": rotation_angle  # 添加旋转角度参数
            }
        except ValueError as e:
            CTkMessagebox(
                title="输入错误",
                message=str(e),
                icon="cancel"
            )
            return None

    def on_canvas_resize(self, event):
        """当画布大小改变时更新预览"""
        if hasattr(self, 'preview_photo'):
            self.update_preview()

    def update_status(self, message, progress=None):
        """更新状态和进度"""
        self.status_label.configure(text=message)
        if progress is not None:
            self.progress_bar.pack(fill="x", padx=5, pady=5)
            self.progress_bar.set(progress / 100)
        else:
            self.progress_bar.pack_forget()
        self.root.update()

    def on_window_resize(self, event):
        """处理窗口大小改变事件"""
        if event.widget == self.root:
            # 更新预览区域
            if hasattr(self, 'preview_canvas'):
                self.on_canvas_resize(event)
            
            # 确保左侧面板宽度固定
            self.left_panel.configure(width=350)

    def on_closing(self):
        """程序关闭时的处理"""
        # 清理缓存目录
        cache_dir = os.path.join(os.getcwd(), "cache")
        if os.path.exists(cache_dir):
            for file in os.listdir(cache_dir):
                try:
                    os.remove(os.path.join(cache_dir, file))
                except:
                    pass
            try:
                os.rmdir(cache_dir)
            except:
                pass
        
        # 关闭窗口
        self.root.destroy()

    def update_speed(self, event=None):
        """更新播放速度"""
        try:
            value = self.speed_entry.get()
            if not value:  # 如果输入框为空，不处理
                return
            
            # 获取用户输入的倍率
            speed_multiplier = float(value)
            if speed_multiplier <= 0:
                return  # 如果输入小于等于0，不处理
            
            # 计算实际延迟时间（基准延迟100ms）
            self.frame_delay = int(100 / speed_multiplier)
            
            # 如果正在播放，重新从第一帧开始播放
            if self.is_playing:
                if self.animation_after_id:
                    self.root.after_cancel(self.animation_after_id)
                # 重置到第一帧
                self.current_frame = 0
                self.image.seek(0)
                self.update_preview()
                self.frame_label.configure(text=f"帧: 1/{self.image.n_frames}")
                # 开始新的播放
                self.play_animation()
                
        except ValueError:
            pass  # 输入无效时不做处理，让用户继续输入

    @lru_cache(maxsize=32)
    def resize_frame(self, frame_array, new_size):
        """使用 numpy 进行快速缩放"""
        try:
            # 将输入转换为 numpy 数组（如果不是的话）
            if isinstance(frame_array, bytes):
                frame_array = np.frombuffer(frame_array, dtype=np.uint8)
            elif not isinstance(frame_array, np.ndarray):
                frame_array = np.array(frame_array)
            
            # 确保数组是正确的形状和类型
            if len(frame_array.shape) < 2:
                return None
            
            if frame_array.dtype != np.uint8:
                frame_array = frame_array.astype(np.uint8)
            
            # 确保尺寸是整数元组
            new_w, new_h = int(new_size[0]), int(new_size[1])
            
            # 使用 cv2.resize 进行缩放
            resized = cv2.resize(
                frame_array,
                (new_w, new_h),
                interpolation=cv2.INTER_NEAREST
            )
            
            return resized
        except Exception as e:
            print(f"缩放帧出错：{str(e)}")
            return None

    def start_preloading(self):
        """开始预加载帧"""
        if hasattr(self, 'frames'):
            self.preload_thread = threading.Thread(target=self._preload_frames, daemon=True)
            self.preload_thread.start()

    def stop_preloading(self):
        """停止预加载"""
        if self.preload_thread and self.preload_thread.is_alive():
            self.frame_queue.queue.clear()
            while not self.frame_queue.empty():
                try:
                    self.frame_queue.get_nowait()
                except queue.Empty:
                    break

    def _preload_frames(self):
        """预加载帧的后台线程"""
        while True:
            if not hasattr(self, 'frames') or not self.is_playing:
                break
                
            next_frame_idx = (self.current_frame + 1) % len(self.frames)
            if not self.frame_queue.full():
                # 获取下一帧的缩放版本
                frame = self.prepare_frame(next_frame_idx)
                try:
                    self.frame_queue.put(frame, timeout=0.1)
                except queue.Full:
                    continue

    def prepare_frame(self, frame_idx):
        """准备指定索引的帧"""
        try:
            if not self.current_size:
                # 获取画布尺寸
                canvas_width = self.preview_canvas.winfo_width()
                canvas_height = self.preview_canvas.winfo_height()
                
                if canvas_width <= 1 or canvas_height <= 1:
                    return None
                    
                # 计算缩放尺寸
                img_width, img_height = self.image.size
                scale_x = canvas_width / img_width
                scale_y = canvas_height / img_height
                scale = min(scale_x, scale_y)
                
                self.current_size = (
                    max(1, int(img_width * scale)),
                    max(1, int(img_height * scale))
                )
            
            cache_key = f"{frame_idx}_{self.current_size[0]}_{self.current_size[1]}"
            if cache_key in self.frame_cache:
                return self.frame_cache[cache_key]
            
            # 获取原始帧
            frame = self.frames[frame_idx]
            
            # 使用 SIMD 优化的缩放
            if isinstance(frame, np.ndarray):
                # 确保正确的数据类型和格式
                if frame.dtype != np.uint8:
                    frame = frame.astype(np.uint8)
                
                # 使用 cv2 进行快速缩放
                resized = cv2.resize(
                    frame,
                    (self.current_size[0], self.current_size[1]),
                    interpolation=cv2.INTER_NEAREST
                )
                
                # 确保正确的颜色格式
                if len(resized.shape) == 3:
                    if resized.shape[2] == 4:
                        resized = cv2.cvtColor(resized, cv2.COLOR_BGRA2RGBA)
                    elif resized.shape[2] == 3:
                        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
                
                img = Image.fromarray(resized)
            else:
                img = frame.resize(
                    self.current_size,
                    Image.Resampling.NEAREST
                )
            
            # 创建 PhotoImage
            photo = ImageTk.PhotoImage(img)
            
            # 缓存结果
            self.frame_cache[cache_key] = photo
            
            # 限制缓存大小
            if len(self.frame_cache) > 32:
                self.frame_cache.pop(next(iter(self.frame_cache)))
            
            return photo
            
        except Exception as e:
            print(f"准备帧出错：{str(e)}")
            return None

    def update_display(self):
        """更新显示"""
        if not hasattr(self, 'preview_photo'):
            return
            
        try:
            # 计算居中位置
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            x = (canvas_width - self.current_size[0]) // 2
            y = (canvas_height - self.current_size[1]) // 2
            
            # 创建背景
            bg = self.create_checkerboard_background(canvas_width, canvas_height)
            
            # 清除画布并显示图像
            self.preview_canvas.delete("all")
            self.preview_canvas.create_image(0, 0, anchor="nw", image=bg)
            self.preview_canvas.create_image(x, y, anchor="nw", image=self.preview_photo)
            
        except Exception as e:
            print(f"更新显示出错：{str(e)}")

    def create_checkerboard_background(self, width, height):
        """创建棋盘格背景"""
        cache_key = f"{width}_{height}"
        if cache_key in self.background_cache:
            return self.background_cache[cache_key]
            
        # 创建透明背景图像
        img = Image.new('RGB', (width, height), '#2b2b2b')
        draw = ImageDraw.Draw(img)
        
        # 绘制棋盘格
        cell_size = 8
        for y in range(0, height, cell_size):
            for x in range(0, width, cell_size):
                if (x // cell_size + y // cell_size) % 2 == 0:
                    draw.rectangle(
                        [x, y, x + cell_size, y + cell_size],
                        fill='#363636'
                    )
        
        # 缓存背景
        photo = ImageTk.PhotoImage(img)
        self.background_cache[cache_key] = photo
        return photo
