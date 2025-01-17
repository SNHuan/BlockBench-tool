class GeometryGenerator:
    @staticmethod
    def create_section_geometry(texture_width, texture_height, frame_count, section_count):
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
        
        origin = -8
        j = 0
        
        for i in range(section_count):
            bone = {
                "name": f"main{i+1}",
                "parent": f"main{i}",
                "pivot": [0, 0, 0]
            }
            origin = -8 + (16 / section_count) * i
            if i == 0:
                bone["parent"] = "main"
            geometry["minecraft:geometry"][0]["bones"].append(bone)
            for j in range(frame_count):
                bone1 = {
                    "name": f"bone{i+1}-{j+1}",
                    "parent": f"main{i+1}",
                    "pivot": [origin, 0, 0],
                    "cubes": [
                        {
                            "origin": [origin, -8, 0],
                            "size": [16/section_count, 16, 0],
                            "uv": {
                                "north": {"uv": [section_width * i + texture_width * j, 0], "uv_size": [section_width, texture_height]}
                            }
                        }
                    ]
                }
                geometry["minecraft:geometry"][0]["bones"].append(bone1)
            
        
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
