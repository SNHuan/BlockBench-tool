import os
import json
import shutil

class FileManager:
    @staticmethod
    def create_model_directory(base_dir, model_name):
        model_dir = os.path.join(base_dir, "models", model_name)
        os.makedirs(model_dir, exist_ok=True)
        return model_dir

    @staticmethod
    def save_model_files(model_dir, model_name, geometry_script, animation_script):
        geometry_path = os.path.join(model_dir, f"{model_name}.json")
        with open(geometry_path, "w") as f:
            json.dump(geometry_script, f, indent=4)

        animation_path = os.path.join(model_dir, f"{model_name}anim.json")
        with open(animation_path, "w") as f:
            json.dump(animation_script, f, indent=4)

    @staticmethod
    def copy_texture(source_path, target_dir, target_name=None):
        if target_name is None:
            target_name = os.path.basename(source_path)
        target_path = os.path.join(target_dir, target_name)
        shutil.copy2(source_path, target_path)
        return target_path
