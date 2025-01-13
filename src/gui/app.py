# -*- coding: utf-8 -*-
import customtkinter as ctk
from tkinter import filedialog
from PIL import Image
from CTkMessagebox import CTkMessagebox
import os

from ..models.geometry import GeometryGenerator
from ..models.animation import AnimationGenerator
from ..utils.image_processor import ImageProcessor
from ..utils.file_manager import FileManager
from .components import InputField

class AnimationGeneratorApp:
    def __init__(self):
        self.setup_window()
        self.setup_ui()
        self.image_path = None
        self.image = None

    def setup_window(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        self.root = ctk.CTk()
        self.root.title("BlockBench 工具")
        self.root.geometry("500x800")
        
        self.main_frame = ctk.CTkFrame(self.root)
        self.main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        self.title_label = ctk.CTkLabel(
            self.main_frame, 
            text="BlockBench 模型动画生成器",
            font=ctk.CTkFont(size=24, weight="bold")
        )
        self.title_label.pack(pady=20)

    def setup_ui(self):
        self.create_animation_type_section()
        self.create_upload_section()
        self.create_input_fields()
        
        # 添加循环选项复选框
        self.loop_var = ctk.BooleanVar(value=False)
        self.loop_checkbox = ctk.CTkCheckBox(
            self.main_frame,
            text="循环动画",
            variable=self.loop_var,
            font=ctk.CTkFont(size=14)
        )
        self.loop_checkbox.pack(padx=35, pady=5, anchor="w")
        
        self.generate_btn = ctk.CTkButton(
            self.main_frame,
            text="生成动画",
            command=self.generate_animation,
            font=ctk.CTkFont(size=16),
            height=40
        )
        self.generate_btn.pack(pady=20)

    def create_animation_type_section(self):
        type_frame = ctk.CTkFrame(self.main_frame)
        type_frame.pack(padx=20, pady=10, fill="x")
        
        type_label = ctk.CTkLabel(
            type_frame,
            text="动画类型:",
            font=ctk.CTkFont(size=14)
        )
        type_label.pack(side="left", padx=5)
        
        self.animation_type = ctk.CTkSegmentedButton(
            type_frame,
            values=["普通动画", "圆形动画"],
            command=self.on_animation_type_change
        )
        self.animation_type.pack(side="left", padx=5, fill="x", expand=True)
        self.animation_type.set("普通动画")

    def create_upload_section(self):
        upload_frame = ctk.CTkFrame(self.main_frame)
        upload_frame.pack(padx=20, pady=10, fill="x")
        
        self.upload_btn = ctk.CTkButton(
            upload_frame,
            text="上传图片",
            command=self.upload_image,
            font=ctk.CTkFont(size=14)
        )
        self.upload_btn.pack(side="left", padx=10, pady=10)
        
        self.file_label = ctk.CTkLabel(
            upload_frame,
            text="未选择文件",
            font=ctk.CTkFont(size=12)
        )
        self.file_label.pack(side="left", padx=10, fill="x", expand=True)

    def create_input_fields(self):
        input_frame = ctk.CTkFrame(self.main_frame)
        input_frame.pack(padx=20, pady=10, fill="both")
        
        self.entries = {}
        fields = [
            ("图片名称:", "texture_name", ""),
            ("图片宽度:", "texture_width", "32"),
            ("图片高度:", "texture_height", "32"),
            ("图片帧数:", "frame_count", "8"),
            ("暂停帧数(可选):", "pause_frame", "")
        ]

        # 创建基本输入字段
        for label_text, field_name, default_value in fields:
            field = InputField(input_frame, label_text, default_value)
            field.frame.pack(fill="x", padx=10, pady=5)
            self.entries[field_name] = field.entry
            
            # 为暂停帧数添加验证和回调
            if field_name == "pause_frame":
                self.entries[field_name].bind('<KeyRelease>', self.on_pause_frame_change)

        # 创建暂停秒数输入框（默认隐藏）
        self.pause_duration_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        pause_duration_field = InputField(
            self.pause_duration_frame, 
            "暂停秒数:", 
            "0"
        )
        pause_duration_field.frame.pack(fill="x", padx=10, pady=5)
        self.entries["pause_duration"] = pause_duration_field.entry

        # 创建旋转角度输入框（默认隐藏）
        self.rotation_angles_frame = ctk.CTkFrame(input_frame, fg_color="transparent")
        rotation_field = InputField(
            self.rotation_angles_frame, 
            "旋转角度:", 
            "45"
        )
        rotation_field.frame.pack(fill="x", padx=10, pady=5)
        self.entries["rotation_angles"] = rotation_field.entry

    def on_animation_type_change(self, value):
        if value in ["圆形动画", "方形动画", "六边形动画", "八边形动画"]:
            self.rotation_angles_frame.pack(fill="x", padx=10, pady=5)
        else:
            self.rotation_angles_frame.pack_forget()

    def upload_image(self):
        file_path = filedialog.askopenfilename(
            filetypes=[
                ("图片文件", "*.png;*.gif;*.jpg;*.jpeg"),
                ("所有文件", "*.*")
            ]
        )
        
        if file_path:
            try:
                # 验证文件扩展名
                ext = os.path.splitext(file_path)[1].lower()
                if ext not in ['.png', '.gif', '.jpg', '.jpeg']:
                    raise ValueError("不支持的文件格式。请使用 PNG、GIF 或 JPEG 格式的图片。")
                
                self.image_path = file_path
                self.image = Image.open(file_path)
                
                filename = os.path.basename(file_path)
                self.file_label.configure(text=filename)
                
                self.auto_fill_image_info()
                
            except Exception as e:
                CTkMessagebox(
                    title="错误",
                    message=f"无法加载图片：{str(e)}",
                    icon="cancel"
                )

    def auto_fill_image_info(self):
        if not self.image:
            return
        
        width, height = self.image.size
        name = os.path.splitext(os.path.basename(self.image_path))[0]
        
        self.entries["texture_name"].delete(0, "end")
        self.entries["texture_name"].insert(0, name)
        
        self.entries["texture_width"].delete(0, "end")
        self.entries["texture_height"].delete(0, "end")
        self.entries["texture_width"].insert(0, str(width))
        self.entries["texture_height"].insert(0, str(height))
        
        frame_count = ImageProcessor.calculate_frame_count(self.image)
        self.entries["frame_count"].delete(0, "end")
        self.entries["frame_count"].insert(0, str(frame_count))

    def validate_inputs(self):
        try:
            if not self.entries["texture_name"].get().strip():
                raise ValueError("请输入图片名称")
            
            try:
                texture_width = int(self.entries["texture_width"].get().strip())
                texture_height = int(self.entries["texture_height"].get().strip())
                frame_count = int(self.entries["frame_count"].get().strip())
                rotation_angles = int(self.entries["rotation_angles"].get().strip()) if self.animation_type.get() != "普通动画" else 0
            except ValueError:
                raise ValueError("请确保所有数值输入都是有效的整数")
            
            if texture_width <= 0 or texture_height <= 0:
                raise ValueError("图片尺寸必须大于0")
            if frame_count <= 0:
                raise ValueError("帧数必须大于0")
            if self.animation_type.get() != "普通动画" and (rotation_angles < 0 or rotation_angles > 360):
                raise ValueError("旋转角度必须在0到360度之间")
            
            pause_frame = None
            pause_duration = 0
            
            pause_frame_text = self.entries["pause_frame"].get().strip()
            if pause_frame_text:
                try:
                    pause_frame = int(pause_frame_text)
                    if pause_frame <= 0 or pause_frame > frame_count:
                        raise ValueError(f"暂停帧数必须在1到{frame_count}之间")
                except ValueError:
                    raise ValueError("暂停帧数必须是有效的整数")
                
                pause_duration_text = self.entries["pause_duration"].get().strip()
                if pause_duration_text:
                    try:
                        pause_duration = float(pause_duration_text)
                        if pause_duration < 0:
                            raise ValueError("暂停时间不能为负数")
                    except ValueError:
                        raise ValueError("暂停秒数必须是有效的数字")
            
            return {
                "texture_name": self.entries["texture_name"].get().strip(),
                "texture_width": texture_width,
                "texture_height": texture_height,
                "frame_count": frame_count,
                "rotation_angles": rotation_angles,
                "pause_frame": pause_frame,
                "pause_duration": pause_duration,
                "animation_type": self.animation_type.get(),
                "loop": self.loop_var.get()
            }
            
        except ValueError as e:
            CTkMessagebox(title="输入错误", message=str(e), icon="cancel")
            return None

    def generate_animation(self):
        params = self.validate_inputs()
        if not params:
            return
        
        try:
            script_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            model_dir = FileManager.create_model_directory(script_dir, params["texture_name"])

            # 处理图片
            if self.image_path and self.image_path.lower().endswith('.gif'):
                sprite_path = os.path.join(model_dir, f"{params['texture_name']}.png")
                sprite_image = ImageProcessor.convert_gif_to_spritesheet(self.image_path)[1]
                sprite_image.save(sprite_path)
                params["texture_width"] = sprite_image.width
                params["texture_height"] = sprite_image.height
                if getattr(self.image, "is_animated", False):
                    params["frame_count"] = self.image.n_frames
            elif self.image_path:
                FileManager.copy_texture(self.image_path, model_dir)
            
            # 生成几何脚本
            if params["animation_type"] == "圆形动画":
                geometry_script = GeometryGenerator.create_circle_geometry(
                    params["texture_width"],
                    params["texture_height"],
                    params["frame_count"],
                    params["rotation_angles"]
                )
            elif params["animation_type"] == "方形动画":
                geometry_script = GeometryGenerator.create_square_geometry(
                    params["texture_width"],
                    params["texture_height"],
                    params["frame_count"],
                    params["rotation_angles"]
                )
            elif params["animation_type"] == "六边形动画":
                geometry_script = GeometryGenerator.create_hexagon_geometry(
                    params["texture_width"],
                    params["texture_height"],
                    params["frame_count"],
                    params["rotation_angles"]
                )
            elif params["animation_type"] == "八边形动画":
                geometry_script = GeometryGenerator.create_octagon_geometry(
                    params["texture_width"],
                    params["texture_height"],
                    params["frame_count"],
                    params["rotation_angles"]
                )
            else:
                geometry_script = GeometryGenerator.create_normal_geometry(
                    params["texture_width"],
                    params["texture_height"],
                    params["frame_count"]
                )
            
            # 生成动画脚本
            animation_script = AnimationGenerator.create_animation(
                params["frame_count"],
                0.05,
                params["pause_frame"],
                params["pause_duration"],
                params["animation_type"].replace("动画", ""),
                params["loop"]
            )
            
            # 保存文件
            FileManager.save_model_files(model_dir, params["texture_name"], geometry_script, animation_script)
            
            success_message = f"动画文件已生成到文件夹：\n{model_dir}"
            if self.image_path and self.image_path.lower().endswith('.gif'):
                success_message += f"\n已生成精灵图：{params['texture_name']}.png"
            
            CTkMessagebox(
                title="成功", 
                message=success_message,
                icon="check"
            )
            
        except Exception as e:
            CTkMessagebox(
                title="错误",
                message=f"生成文件时出错：{str(e)}",
                icon="cancel"
            )

    def on_pause_frame_change(self, event):
        """当暂停帧数输入框的值改变时触发"""
        pause_frame_value = self.entries["pause_frame"].get().strip()
        if pause_frame_value:
            try:
                frame_count = int(self.entries["frame_count"].get().strip() or "0")
                pause_frame = int(pause_frame_value)
                if 0 < pause_frame <= frame_count:
                    self.pause_duration_frame.pack(fill="x", padx=10, pady=5)
                    return
            except ValueError:
                pass
        self.pause_duration_frame.pack_forget()

    def run(self):
        self.root.mainloop()
