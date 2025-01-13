class Settings:
    # 默认配置
    DEFAULT_CONFIG = {
        "max_frames": 32,          # 最大帧数
        "min_frame_interval": 0.05,  # 最小帧间隔（秒）
        "max_frame_interval": 1.0,   # 最大帧间隔（秒）
        "max_pause_duration": 5.0,   # 最大暂停时间（秒）
        "default_frame_size": {      # 默认帧大小
            "width": 32,
            "height": 32
        },
        "output_directory": "output",  # 输出目录
        "recent_files_limit": 5,       # 最近文件数量限制
        "supported_formats": [         # 支持的文件格式
            ".png",
            ".gif",
            ".jpg",
            ".jpeg"
        ]
    }
    
    @classmethod
    def validate_frame_count(cls, count):
        """验证帧数是否有效"""
        return 0 < count <= cls.DEFAULT_CONFIG["max_frames"]
    
    @classmethod
    def validate_frame_interval(cls, interval):
        """验证帧间隔是否有效"""
        return cls.DEFAULT_CONFIG["min_frame_interval"] <= interval <= cls.DEFAULT_CONFIG["max_frame_interval"]
    
    @classmethod
    def validate_pause_duration(cls, duration):
        """验证暂停时间是否有效"""
        return 0 <= duration <= cls.DEFAULT_CONFIG["max_pause_duration"] 