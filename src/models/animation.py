class AnimationGenerator:
    @staticmethod
    def create_animation(frame_count, animation_type="普通动画", frame_time=0.1, loop=False ,section_count=8):
        """生成动画数据
        Args:
            frame_count: 帧数
            animation_type: 动画类型 ("normal"/"circle"/"section")
            frame_time: 每帧的时间间隔（秒）
            loop: 是否循环播放
        """
        # 计算动画总时长
        total_time = (frame_count - 1) * frame_time

        animation_data = {
            "format_version": "1.8.0",
            "animations": {
                "idle": {
                    "loop": loop,
                    "animation_length": total_time,
                    "bones": {}
                }
            }
        }

        # 根据动画类型选择生成方法
        if animation_type == "普通动画":
            bones_data = AnimationGenerator._create_normal_animation(
                frame_count, frame_time, loop
            )
        elif animation_type == "圆形动画":
            bones_data = AnimationGenerator._create_circle_animation(
                frame_count, frame_time, loop
            )
        elif animation_type == "分段动画":
            bones_data = AnimationGenerator._create_section_animation(
                frame_count, frame_time, loop, section_count
            )
        else:
            raise ValueError(f"不支持的动画类型: {animation_type}")

        animation_data["animations"]["idle"]["bones"] = bones_data
        return animation_data

    @staticmethod
    def _create_normal_animation(frame_count, frame_time, loop):
        """生成普通动画的骨骼数据"""
        bones_data = {}
        
        for i in range(frame_count):
            bone_name = f"bone{i+1}"
            current_time = i * frame_time
            
            bone_data = {
                "scale": {
                    "0.0": {
                        "pre": [0, 0, 0],
                        "post": [0, 0, 0]
                    },
                    f"{current_time:.3f}": {
                        "pre": [0, 0, 0],
                        "post": [1, 1, 1]
                    }
                }
            }

            # 处理结束时间点
            if i < frame_count - 1:
                next_time = (i + 1) * frame_time
                bone_data["scale"][f"{next_time:.3f}"] = {
                    "pre": [1, 1, 1],
                    "post": [0, 0, 0]
                }
            elif loop:
                bone_data["scale"]["0.0"] = {
                    "pre": [1, 1, 1],
                    "post": [0, 0, 0]
                }

            bones_data[bone_name] = bone_data

        return bones_data

    @staticmethod
    def _create_circle_animation(frame_count, frame_time, loop):
        """生成圆形动画的骨骼数据"""
        bones_data = {}
        
        for i in range(frame_count):
            bone_name = f"bone{i+1}"
            current_time = i * frame_time
            
            # 圆形动画特殊处理：所有骨骼都需要旋转
            bone_data = {
                "scale": {
                    "0.0": {
                        "pre": [0, 0, 0],
                        "post": [0, 0, 0]
                    },
                    f"{current_time:.3f}": {
                        "pre": [0, 0, 0],
                        "post": [1, 1, 1]
                    }
                }
            }

            # 处理结束时间点
            if i < frame_count - 1:
                next_time = (i + 1) * frame_time
                bone_data["scale"][f"{next_time:.3f}"] = {
                    "pre": [1, 1, 1],
                    "post": [0, 0, 0]
                }
            elif loop:
                bone_data["scale"]["0.0"] = {
                    "pre": [1, 1, 1],
                    "post": [0, 0, 0]
                }

            bones_data[bone_name] = bone_data

        return bones_data

    @staticmethod
    def _create_section_animation(frame_count, frame_time, loop, section_count):
        """生成分段动画的骨骼数据
        Args:
            frame_count: 帧数
            frame_time: 每帧时间间隔
            loop: 是否循环
            section_count: 分段数量
        """
        bones_data = {}
        
        for i in range(frame_count):
            current_time = i * frame_time
            # 为每个分段创建动画
            for j in range(section_count):
                bone_name = f"bone{j+1}-{i+1}"
                
                bones_data[bone_name] = {
                    "scale": {
                        "0.0": {
                            "pre": [0, 0, 0],
                            "post": [0, 0, 0]
                        },
                        f"{current_time:.3f}": { 
                            "pre": [0, 0, 0],
                            "post": [1, 1, 1]
                        }
                    }
                }
                
                # 处理分段的结束时间点
                if i < frame_count - 1:
                    next_time = (i + 1) * frame_time
                    bones_data[bone_name]["scale"][f"{next_time:.3f}"] = {
                        "pre": [1, 1, 1],
                        "post": [0, 0, 0]
                    }
                elif loop:
                    bones_data[bone_name]["scale"]["0.0"] = {
                        "pre": [1, 1, 1],
                        "post": [0, 0, 0]
                    }

        return bones_data