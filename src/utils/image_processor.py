import os
from PIL import Image

class ImageProcessor:
    @staticmethod
    def convert_gif_to_spritesheet(gif_path):
        gif = Image.open(gif_path)
        
        frames = []
        try:
            while True:
                gif.seek(len(frames))
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
        
        output_path = os.path.splitext(gif_path)[0] + ".png"
        spritesheet.save(output_path, "PNG")
        return output_path, spritesheet

    @staticmethod
    def calculate_frame_count(image):
        if getattr(image, "is_animated", False):
            return image.n_frames
        width, height = image.size
        return round(width / height)
