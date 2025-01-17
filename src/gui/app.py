# -*- coding: utf-8 -*-
import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
from CTkMessagebox import CTkMessagebox
import os
import json
import sys
from functools import lru_cache
from tkinterdnd2 import TkinterDnD, DND_FILES
from .section_editor import SectionEditorDialog

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
from src.utils.image_processor import ImageProcessor
from src.models.geometry import GeometryGenerator
from src.models.animation import AnimationGenerator

class AnimationGeneratorApp:
    def __init__(self):
        # 设置主题
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # 创建主窗口 - 使用TkinterDnD
        self.root = TkinterDnD.Tk()
        self.root.title("BlockBench 模型动画生成器")
        
        # 设置窗口最小尺寸
        self.root.minsize(800, 600)
        
        # 获取屏幕尺寸和计算窗口大小
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = min(int(screen_width * 0.7), 1000)
        window_height = min(int(screen_height * 0.7), 700)
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        # 设置窗口大小和位置
        self.root.geometry(f"{window_width}x{window_height}+{x}+{y}")
        
        # 创建主框架
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建左右分栏
        self.create_panels()
        
        # 创建界面元素
        self.create_left_panel()
        self.create_right_panel()
        
        # 简化图像相关属性
        self.image = None
        self.image_path = None
        self.preview_photo = None
        
        # 绑定窗口关闭事件
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # 添加分段位置存储
        self.section_positions = None
        
        # 添加分段数据持久化
        self.load_section_data()

    def create_panels(self):
        """创建左右面板"""
        self.left_panel = ctk.CTkFrame(self.main_frame, width=300)
        self.left_panel.pack(side="left", fill="y", padx=(0, 5))
        self.left_panel.pack_propagate(False)
        
        self.right_panel = ctk.CTkFrame(self.main_frame)
        self.right_panel.pack(side="right", fill="both", expand=True, padx=(5, 0))

    def create_left_panel(self):
        """创建左侧面板内容"""
        # 标题
        title = ctk.CTkLabel(
            self.left_panel,
            text="BlockBench\n模型动画生成器",
            font=ctk.CTkFont(size=20, weight="bold")
        )
        title.pack(pady=15)
        
        # 上传区域
        upload_frame = ctk.CTkFrame(self.left_panel)
        upload_frame.pack(fill="x", padx=15, pady=10)
        
        self.upload_btn = ctk.CTkButton(
            upload_frame,
            text="选择图片",
            command=self.upload_image
        )
        self.upload_btn.pack(fill="x", pady=5)
        
        # 文件标签支持拖放
        self.file_label = ctk.CTkLabel(
            upload_frame,
            text="请选择图片文件\n或拖拽文件到此处",
            wraplength=250
        )
        self.file_label.pack(pady=5)
        
        # 绑定拖放事件
        self.root.drop_target_register(DND_FILES)
        self.root.dnd_bind('<<Drop>>', self.on_drop)
        
        # 参数设置区
        self.create_parameter_inputs()
        
        # 生成按钮
        self.generate_btn = ctk.CTkButton(
            self.left_panel,
            text="生成动画",
            command=self.generate_animation,
            font=ctk.CTkFont(size=16, weight="bold")
        )
        self.generate_btn.pack(fill="x", padx=15, pady=20)
        
    def create_parameter_inputs(self):
        """创建参数输入区域"""
        settings_frame = ctk.CTkFrame(self.left_panel)
        settings_frame.pack(fill="x", padx=15, pady=10)
        
        # 基本参数
        params = [
            ("名称", "texture_name", ""),
            ("宽度", "texture_width", "32"),
            ("高度", "texture_height", "32"),
            ("帧数", "frame_count", "8"),
            ("帧间隔(秒)", "frame_time", "0.1")
        ]
        
        self.entries = {}
        for label, key, default in params:
            frame = ctk.CTkFrame(settings_frame)
            frame.pack(fill="x", pady=2)
            
            ctk.CTkLabel(frame, text=label).pack(side="left", padx=5)
            entry = ctk.CTkEntry(frame)
            entry.insert(0, default)
            entry.pack(side="right", fill="x", expand=True, padx=5)
            self.entries[key] = entry
        
        # 动画类型选择
        type_frame = ctk.CTkFrame(settings_frame)
        type_frame.pack(fill="x", pady=5)
        
        self.animation_type = ctk.CTkSegmentedButton(
            type_frame,
            values=["普通动画", "圆形动画", "分段动画"],
            command=self.on_animation_type_change
        )
        self.animation_type.pack(fill="x", padx=5, pady=5)
        self.animation_type.set("普通动画")
        
        # 旋转角度/分段数输入框（默认隐藏）
        self.rotation_frame = ctk.CTkFrame(settings_frame)
        self.rotation_label = ctk.CTkLabel(
            self.rotation_frame,
            text="旋转角度:"
        )
        self.rotation_label.pack(side="left", padx=5)
        
        self.entries["rotation_angle"] = ctk.CTkEntry(self.rotation_frame)
        self.entries["rotation_angle"].insert(0, "360")
        self.entries["rotation_angle"].pack(side="right", fill="x", expand=True, padx=5)
        
        # 分段编辑按钮（默认隐藏）
        self.section_frame = ctk.CTkFrame(settings_frame)
        self.section_btn = ctk.CTkButton(
            self.section_frame,
            text="编辑分段",
            command=self.edit_sections
        )
        self.section_btn.pack(fill="x", padx=5, pady=5)
        
        # 循环选项
        self.loop_var = tk.BooleanVar(value=False)
        self.loop_checkbox = ctk.CTkCheckBox(
            settings_frame,
            text="循环动画",
            variable=self.loop_var
        )
        self.loop_checkbox.pack(pady=5)

    def create_right_panel(self):
        """创建右侧预览区域"""
        # 预览标题
        ctk.CTkLabel(
            self.right_panel,
            text="预览",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(anchor="w", padx=15, pady=10)
        
        # 预览画布
        self.preview_canvas = ctk.CTkCanvas(
            self.right_panel,
            bg='#2b2b2b',
            highlightthickness=0
        )
        self.preview_canvas.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        
        # 绑定画布大小改变事件
        self.preview_canvas.bind('<Configure>', self.on_canvas_resize)

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
                
                # 更新文件名显示
                filename = os.path.basename(file_path)
                self.file_label.configure(text=filename)
                
                # 自动填充参数
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

    def on_animation_type_change(self, value):
        """动画类型改变时的回调"""
        if value == "圆形动画":
            self.rotation_label.configure(text="旋转角度:")
            self.entries["rotation_angle"].delete(0, "end")
            self.entries["rotation_angle"].insert(0, "360")
            self.rotation_frame.pack(fill="x", pady=2)
            self.section_frame.pack_forget()  # 隐藏分段编辑按钮
        elif value == "分段动画":
            self.rotation_label.configure(text="分段数量:")
            self.entries["rotation_angle"].delete(0, "end")
            self.entries["rotation_angle"].insert(0, "8")
            self.rotation_frame.pack(fill="x", pady=2)
            self.section_frame.pack(fill="x", pady=2)  # 显示分段编辑按钮
        else:
            self.rotation_frame.pack_forget()
            self.section_frame.pack_forget()

    def on_canvas_resize(self, event):
        """画布大小改变时的回调"""
        self.update_preview()

    def generate_animation(self):
        """生成动画"""
        try:
            # 获取参数
            params = {
                "texture_name": self.entries["texture_name"].get().strip(),
                "texture_width": int(self.entries["texture_width"].get()),
                "texture_height": int(self.entries["texture_height"].get()),
                "frame_count": int(self.entries["frame_count"].get()),
                "frame_time": float(self.entries["frame_time"].get()),
                "animation_type": self.animation_type.get(),
                "loop": self.loop_var.get()
            }
            
            # 验证参数
            if not params["texture_name"]:
                raise ValueError("请输入名称")
            if params["texture_width"] <= 0:
                raise ValueError("宽度必须大于0")
            if params["texture_height"] <= 0:
                raise ValueError("高度必须大于0")
            if params["frame_count"] <= 0:
                raise ValueError("帧数必须大于0")
            if params["frame_time"] <= 0:
                raise ValueError("帧间隔必须大于0")
            
            # 创建输出目录
            models_dir = os.path.join(os.getcwd(), "models")
            os.makedirs(models_dir, exist_ok=True)
            
            # 创建模型专属文件夹
            model_dir = os.path.join(models_dir, params["texture_name"])
            os.makedirs(model_dir, exist_ok=True)
            
            # 获取旋转角度或分段数
            section_count = 8  # 默认分段数
            if params["animation_type"] in ["圆形动画", "分段动画"]:
                try:
                    value = float(self.entries["rotation_angle"].get())
                    if value <= 0:
                        raise ValueError(
                            "旋转角度必须大于0" if params["animation_type"] == "圆形动画"
                            else "分段数必须大于0"
                        )
                    if params["animation_type"] == "分段动画":
                        if section_count <= 0:
                            raise ValueError("分段数必须大于0")
                        else:
                            section_count = int(value)
                except ValueError as e:
                    raise ValueError(
                        "请输入有效的旋转角度" if params["animation_type"] == "圆形动画"
                        else "请输入有效的分段数"
                    )
            
            # 生成几何体
            if params["animation_type"] == "普通动画":
                geometry = GeometryGenerator.create_normal_geometry(
                    params["texture_width"],
                    params["texture_height"],
                    params["frame_count"]
                )
            elif params["animation_type"] == "圆形动画":
                geometry = GeometryGenerator.create_circle_geometry(
                    params["texture_width"],
                    params["texture_height"],
                    params["frame_count"],
                    value  # 旋转角度
                )
            else:  # 分段动画
                geometry = GeometryGenerator.create_section_geometry(
                    params["texture_width"],
                    params["texture_height"],
                    params["frame_count"],
                    section_count,  # 分段数
                    positions=self.section_positions  # 传递枢轴点位置
                )
            
            # 生成动画
            animation = AnimationGenerator.create_animation(
                params["frame_count"],
                animation_type=params["animation_type"],  # 转换为英文
                frame_time=params["frame_time"],
                loop=params["loop"],
                section_count=section_count,
            )
            
            # 保存几何体文件
            geometry_file = os.path.join(model_dir, f"{params['texture_name']}_geometry.json")
            with open(geometry_file, 'w', encoding='utf-8') as f:
                json.dump(geometry, f, indent=4, ensure_ascii=False)
            
            # 保存动画文件
            animation_file = os.path.join(model_dir, f"{params['texture_name']}_animation.json")
            with open(animation_file, 'w', encoding='utf-8') as f:
                json.dump(animation, f, indent=4, ensure_ascii=False)
            
            # 处理图片
            if self.image_path:
                output_image = os.path.join(model_dir, f"{params['texture_name']}.png")
                ImageProcessor.process_image(
                    self.image_path,
                    output_image,
                    params["frame_count"]
                )
            
            CTkMessagebox(
                title="成功", 
                message=f"动画已生成！\n文件保存在：{model_dir}",
                icon="check"
            )
            
        except Exception as e:
            CTkMessagebox(
                title="错误",
                message=str(e),
                icon="cancel"
            )

    def on_closing(self):
        """窗口关闭时的处理"""
        self.root.destroy()

    def on_drop(self, event):
        """处理文件拖放"""
        file_path = event.data
        # 去除花括号（如果有）
        if file_path.startswith('{') and file_path.endswith('}'):
            file_path = file_path[1:-1]
        
        # 检查文件类型
        if file_path.lower().endswith(('.png', '.gif', '.jpg', '.jpeg')):
            try:
                self.image_path = file_path
                self.image = Image.open(file_path)
                
                # 更新文件名显示
                filename = os.path.basename(file_path)
                self.file_label.configure(text=filename)
                
                # 自动填充参数
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
                message="请拖入图片文件 (PNG/GIF/JPG)",
                icon="cancel"
            )

    def load_section_data(self):
        """加载分段数据"""
        try:
            data_file = os.path.join(os.getcwd(), "section_data.json")
            if os.path.exists(data_file):
                with open(data_file, 'r') as f:
                    data = json.load(f)
                    self.section_positions = data.get('positions')
        except Exception as e:
            print(f"加载分段数据失败：{e}")
    
    def save_section_data(self):
        """保存分段数据"""
        try:
            data_file = os.path.join(os.getcwd(), "section_data.json")
            with open(data_file, 'w') as f:
                json.dump({
                    'positions': self.section_positions
                }, f)
        except Exception as e:
            print(f"保存分段数据失败：{e}")
    
    def edit_sections(self):
        """打开分段编辑器"""
        try:
            section_count = int(self.entries["rotation_angle"].get())
            if section_count <= 0:
                raise ValueError("分段数必须大于0")
            
            # 如果存在之前的位置数据且长度匹配，使用它；否则创建新的
            if self.section_positions and len(self.section_positions) == section_count:
                initial_positions = self.section_positions
            else:
                initial_positions = [0] * section_count
            
            def on_save(positions):
                self.section_positions = positions
                self.save_section_data()  # 保存到文件
            
            editor = SectionEditorDialog(
                self.root,
                section_count=section_count,
                on_save=on_save,
                image_path=self.image_path,
                initial_positions=initial_positions  # 传入初始位置
            )
            
        except ValueError as e:
            CTkMessagebox(
                title="错误",
                message=str(e),
                icon="cancel"
            )
