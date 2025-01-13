class AnimationGenerator:
    @staticmethod
    def create_animation(frame_count, scale_interval, pause_frame=None, pause_duration=0, animation_type="circle", loop=False):
        # 计算总动画长度
        animation_length = frame_count * scale_interval  # 总长度包含所有帧
        if pause_frame and pause_duration:
            animation_length += pause_duration  # 加上暂停时间

        animation_data = {
            "format_version": "1.8.0",
            "animations": {
                "idle": {
                    "loop": loop,
                    "animation_length": animation_length,
                    "bones": {}
                }
            }
        }

        for i in range(frame_count):
            bone_name = f"{'quan' if animation_type == 'circle' else 'bone'}{i+1}"
            current_time = i * scale_interval
            
            # 计算下一帧时间，考虑暂停
            if pause_frame and i + 1 == pause_frame:
                # 如果是暂停帧，该帧的显示时间需要加上暂停时间
                next_time = current_time + scale_interval + pause_duration
            else:
                # 如果在暂停帧之后，时间点需要后移
                if pause_frame and i + 1 > pause_frame:
                    current_time += pause_duration
                next_time = current_time + scale_interval

            if loop:
                if i == 0:  # 第一帧
                    animation_data["animations"]["idle"]["bones"][bone_name] = {
                        "scale": {
                            "0.0": [1, 1, 1],  # 第一帧开始就显示
                            f"{next_time}": {"pre": [1, 1, 1], "post": [0, 0, 0]}  # 下一帧开始时隐藏
                        }
                    }
                elif i == frame_count - 1:  # 最后一帧
                    animation_data["animations"]["idle"]["bones"][bone_name] = {
                        "scale": {
                            "0.0": [0, 0, 0],  # 开始时隐藏
                            f"{current_time}": {"pre": [0, 0, 0], "post": [1, 1, 1]}  # 当前时间点显示
                        }
                    }
                else:  # 中间帧
                    animation_data["animations"]["idle"]["bones"][bone_name] = {
                        "scale": {
                            "0.0": [0, 0, 0],  # 开始时隐藏
                            f"{current_time}": {"pre": [0, 0, 0], "post": [1, 1, 1]},  # 当前时间点显示
                            f"{next_time}": {"pre": [1, 1, 1], "post": [0, 0, 0]}  # 下一帧开始时隐藏
                        }
                    }
            else:
                # 非循环动画
                animation_data["animations"]["idle"]["bones"][bone_name] = {
                    "scale": {
                        "0.0": [0, 0, 0],  # 开始时隐藏
                        f"{current_time}": {"pre": [0, 0, 0], "post": [1, 1, 1]},  # 当前时间点显示
                        f"{next_time}": {"pre": [1, 1, 1], "post": [0, 0, 0]}  # 下一帧开始时隐藏
                    }
                }

        return animation_data