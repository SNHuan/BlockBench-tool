class Settings:
    # 默认配置
    DEFAULT_CONFIG = {
        "max_frames": 32,          # 最大帧数
        "min_frame_interval": 0.05,  # 最小帧间隔（秒）
        "max_frame_interval": 1.0,   # 最大帧间隔（秒）
        "max_pause_duration": 5.0,   # 最大暂停时间（秒）
        "fps": 10,                   # 默认帧速率
        "frame_time": 0.1,          # 默认帧时间（1/fps）
        "default_frame_size": {      # 默认帧大小
            "width": 32,
            "height": 32
        }
    } 