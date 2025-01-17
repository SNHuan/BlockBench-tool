class GeometryGenerator:
    @staticmethod
    def create_section_geometry(texture_width, texture_height, frame_count, section_count, positions=None):
        """生成分段几何体
        Args:
            texture_width: 纹理宽度
            texture_height: 纹理高度
            frame_count: 帧数
            section_count: 分段数
            positions: 每个分段的Y轴偏移值（-1到1之间）
        """
        geometry = {
            "format_version": "1.12.0",
            "minecraft:geometry": [
                {
                    "description": {
                        "identifier": "geometry.section",
                        "texture_width": texture_width * frame_count,
                        "texture_height": texture_height,
                        "visible_bounds_width": 3,
                        "visible_bounds_height": 3,
                        "visible_bounds_offset": [0, 0.5, 0]
                    },
                    "bones": [
                        {
                            "name": "main",
                            "pivot": [0, 0, 0]
                        }
                    ]
                }
            ]
        }

        section_width = texture_width / section_count
        section_size = 16 / section_count  # 每个分段的实际大小

        # 创建分段骨骼
        for i in range(section_count):
            # 计算分段的基础位置
            section_x = -8 + (section_size * i)  # 从模型左边缘开始
            
            # 计算Y轴偏移（BlockBench坐标系：向上为正，向下为负）
            offset_y = 0
            if positions and i < len(positions):
                # 将-1到1的值映射到实际的像素偏移
                # 注意：保持原始正负值，因为已经符合BlockBench坐标系
                offset_y = positions[i] * 8  # 最大偏移为8个单位（128像素）
            
            # 创建主骨骼
            main_bone = {
                "name": f"main{i+1}",
                "parent": "main" if i == 0 else f"main{i}",
                "pivot": [section_x, offset_y, 0]  # 枢轴点在分段左侧中心
            }
            geometry["minecraft:geometry"][0]["bones"].append(main_bone)

            # 为每一帧创建显示骨骼
            for j in range(frame_count):
                display_bone = {
                    "name": f"bone{i+1}-{j+1}",
                    "parent": f"main{i+1}",
                    "pivot": [section_x, offset_y, 0],  # 继承父骨骼的枢轴点
                    "cubes": [
                        {
                            "origin": [section_x, -8, 0],  # 原点在左上角
                            "size": [section_size, 16, 0],
                            "uv": {
                                "north": {
                                    "uv": [section_width * i + texture_width * j, 0],
                                    "uv_size": [section_width, texture_height]
                                }
                            }
                        }
                    ]
                }
                geometry["minecraft:geometry"][0]["bones"].append(display_bone)

        return geometry
    @staticmethod
    def create_normal_geometry(texture_width, texture_height, frame_count):
        geometry = {
            "format_version": "1.12.0",
            "minecraft:geometry": [
                {
                    "description": {
                        "identifier": "geometry.normal",
                        "texture_width": texture_width * frame_count,
                        "texture_height": texture_height,
                        "visible_bounds_width": 3,
                        "visible_bounds_height": 3,
                        "visible_bounds_offset": [0, 0.5, 0]
                    },
                    "bones": [
                        {
                            "name": "main",
                            "pivot": [0, 0, 0]
                        }
                    ]
                }
            ]
        }


        
        for i in range(frame_count):
            bone = {
                "name": f"bone{i+1}",
                "parent": "main",
                "pivot": [0, 0, 0],
                "cubes": [
                    {
                        "origin": [-8, -8, 0],
                        "size": [16, 16, 0],
                        "uv": {
                            "north": {"uv": [texture_width * i, 0], "uv_size": [texture_width, texture_height]}
                        }
                    }
                ]
            }
            geometry["minecraft:geometry"][0]["bones"].append(bone)
        
        return geometry

    @staticmethod
    def create_circle_geometry(texture_width, texture_height, frame_count, rotation_angles):
        geometry = {
            "format_version": "1.12.0",
            "minecraft:geometry": [
                {
                    "description": {
                        "identifier": "geometry.circle",
                        "texture_width": texture_width * frame_count,
                        "texture_height": texture_height,
                        "visible_bounds_width": 3,
                        "visible_bounds_height": 3,
                        "visible_bounds_offset": [0, 0.5, 0]
                    },
                    "bones": [
                        {
                            "name": "main",
                            "pivot": [0, 0, 0]
                        }
                    ]
                }
            ]
        }
        
        
        for i in range(frame_count):
            bone = {
                "name": f"bone{i+1}",
                "parent": "main",
                "pivot": [0.00049, 0, -0.00016],
                "rotation": [-90, 0, 0],
                "cubes": [
                    {
                        "origin": [-35.2947, -22.25805, -15.37216],
                        "size": [26.0775, 0, 30.744],
                        "pivot": [-22.25595, -22.25805, -0.00016],
                        "rotation": [-(90 + rotation_angles), 0, -135],
                        "uv": {
                            "down": {"uv": [texture_width * i, 0], "uv_size": [texture_width, texture_height]}
                        }
                    },
                    {
                        "origin": [-13.03875, 31.47699, -15.37216],
                        "size": [26.0775, 0, 30.744],
                        "pivot": [0, 31.47699, -0.00016],
                        "rotation": [(90 - rotation_angles), 0, 0],
                        "uv": {
                            "up": {"uv": [texture_width * i, 0], "uv_size": [texture_width, texture_height]}
                        }
                    },
                    {
                        "origin": [9.21849, 22.25774, -15.37216],
                        "size": [26.0775, 0, 30.744],
                        "pivot": [22.25724, 22.25774, -0.00016],
                        "rotation": [(90 - rotation_angles), 0, 45],
                        "uv": {
                            "up": {"uv": [texture_width * i, 0], "uv_size": [texture_width, texture_height]}
                        }
                    },
                    {
                        "origin": [18.43775, 0.00049, -15.37216],
                        "size": [26.0775, 0, 30.744],
                        "pivot": [31.4765, 0.00049, -0.00016],
                        "rotation": [90 - rotation_angles, 0, 90],
                        "uv": {
                            "up": {"uv": [texture_width * i, 0], "uv_size": [texture_width, texture_height]}
                        }
                    },
                    {
                        "origin": [-44.51525, 0.00049, -15.37216],
                        "size": [26.0775, 0, 30.744],
                        "pivot": [-31.4765, 0.00049, -0.00016],
                        "rotation": [90 - rotation_angles, 0, -90],
                        "uv": {
                            "up": {"uv": [texture_width * i, 0], "uv_size": [texture_width, texture_height]}
                        }
                    },
                    {
                        "origin": [-35.29599, 22.25774, -15.37216],
                        "size": [26.0775, 0, 30.744],
                        "pivot": [-22.25724, 22.25774, -0.00016],
                        "rotation": [90 - rotation_angles, 0, -45],
                        "uv": {
                            "up": {"uv": [texture_width * i, 0], "uv_size": [texture_width, texture_height]}
                        }
                    },
                    {
                        "origin": [-13.03746, -31.4773, -15.37216],
                        "size": [26.0775, 0, 30.744],
                        "pivot": [0.00129, -31.4773, -0.00016],
                        "rotation": [-90 - rotation_angles, 0, 180],
                        "uv": {
                            "down": {"uv": [texture_width * i, 0], "uv_size": [texture_width, texture_height]}
                        }
                    },
                    {
                        "origin": [9.21978, -22.25805, -15.37216],
                        "size": [26.0775, 0, 30.744],
                        "pivot": [22.25853, -22.25805, -0.00016],
                        "rotation": [-90 - rotation_angles, 0, 135],
                        "uv": {
                            "down": {"uv": [texture_width * i, 0], "uv_size": [texture_width, texture_height]}
                        }
                    }
                ]
            }
            geometry["minecraft:geometry"][0]["bones"].append(bone)
        
        return geometry
