class AnimationGenerator:
    @staticmethod
    def create_animation(frame_count, is_circle=False, frame_time=0.1, loop=False):
        """生成动画数据
        Args:
            frame_count: 帧数
            is_circle: 是否为圆形动画
            frame_time: 每帧的时间间隔（秒）
            loop: 是否循环播放
        """
        # 计算动画总时长（最后一帧的时间）
        total_time = (frame_count - 1) * frame_time  # 因为第0秒就播放第一帧

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

        # 为每一帧创建骨骼动画
        for i in range(frame_count):
            bone_name = f"bone{i+1}"
            current_time = i * frame_time
            
            # 创建骨骼动画数据
            if i == 0:  # 第一帧特殊处理
                if loop:
                    # 循环模式：从开始就显示，到下一帧时隐藏
                    bone_data = {
                        "scale": {
                            "0.0": {
                                "pre": [1, 1, 1],
                                "post": [1, 1, 1]
                            },
                            f"{frame_time:.3f}": {
                                "pre": [1, 1, 1],
                                "post": [0, 0, 0]
                            }
                        }
                    }
                else:
                    # 非循环模式：从开始就显示，到下一帧时隐藏
                    bone_data = {
                        "scale": {
                            "0.0": {
                                "pre": [1, 1, 1],
                                "post": [1, 1, 1]
                            },
                            f"{frame_time:.3f}": {
                                "pre": [1, 1, 1],
                                "post": [0, 0, 0]
                            }
                        }
                    }
            else:
                # 其他帧：从当前时间显示，到下一帧时隐藏
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

                # 添加结束时间点
                if i < frame_count - 1:
                    # 非最后一帧，在下一帧开始前结束
                    next_time = (i + 1) * frame_time
                    bone_data["scale"][f"{next_time:.3f}"] = {
                        "pre": [1, 1, 1],
                        "post": [0, 0, 0]
                    }
                elif loop:
                    # 最后一帧且循环模式，连接到开始
                    bone_data["scale"]["0.0"] = {
                        "pre": [1, 1, 1],
                        "post": [0, 0, 0]
                    }

            # 添加到动画数据中
            animation_data["animations"]["idle"]["bones"][bone_name] = bone_data

        return animation_data