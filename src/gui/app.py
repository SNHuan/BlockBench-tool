# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
import os
from tkinterdnd2 import TkinterDnD, DND_FILES

from ..models.geometry import GeometryGenerator
from ..models.animation import AnimationGenerator
from ..utils.image_processor import ImageProcessor
from ..utils.file_manager import FileManager
from ..utils.config_manager import ConfigManager
from ..utils.logger import Logger
from ..utils.settings import Settings
from .components import InputField
from .progress_dialog import ProgressDialog
from .preview import PreviewWindow
from .batch_process import BatchProcessDialog

class AnimationGeneratorApp:
    def __init__(self):
        self.setup_window()
        self.setup_ui()
        self.image_path = None
        self.image = None
        
        # 绑定窗口大小改变事件
        self.preview_canvas.bind('<Configure>', self.on_canvas_resize)

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
        
        # 动画类型选择
        type_frame = ctk.CTkFrame(
            self.left_panel,
            fg_color='transparent'
        )
        type_frame.pack(fill="x", padx=15, pady=5)
        
        ctk.CTkLabel(
            type_frame,
            text="动画类型",
            font=ctk.CTkFont(size=14)
        ).pack(pady=(0, 5))
        
        self.animation_type = ctk.CTkSegmentedButton(
            type_frame,
            values=["普通动画", "圆形动画"],
            command=self.on_animation_type_change,
            selected_color='#1f538d',  # 更深的蓝色
            unselected_color='#2b2b2b'  # 深色背景
        )
        self.animation_type.pack(fill="x", padx=5, pady=(0, 5))
        self.animation_type.set("普通动画")
        
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

    def create_right_panel(self):
        # 预览区标题栏
        preview_header = ctk.CTkFrame(
            self.right_panel,
            fg_color='transparent',
            height=40
        )
        preview_header.pack(fill="x")
        preview_header.pack_propagate(False)
        
        ctk.CTkLabel(
            preview_header,
            text="预览",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(side="left", padx=15)
        
        self.preview_btn = ctk.CTkButton(
            preview_header,
            text="打开预览",
            width=100,
            command=self.show_preview,
            fg_color='#1f538d',
            hover_color='#1a4578'
        )
        self.preview_btn.pack(side="right", padx=15)
        
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
            highlightthickness=0  # 移除边框
        )
        self.preview_canvas.pack(fill="both", expand=True)

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
        if not self.image_path:
            CTkMessagebox(
                title="错误",
                message="请先选择图片文件",
                icon="cancel"
            )
            return
        PreviewWindow(self.root, self.image_path)

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
                params["rotation_angles"]
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
            ("帧数", "frame_count", "8")
        ]
        
        for label, key, default in params:
            frame = ctk.CTkFrame(input_group)
            frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(
                frame, text=label, width=50
            ).pack(side="left", padx=5)
            
            entry = ctk.CTkEntry(frame)
            entry.pack(side="right", fill="x", expand=True, padx=5)
            entry.insert(0, default)
            self.entries[key] = entry

    def on_animation_type_change(self, value):
        """动画类型改变时的回调"""
        if value == "圆形动画":
            # 显示旋转角度输入框
            if hasattr(self, 'rotation_frame'):
                self.rotation_frame.pack(fill="x", pady=2)
        else:
            # 隐藏旋转角度输入框
            if hasattr(self, 'rotation_frame'):
                self.rotation_frame.pack_forget()

    def upload_image(self):
        """上传图片"""
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
        """更新预览画布"""
        if not self.image_path:
            return
        
        try:
            # 加载图片
            img = Image.open(self.image_path)
            
            # 获取画布尺寸
            canvas_width = self.preview_canvas.winfo_width()
            canvas_height = self.preview_canvas.winfo_height()
            
            if canvas_width > 1 and canvas_height > 1:
                # 获取图片原始尺寸
                img_width, img_height = img.size
                
                # 计算合适的缩放比例
                width_ratio = canvas_width / img_width
                height_ratio = canvas_height / img_height
                scale = min(width_ratio, height_ratio) * 0.9  # 留出一些边距
                
                # 限制最大尺寸以避免卡顿
                MAX_DIMENSION = 1500  # 最大尺寸限制
                if img_width * scale > MAX_DIMENSION or img_height * scale > MAX_DIMENSION:
                    scale = min(MAX_DIMENSION / img_width, MAX_DIMENSION / img_height)
                
                # 计算缩放后的尺寸
                new_width = int(img_width * scale)
                new_height = int(img_height * scale)
                
                # 缩放图片
                img = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # 转换为PhotoImage
                self.preview_photo = ImageTk.PhotoImage(img)
                
                # 清除画布
                self.preview_canvas.delete("all")
                
                # 计算居中位置
                x = canvas_width // 2
                y = canvas_height // 2
                
                # 在画布中央显示图片
                self.preview_canvas.create_image(
                    x, y,
                    image=self.preview_photo,
                    anchor="center"
                )
                
                # 添加图片信息文本
                info_text = f"{img_width}x{img_height} ({int(scale * 100)}%)"
                self.preview_canvas.create_text(
                    10, 10,  # 左上角位置
                    text=info_text,
                    fill="#ffffff",
                    anchor="nw",
                    font=("Arial", 10)
                )
                
        except Exception as e:
            print(f"更新预览时出错：{str(e)}")

    def generate_animation(self):
        """生成动画"""
        # 验证输入
        params = self.validate_inputs()
        if not params:
            return
        
        try:
            # 显示进度对话框
            progress = ProgressDialog(self.root)
            progress.set_progress(0, "正在准备...")
            
            # 1. 验证图片
            if not self.image_path or not self.image:
                raise ValueError("请先选择图片文件")
            
            progress.set_progress(20, "正在处理图片...")
            
            # 2. 创建输出目录
            output_dir = os.path.join(os.path.dirname(self.image_path), "output")
            os.makedirs(output_dir, exist_ok=True)
            
            # 3. 生成几何体
            progress.set_progress(40, "正在生成几何体...")
            geometry = self.generate_geometry(params)
            
            # 4. 生成动画
            progress.set_progress(60, "正在生成动画...")
            animation = AnimationGenerator.create_animation(
                params["frame_count"],
                params["animation_type"] == "圆形动画"
            )
            
            # 5. 保存文件
            progress.set_progress(80, "正在保存文件...")
            
            # 保存几何体文件
            geometry_file = os.path.join(output_dir, f"{params['texture_name']}_geometry.json")
            with open(geometry_file, 'w', encoding='utf-8') as f:
                f.write(geometry)
            
            # 保存动画文件
            animation_file = os.path.join(output_dir, f"{params['texture_name']}_animation.json")
            with open(animation_file, 'w', encoding='utf-8') as f:
                f.write(animation)
            
            # 复制或处理图片
            image_processor = ImageProcessor()
            output_image = os.path.join(output_dir, f"{params['texture_name']}.png")
            image_processor.process_image(
                self.image_path,
                output_image,
                params["frame_count"]
            )
            
            progress.set_progress(100, "完成！")
            
            # 显示成功消息
            CTkMessagebox(
                title="成功",
                message=f"动画已生成！\n文件保存在：{output_dir}",
                icon="check"
            )
            
        except Exception as e:
            CTkMessagebox(
                title="错误",
                message=f"生成动画时出错：{str(e)}",
                icon="cancel"
            )
        finally:
            # 关闭进度对话框
            if progress:
                progress.destroy()

    def validate_inputs(self):
        """验证输入参数"""
        try:
            # ... 验证代码 ...
            return {
                "texture_name": self.entries["texture_name"].get().strip(),
                "texture_width": int(self.entries["texture_width"].get()),
                "texture_height": int(self.entries["texture_height"].get()),
                "frame_count": int(self.entries["frame_count"].get()),
                "animation_type": self.animation_type.get()
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
