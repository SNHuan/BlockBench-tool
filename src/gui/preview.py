import customtkinter as ctk
from PIL import Image, ImageTk, ImageEnhance, ImageOps
import os
from CTkMessagebox import CTkMessagebox
import numpy as np
import colorsys

class ImageEditorWindow:
    def __init__(self, parent, image_path, on_image_changed=None):
        self.window = ctk.CTkToplevel(parent)
        self.window.title("图像编辑器")
        self.window.minsize(500, 400)
        
        # 保存回调函数
        self.on_image_changed = on_image_changed
        
        # 创建缓存目录
        self.cache_dir = os.path.join(os.getcwd(), "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # 保存原始图片和路径
        self.image_path = image_path
        self.original_image = Image.open(image_path)
        self.image = self.original_image.copy()
        self.current_frame = 0
        self.is_playing = False
        self.frame_delay = 100
        self.hue_shift = 0
        self.zoom_level = 1
        self.brightness = 1.0  # 初始化亮度
        self.contrast = 1.0  # 初始化对比度
        
        # 初始化播放相关属性
        self.current_frame = 0
        self.is_playing = False
        self.frame_delay = 100
        self.animation_after_id = None
        
        # 创建主框架
        main_frame = ctk.CTkFrame(self.window)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        # 创建工具栏
        toolbar = ctk.CTkFrame(main_frame)
        toolbar.pack(fill="x", pady=(0, 10))
        
        # 缩放控制
        self.zoom_frame = ctk.CTkFrame(toolbar)  # 确保 zoom_frame 被定义
        self.zoom_frame.pack(side="left", padx=5)
        
        ctk.CTkLabel(self.zoom_frame, text="缩放:").pack(side="left", padx=5)
        for zoom in [1, 2, 4, 8]:
            btn = ctk.CTkButton(
                self.zoom_frame,
                text=f"{zoom}x",
                width=40,
                command=lambda z=zoom: self.set_zoom(z)
            )
            btn.pack(side="left", padx=2)
        
        # 图片信息显示
        self.info_label = ctk.CTkLabel(toolbar, text="")
        self.info_label.pack(side="right", padx=10)
        
        # 创建预览区域（带滚动条）
        preview_frame = ctk.CTkFrame(main_frame)
        preview_frame.pack(fill="both", expand=True)
        
        # 添加滚动条
        self.h_scroll = ctk.CTkScrollbar(preview_frame, orientation="horizontal")
        self.h_scroll.pack(side="bottom", fill="x")
        
        self.v_scroll = ctk.CTkScrollbar(preview_frame, orientation="vertical")
        self.v_scroll.pack(side="right", fill="y")
        
        # 创建预览画布
        self.canvas = ctk.CTkCanvas(
            preview_frame,
            bg='gray90',
            highlightthickness=0,
            xscrollcommand=self.h_scroll.set,
            yscrollcommand=self.v_scroll.set
        )
        self.canvas.pack(fill="both", expand=True)
        
        # 配置滚动条
        self.h_scroll.configure(command=self.canvas.xview)
        self.v_scroll.configure(command=self.canvas.yview)
        
        # 创建控制栏
        control_frame = ctk.CTkFrame(main_frame)
        control_frame.pack(fill="x", pady=(10, 0))
        
        # 左侧控制区
        left_controls = ctk.CTkFrame(control_frame)
        left_controls.pack(side="left", fill="x", expand=True)
        
        # 添加播放控制区域（如果是GIF）
        if hasattr(self.image, "n_frames"):
            play_frame = ctk.CTkFrame(left_controls)
            play_frame.pack(side="left", padx=5)
            
            # 播放控制按钮
            self.play_btn = ctk.CTkButton(
                play_frame,
                text="播放",
                width=60,
                command=self.toggle_play,
                fg_color='#1f538d',
                hover_color='#1a4578'
            )
            self.play_btn.pack(side="left", padx=2)
            
            # 帧控制按钮
            self.prev_btn = ctk.CTkButton(
                play_frame,
                text="◀",
                width=30,
                command=self.prev_frame,
                fg_color='#1f538d',
                hover_color='#1a4578'
            )
            self.prev_btn.pack(side="left", padx=2)
            
            self.next_btn = ctk.CTkButton(
                play_frame,
                text="▶",
                width=30,
                command=self.next_frame,
                fg_color='#1f538d',
                hover_color='#1a4578'
            )
            self.next_btn.pack(side="left", padx=2)
            
            # 帧计数器
            self.frame_label = ctk.CTkLabel(
                play_frame,
                text=f"帧: 1/{self.image.n_frames}"
            )
            self.frame_label.pack(side="left", padx=5)
            
            # 播放速度控制
            speed_frame = ctk.CTkFrame(play_frame)
            speed_frame.pack(side="left", padx=5)
            
            ctk.CTkLabel(speed_frame, text="速度:").pack(side="left")
            self.speed_entry = ctk.CTkEntry(speed_frame, width=50)
            self.speed_entry.insert(0, "1.0")
            self.speed_entry.pack(side="left", padx=2)
            ctk.CTkLabel(speed_frame, text="x").pack(side="left")
            
            # 绑定速度输入框的回车事件
            self.speed_entry.bind('<Return>', self.update_speed)
            self.speed_entry.bind('<FocusOut>', self.update_speed)
        
        # 编辑控制
        edit_frame = ctk.CTkFrame(left_controls)
        edit_frame.pack(side="left", padx=5)
        
        # 亮度调整
        ctk.CTkLabel(edit_frame, text="亮度:").pack(side="left", padx=5)
        self.brightness_slider = ctk.CTkSlider(
            edit_frame,
            from_=0.5,
            to=2.0,
            width=100,
            command=self.update_brightness
        )
        self.brightness_slider.pack(side="left", padx=5)
        self.brightness_slider.set(1.0)
        
        # 对比度调整
        ctk.CTkLabel(edit_frame, text="对比度:").pack(side="left", padx=5)
        self.contrast_slider = ctk.CTkSlider(
            edit_frame,
            from_=0.5,
            to=2.0,
            width=100,
            command=self.update_contrast
        )
        self.contrast_slider.pack(side="left", padx=5)
        self.contrast_slider.set(1.0)
        
        # 色相调整
        ctk.CTkLabel(edit_frame, text="色相:").pack(side="left", padx=5)
        self.hue_slider = ctk.CTkSlider(
            edit_frame,
            from_=0,
            to=360,
            width=100,
            command=self.update_hue
        )
        self.hue_slider.pack(side="left", padx=5)
        self.hue_slider.set(0)
        
        # 右侧控制区
        right_controls = ctk.CTkFrame(control_frame)
        right_controls.pack(side="right", fill="x", padx=10)
        
        self.apply_btn = ctk.CTkButton(
            right_controls,
            text="应用",
            width=60,
            command=self.apply_changes
        )
        self.apply_btn.pack(side="left", padx=5)
        
        # 重置按钮
        self.reset_btn = ctk.CTkButton(
            right_controls,
            text="重置",
            width=60,
            command=self.reset_changes
        )
        self.reset_btn.pack(side="left", padx=5)
        
        # 绑定事件
        self.canvas.bind('<Configure>', self.on_canvas_resize)
        self.canvas.bind('<ButtonPress-1>', self.start_pan)
        self.canvas.bind('<B1-Motion>', self.pan)
        self.canvas.bind('<MouseWheel>', self.zoom_wheel)
        
        # 初始显示
        self.update_preview()
        self.update_info()
        
        # 初始化帧计数器
        if hasattr(self.image, "n_frames"):
            self.frame_label.configure(text=f"帧: 1/{self.image.n_frames}")
        
        # 设置初始缩放按钮状态
        self.update_zoom_buttons()
        
        # 绑定窗口关闭事件
        self.window.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        self.window.lift()
        self.window.focus_force()
        
        # 初始化播放状态
        self.is_playing = False
        self.animation_after_id = None

    def set_zoom(self, level):
        """设置缩放级别"""
        self.zoom_level = level
        self.update_preview()
        self.update_info()
        self.update_zoom_buttons()
        self.update_scrollregion()

    def start_pan(self, event):
        """开始平移"""
        self.canvas.scan_mark(event.x, event.y)

    def pan(self, event):
        """平移画布"""
        self.canvas.scan_dragto(event.x, event.y, gain=1)

    def zoom_wheel(self, event):
        """鼠标滚轮缩放"""
        if event.delta > 0 and self.zoom_level < 16:
            self.zoom_level = int(self.zoom_level * 2)
        elif event.delta < 0 and self.zoom_level > 1:
            self.zoom_level = int(self.zoom_level / 2)
        self.update_preview()
        self.update_info()

    def update_info(self):
        """更新图片信息显示"""
        if self.image:
            width, height = self.image.size
            frame_info = f" 帧:{self.current_frame + 1}/{self.image.n_frames}" if hasattr(self.image, "n_frames") else ""
            self.info_label.configure(
                text=f"{width}x{height} ({self.zoom_level}x){frame_info}"
            )

    def reset_changes(self):
        """重置所有更改"""
        try:
            # 重置所有编辑参数
            self.hue_shift = 0
            self.brightness = 1.0
            self.contrast = 1.0
            
            # 重置所有滑块
            self.hue_slider.set(0)
            self.brightness_slider.set(1.0)
            self.contrast_slider.set(1.0)
            
            # 重置图像
            self.image = self.original_image.copy()
            self.current_frame = 0
            
            # 如果是GIF，重置到第一帧
            if hasattr(self.image, "n_frames"):
                self.image.seek(0)
                
                # 如果正在播放，停止播放
                if self.is_playing:
                    self.toggle_play()
            
            # 更新预览
            self.update_preview()
            self.update_info()
            
            # 通知主界面恢复原图
            if self.on_image_changed:
                self.on_image_changed(self.image_path)
            
        except Exception as e:
            print(f"重置出错：{str(e)}")

    def update_brightness(self, value):
        """更新亮度"""
        self.brightness = float(value)
        self.update_preview()

    def update_contrast(self, value):
        """更新对比度"""
        self.contrast = float(value)
        self.update_preview()

    def update_hue(self, value):
        """更新色相预览"""
        self.hue_shift = float(value)
        self.update_preview()

    def apply_changes(self):
        """应用色相变化"""
        try:
            cache_path = os.path.join(self.cache_dir, f"edited_{os.path.basename(self.image_path)}")
            
            # 如果是GIF，需要处理所有帧
            if hasattr(self.original_image, "n_frames"):
                # 保存当前帧
                current_frame_index = self.current_frame
                
                # 创建新的GIF
                frames = []
                durations = []
                
                # 获取原始GIF的调色板（如果有）
                palette = self.original_image.getpalette()
                
                # 处理每一帧
                for i in range(self.original_image.n_frames):
                    self.original_image.seek(i)
                    frame = self.original_image.copy()
                    # 应用编辑效果
                    edited_frame = self.adjust_image(frame)
                    # 如果原图有调色板，应用到编辑后的帧
                    if palette:
                        edited_frame.putpalette(palette)
                    frames.append(edited_frame)
                    # 保存每一帧的持续时间
                    durations.append(self.original_image.info.get('duration', 100))
                
                # 保存为新的GIF，保持原始GIF的属性
                try:
                    frames[0].save(
                        cache_path,
                        save_all=True,
                        append_images=frames[1:],
                        duration=durations,
                        loop=self.original_image.info.get('loop', 0),
                        format='GIF',
                        optimize=False,  # 禁用优化以保持质量
                        **{k: v for k, v in self.original_image.info.items() 
                           if k in {'transparency', 'background', 'version', 'disposal'}}
                    )
                except (TypeError, ValueError) as e:
                    # 如果带透明度保存失败，尝试不带透明度保存
                    frames[0].save(
                        cache_path,
                        save_all=True,
                        append_images=frames[1:],
                        duration=durations,
                        loop=self.original_image.info.get('loop', 0),
                        format='GIF',
                        optimize=False
                    )
                
                # 重新加载编辑后的GIF
                self.image = Image.open(cache_path)
                # 恢复到之前的帧
                self.image.seek(current_frame_index)
                
            else:
                # 静态图片直接应用编辑
                edited_image = self.adjust_image(self.original_image)
                edited_image.save(cache_path)
                self.image = edited_image
            
            # 更新预览
            self.update_preview()
            
            # 通知主界面更新
            if self.on_image_changed:
                self.on_image_changed(cache_path)
            
        except Exception as e:
            print(f"应用更改时出错：{str(e)}")
            CTkMessagebox(
                title="错误",
                message=f"应用更改失败：{str(e)}",
                icon="cancel"
            )

    def adjust_image(self, image):
        """调整图片的亮度、对比度和色相"""
        try:
            # 保存原始模式
            original_mode = image.mode
            
            # 保存透明通道（如果有）
            if original_mode == 'RGBA':
                r, g, b, a = image.split()
            elif original_mode == 'P':  # 处理调色板模式
                if 'transparency' in image.info:
                    # 转换为RGBA以保持透明度
                    image = image.convert('RGBA')
                    r, g, b, a = image.split()
                else:
                    # 如果没有透明度，转换为RGB
                    image = image.convert('RGB')
                    r, g, b = image.split()
                    a = None
            else:
                # 转换为RGB
                image = image.convert('RGB')
                r, g, b = image.split()
                a = None
            
            # 合并通道进行处理
            rgb_image = Image.merge('RGB', (r, g, b))
            
            # 调整亮度
            enhancer = ImageEnhance.Brightness(rgb_image)
            rgb_image = enhancer.enhance(self.brightness)
            
            # 调整对比度
            enhancer = ImageEnhance.Contrast(rgb_image)
            rgb_image = enhancer.enhance(self.contrast)
            
            # 调整色相
            if self.hue_shift != 0:
                rgb_image = self.adjust_hue_with_pillow(rgb_image, self.hue_shift)
            
            # 分离通道
            r, g, b = rgb_image.split()
            
            # 根据原始模式重建图像
            if a is not None:
                result = Image.merge('RGBA', (r, g, b, a))
                if original_mode == 'P':
                    # 如果原图是调色板模式，尝试转换回调色板模式
                    try:
                        result = result.convert('P', palette=Image.ADAPTIVE)
                    except:
                        pass  # 如果转换失败，保持RGBA模式
            else:
                result = Image.merge('RGB', (r, g, b))
                if original_mode == 'P':
                    # 如果原图是调色板模式，尝试转换回调色板模式
                    try:
                        result = result.convert('P', palette=Image.ADAPTIVE)
                    except:
                        pass  # 如果转换失败，保持RGB模式
            
            return result
            
        except Exception as e:
            print(f"调整图像出错：{str(e)}")
            return image

    def adjust_hue_with_pillow(self, image, hue_shift):
        """使用 Pillow 调整图片色相"""
        try:
            # 确保图像是 RGB 模式
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # 将色相偏移转换为 HSV 空间的调整
            img_array = np.array(image)
            
            # 转换为浮点数并归一化
            img_array = img_array.astype(np.float32) / 255.0
            
            # 转换为 HSV
            h, s, v = np.vectorize(colorsys.rgb_to_hsv)(
                img_array[..., 0],
                img_array[..., 1],
                img_array[..., 2]
            )
            
            # 调整色相
            h = (h + hue_shift / 360.0) % 1.0
            
            # 转换回 RGB
            r, g, b = np.vectorize(colorsys.hsv_to_rgb)(h, s, v)
            
            # 重新组合通道并转换回 uint8
            rgb_array = np.stack([r, g, b], axis=-1) * 255
            rgb_array = rgb_array.astype(np.uint8)
            
            # 转换回 PIL 图像
            return Image.fromarray(rgb_array, mode='RGB')
            
        except Exception as e:
            print(f"调整色相出错：{str(e)}")
            return image

    def on_canvas_resize(self, event):
        """当画布大小改变时更新预览"""
        if hasattr(self, 'preview_photo'):
            self.update_preview()

    def update_preview(self):
        """更新预览图片"""
        if not self.image:
            return
        
        try:
            # 获取当前帧
            current_frame = self.image
            if hasattr(self.image, "n_frames"):
                self.image.seek(self.current_frame)
                current_frame = self.image.copy()
            
            # 应用编辑效果
            current_image = self.adjust_image(current_frame)
            
            # 获取画布尺寸
            canvas_width = self.canvas.winfo_width()
            canvas_height = self.canvas.winfo_height()
            
            if canvas_width <= 1 or canvas_height <= 1:
                return
            
            # 计算缩放后的尺寸
            img_width, img_height = current_image.size
            new_width = int(img_width * self.zoom_level)
            new_height = int(img_height * self.zoom_level)
            
            # 计算居中位置
            x = int(max(0, (canvas_width - new_width) // 2))
            y = int(max(0, (canvas_height - new_height) // 2))
            
            # 缩放图像
            resized_image = current_image.resize(
                (new_width, new_height),
                Image.Resampling.NEAREST
            )
            
            # 更新预览
            self.preview_photo = ImageTk.PhotoImage(resized_image)
            self.canvas.delete("all")
            
            # 绘制透明背景网格
            self.draw_transparency_grid(x, y, new_width, new_height)
            
            # 显示图片
            self.canvas.create_image(
                x, y,
                anchor="nw",
                image=self.preview_photo
            )
            
            # 更新滚动区域
            self.update_scrollregion()
            
        except Exception as e:
            print(f"更新预览出错：{str(e)}")

    def draw_transparency_grid(self, x, y, width, height):
        """绘制透明背景网格"""
        grid_size = 8 * self.zoom_level  # 网格大小随缩放变化
        
        # 计算网格范围
        rows = height // grid_size + 1
        cols = width // grid_size + 1
        
        for row in range(rows):
            for col in range(cols):
                # 计算网格块的位置
                grid_x = x + col * grid_size
                grid_y = y + row * grid_size
                
                # 交替填充颜色
                color = '#2b2b2b' if (row + col) % 2 == 0 else '#363636'
                
                # 在图片下方绘制网格
                self.canvas.create_rectangle(
                    grid_x, grid_y,
                    grid_x + grid_size, grid_y + grid_size,
                    fill=color, outline="",
                    tags="grid"
                )
        
        # 将网格移到图片下方
        self.canvas.tag_lower("grid")

    def update_scrollregion(self):
        """更新滚动区域"""
        if not self.image:
            return
        
        # 计算图片缩放后的尺寸
        img_width, img_height = self.image.size
        new_width = int(img_width * self.zoom_level)
        new_height = int(img_height * self.zoom_level)
        
        # 获取画布尺寸
        canvas_width = self.canvas.winfo_width()
        canvas_height = self.canvas.winfo_height()
        
        # 计算滚动区域
        scroll_width = max(new_width, canvas_width)
        scroll_height = max(new_height, canvas_height)
        
        # 设置滚动区域
        self.canvas.configure(scrollregion=(0, 0, scroll_width, scroll_height))

    def update_zoom_buttons(self):
        """更新缩放按钮状态"""
        # 遍历所有缩放按钮
        for child in self.zoom_frame.winfo_children():
            if isinstance(child, ctk.CTkButton):
                # 从按钮文本中获取缩放级别
                try:
                    zoom = int(child.cget("text").replace("x", ""))
                    # 设置当前缩放级别按钮的颜色
                    if zoom == self.zoom_level:
                        child.configure(
                            fg_color="#1a4578",  # 深蓝色
                            hover_color="#153a66"  # 更深的蓝色
                        )
                    else:
                        child.configure(
                            fg_color="#1f538d",  # 正常蓝色
                            hover_color="#1a4578"  # 深蓝色
                        )
                except ValueError:
                    continue

    def on_closing(self):
        """窗口关闭时的处理"""
        try:
            # 如果正在播放，停止播放
            if self.is_playing:
                self.toggle_play()
            
            # 清理缓存文件
            if os.path.exists(self.cache_dir):
                for file in os.listdir(self.cache_dir):
                    try:
                        os.remove(os.path.join(self.cache_dir, file))
                    except:
                        pass
            
            # 销毁窗口
            self.window.destroy()
        except Exception as e:
            print(f"关闭窗口时出错：{str(e)}")
            self.window.destroy()