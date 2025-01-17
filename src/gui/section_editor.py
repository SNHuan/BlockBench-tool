import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk

class SectionEditorDialog:
    def __init__(self, parent, section_count=8, on_save=None, image_path=None, initial_positions=None):
        self.dialog = ctk.CTkToplevel(parent)
        self.dialog.title("分段动画编辑器")
        self.dialog.geometry("800x500")  # 增加宽度以容纳图片
        
        self.section_count = section_count
        self.on_save = on_save
        # 使用初始位置或创建新的位置列表
        self.section_positions = initial_positions.copy() if initial_positions else [0] * section_count
        
        # 加载参考图片
        self.image = None
        self.photo = None
        if image_path:
            try:
                self.image = Image.open(image_path)
            except Exception as e:
                print(f"加载参考图片失败：{e}")
        
        # 创建主布局
        self.create_layout()
        
        # 模态对话框
        self.dialog.transient(parent)
        self.dialog.grab_set()
    
    def create_layout(self):
        """创建主布局"""
        # 创建标题
        title_frame = ctk.CTkFrame(self.dialog)
        title_frame.pack(fill="x", padx=10, pady=5)
        
        ctk.CTkLabel(
            title_frame,
            text="分段位置调整",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=5)
        
        # 创建滑动条面板
        slider_frame = ctk.CTkFrame(self.dialog)
        slider_frame.pack(side="right", fill="y", padx=10, pady=5)
        
        # 创建预览画布
        canvas_frame = ctk.CTkFrame(self.dialog)
        canvas_frame.pack(side="left", fill="both", expand=True, padx=10, pady=5)
        
        self.canvas = ctk.CTkCanvas(
            canvas_frame,
            bg='#2b2b2b',
            highlightthickness=0
        )
        self.canvas.pack(fill="both", expand=True)
        self.canvas.bind('<Configure>', self.update_preview)
        
        # 创建滑动条
        self.create_sliders(slider_frame)
        
        # 创建按钮
        self.create_buttons(slider_frame)
    
    def create_sliders(self, frame):
        """创建滑动条区域"""
        # 滑动条容器
        sliders_container = ctk.CTkFrame(frame)
        sliders_container.pack(fill="both", expand=True, pady=5)
        
        # 创建滑动条
        self.sliders = []
        for i in range(self.section_count):
            slider_frame = ctk.CTkFrame(sliders_container)
            slider_frame.pack(fill="x", pady=2)
            
            # 标签
            label = ctk.CTkLabel(
                slider_frame,
                text=f"段 {i+1}",
                width=40
            )
            label.pack(side="left", padx=5)
            
            # 滑动条
            slider = ctk.CTkSlider(
                slider_frame,
                from_=-100,
                to=100,
                width=200,
                number_of_steps=100,
                command=lambda value, idx=i: self.on_slider_change(idx, value)
            )
            slider.pack(side="left", padx=5)
            
            # 数值输入框
            value_entry = ctk.CTkEntry(
                slider_frame,
                width=50,
                justify='center'
            )
            value_entry.pack(side="left", padx=5)
            value_entry.insert(0, "0")  # 设置初始值
            
            # 绑定输入框事件 - 使用 KeyRelease 事件实现实时更新
            value_entry.bind('<KeyRelease>', lambda e, idx=i: self.on_entry_change(idx))
            
            # 设置初始值
            initial_value = int(self.section_positions[i] * 100)  # 转换回界面值
            slider.set(initial_value)
            value_entry.delete(0, 'end')
            value_entry.insert(0, str(initial_value))
            
            self.sliders.append({
                'slider': slider,
                'value_entry': value_entry
            })
    
    def create_buttons(self, frame):
        """创建控制按钮"""
        btn_frame = ctk.CTkFrame(frame)
        btn_frame.pack(side="bottom", fill="x", padx=10, pady=10)
        
        # 重置按钮
        ctk.CTkButton(
            btn_frame,
            text="重置",
            command=self.reset_positions
        ).pack(side="left", padx=5)
        
        # 确定按钮
        ctk.CTkButton(
            btn_frame,
            text="确定",
            command=self.save_positions
        ).pack(side="right", padx=5)
        
    def on_slider_change(self, index, value):
        """滑动条值改变时的回调"""
        # 将界面值（-100到100）转换为实际偏移值（-1到1）
        self.section_positions[index] = float(value) / 100
        # 更新数值显示
        self.sliders[index]['value_entry'].delete(0, 'end')
        self.sliders[index]['value_entry'].insert(0, f"{int(value)}")
        self.update_preview()
        
    def update_preview(self, event=None):
        """更新预览"""
        if not hasattr(self, 'canvas'):
            return
            
        # 清除画布
        self.canvas.delete("all")
        
        # 获取画布尺寸
        width = self.canvas.winfo_width()
        height = self.canvas.winfo_height()
        
        # 如果有参考图片，先处理并绘制图片
        if self.image:
            # 计算每个分段的宽度（基于原图）
            img_width, img_height = self.image.size
            segment_width = img_width // self.section_count
            
            # 创建新图片用于显示
            display_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
            
            # 对每个分段进行处理
            for i in range(self.section_count):
                # 裁剪原图对应的分段
                segment = self.image.crop((
                    i * segment_width, 
                    0, 
                    (i + 1) * segment_width, 
                    img_height
                ))
                
                # 计算显示位置
                display_width = width // self.section_count
                display_x = i * display_width
                
                # 调整分段大小以适应显示区域
                segment = segment.resize((
                    display_width,
                    height
                ), Image.Resampling.LANCZOS)
                
                # 将分段粘贴到显示图片上
                display_img.paste(segment, (display_x, 0))
            
            # 更新显示
            self.photo = ImageTk.PhotoImage(display_img)
            self.canvas.create_image(
                0, 0,
                anchor="nw",
                image=self.photo
            )
        
        # 计算分段宽度
        section_width = width / self.section_count
        
        # 绘制中心参考线
        self.canvas.create_line(
            0, height/2,
            width, height/2,
            fill='#666666',
            dash=(4, 4)
        )
        
        # 绘制每个分段
        for i in range(self.section_count):
            x1 = i * section_width
            x2 = (i + 1) * section_width
            
            # 计算枢轴点位置
            pivot_x = x1  # 在分段左侧
            
            # 计算Y轴偏移
            # 将-1到1的值映射到画布坐标
            # BlockBench坐标系：向上为正，所以不需要取反
            canvas_scale = height / 16  # 画布高度对应16个单位
            offset_y = self.section_positions[i] * 8 * canvas_scale  # 最大偏移8个单位
            pivot_y = height/2 - offset_y  # 从中心线计算实际位置
            
            # 绘制分段边界
            self.canvas.create_line(
                x1, 0,
                x1, height,
                fill='#666666',
                dash=(4, 4)
            )
            
            # 绘制pivot线和点
            pivot_radius = 4
            # 垂直参考线
            self.canvas.create_line(
                pivot_x, 0,
                pivot_x, height,
                fill='#FF6B6B',
                width=1,
                dash=(4, 4)
            )
            # pivot点
            self.canvas.create_oval(
                pivot_x - pivot_radius, pivot_y - pivot_radius,
                pivot_x + pivot_radius, pivot_y + pivot_radius,
                fill='#FF6B6B',
                outline='#FF6B6B'
            )
            
            # 绘制分段编号
            self.canvas.create_text(
                pivot_x + section_width/2,
                20,  # 固定在顶部
                text=f"main{i+1}",
                fill='white',
                font=('Arial', 10, 'bold')
            )
        
        # 绘制最后一个分段的右边界
        self.canvas.create_line(
            width-1, 0,
            width-1, height,
            fill='#666666',
            dash=(4, 4)
        )
        
    def reset_positions(self):
        """重置所有位置"""
        for i, slider_data in enumerate(self.sliders):
            slider_data['slider'].set(0)
            slider_data['value_entry'].delete(0, 'end')
            slider_data['value_entry'].insert(0, "0")
            self.section_positions[i] = 0
        self.update_preview()
        
    def save_positions(self):
        """保存位置设置"""
        if self.on_save:
            self.on_save(self.section_positions)
        self.dialog.destroy() 

    def on_entry_change(self, index, event=None):
        """输入框值改变时的回调"""
        try:
            entry_text = self.sliders[index]['value_entry'].get()
            # 处理空字符串或只有负号的情况
            if not entry_text or entry_text == '-':
                return
            
            # 获取输入值
            value = int(entry_text)
            # 限制范围
            value = max(-100, min(100, value))
            
            # 如果值发生了变化，才更新
            current_value = int(self.section_positions[index] * 100)
            if value != current_value:
                # 更新界面
                self.sliders[index]['value_entry'].delete(0, 'end')
                self.sliders[index]['value_entry'].insert(0, str(value))
                self.sliders[index]['slider'].set(value)
                # 更新数据
                self.section_positions[index] = float(value) / 100
                self.update_preview()
            
        except ValueError:
            # 对于无效输入，不做处理，允许用户继续输入
            pass 