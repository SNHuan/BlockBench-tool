import json
import os

class ConfigManager:
    CONFIG_FILE = "config.json"
    
    @staticmethod
    def save_config(config_data):
        """保存配置到文件"""
        with open(ConfigManager.CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(config_data, f, indent=4, ensure_ascii=False)
    
    @staticmethod
    def load_config():
        """加载配置文件"""
        if not os.path.exists(ConfigManager.CONFIG_FILE):
            return {
                "last_directory": "",  # 上次打开的目录
                "default_settings": {
                    "texture_width": "32",
                    "texture_height": "32",
                    "frame_count": "8",
                    "rotation_angles": "45",
                    "animation_type": "普通动画",
                    "loop": False
                }
            }
        
        with open(ConfigManager.CONFIG_FILE, 'r', encoding='utf-8') as f:
            return json.load(f) 