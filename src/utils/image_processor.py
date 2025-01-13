from PIL import Image

class ImageProcessor:
    def __init__(self):
        pass

    def process_image(self, source_path, output_path, frame_count):
        """处理图片并保存"""
        try:
            # 打开源图片
            img = Image.open(source_path)
            
            # 如果是GIF，转换为精灵图
            if getattr(img, "is_animated", False):
                return self.convert_gif_to_spritesheet(img, output_path)
            else:
                # 如果是普通图片，直接复制
                img.save(output_path, "PNG")
                return output_path, img
        except Exception as e:
            raise Exception(f"处理图片时出错：{str(e)}")

    def convert_gif_to_spritesheet(self, gif, output_path):
        """将GIF转换为精灵图"""
        frames = []
        try:
            for i in range(gif.n_frames):
                gif.seek(i)
                frames.append(gif.copy())
        except EOFError:
            pass
        
        frame_width = frames[0].width
        frame_height = frames[0].height
        spritesheet_width = frame_width * len(frames)
        spritesheet_height = frame_height
        
        spritesheet = Image.new('RGBA', (spritesheet_width, spritesheet_height), (0, 0, 0, 0))
        
        for i, frame in enumerate(frames):
            spritesheet.paste(frame, (i * frame_width, 0))
        
        spritesheet.save(output_path, "PNG")
        return output_path, spritesheet

    def calculate_frame_count(self, image):
        """计算帧数"""
        if getattr(image, "is_animated", False):
            return image.n_frames
        width, height = image.size
        return round(width / height) 