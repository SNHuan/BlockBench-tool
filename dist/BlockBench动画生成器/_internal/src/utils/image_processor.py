from PIL import Image

class ImageProcessor:
    @staticmethod
    def process_image(source_path, output_path, frame_count):
        """处理图片并保存"""
        try:
            img = Image.open(source_path)
            
            # 如果是GIF，转换为精灵图
            if getattr(img, "is_animated", False):
                frames = []
                for i in range(img.n_frames):
                    img.seek(i)
                    frames.append(img.copy())
                
                # 创建精灵图
                frame_width = frames[0].width
                frame_height = frames[0].height
                spritesheet = Image.new('RGBA', (frame_width * len(frames), frame_height))
                
                for i, frame in enumerate(frames):
                    spritesheet.paste(frame, (i * frame_width, 0))
                
                spritesheet.save(output_path, "PNG")
                return output_path, spritesheet
            else:
                # 普通图片直接保存
                img.save(output_path, "PNG")
                return output_path, img
                
        except Exception as e:
            raise Exception(f"处理图片时出错：{str(e)}") 