import os
import sys
import site
import shutil
import zipfile
import importlib
import pkg_resources
from datetime import datetime
from pathlib import Path
import PyInstaller.__main__

class BuildUtils:
    def __init__(self, app_name="BlockBench动画生成器"):
        self.app_name = app_name
        self.project_root = Path(os.getcwd())
        self.build_dir = self.project_root / "build"
        self.dist_dir = self.project_root / "dist"
        self.history_dir = self.project_root / "history"
        
    def get_version(self):
        """获取版本号"""
        try:
            with open('version.txt', 'r') as f:
                return f.read().strip()
        except:
            return datetime.now().strftime('%Y%m%d_%H%M%S')
            
    def scan_project_imports(self):
        """扫描项目中使用的所有导入"""
        imports = set()
        hidden_imports = set()
        
        def process_file(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
            # 分析 import 语句
            lines = content.split('\n')
            for line in lines:
                line = line.strip()
                if line.startswith('import ') or line.startswith('from '):
                    # 移除注释
                    if '#' in line:
                        line = line[:line.index('#')]
                    
                    try:
                        # 提取模块名
                        if line.startswith('import '):
                            module = line[7:].strip().split(' ')[0]
                        else:  # from ... import ...
                            parts = line[5:].split('import')
                            if len(parts) < 2:
                                continue
                            module = parts[0].strip()
                        
                        # 跳过空模块名
                        if not module:
                            continue
                        
                        # 处理多重导入
                        if ',' in module:
                            modules = [m.strip() for m in module.split(',')]
                        else:
                            modules = [module]
                        
                        for module in modules:
                            # 移除相对导入
                            if module.startswith('.'):
                                continue
                            # 获取顶级模块
                            top_module = module.split('.')[0]
                            if top_module and top_module not in sys.modules:
                                try:
                                    importlib.import_module(top_module)
                                    imports.add(top_module)
                                except ImportError:
                                    pass
                    except Exception as e:
                        print(f"警告: 处理文件 {file_path} 中的导入语句时出错: {e}")
                        continue
        
        # 扫描所有 Python 文件
        for root, _, files in os.walk(self.project_root):
            for file in files:
                if file.endswith('.py'):
                    try:
                        process_file(Path(root) / file)
                    except Exception as e:
                        print(f"警告: 处理文件 {file} 时出错: {e}")
        
        # 添加特殊处理的模块
        special_modules = {
            'tkinterdnd2': {'tkdnd': self.find_tkdnd()},
            'PIL': {'_tkinter_finder'},
            'customtkinter': set(),
            'CTkMessagebox': set(),  # 添加这个模块
        }
        
        for module, extra_imports in special_modules.items():
            if module in imports:
                hidden_imports.update(extra_imports)
        
        return imports, hidden_imports
    
    def find_tkdnd(self):
        """查找 tkdnd 库文件路径"""
        for site_pkg in site.getsitepackages():
            tkdnd_path = Path(site_pkg) / 'tkinterdnd2' / 'tkdnd'
            if tkdnd_path.exists():
                return str(tkdnd_path)
        return None
        
    def collect_data_files(self):
        """收集需要包含的数据文件"""
        data_files = []
        
        # 添加 tkdnd
        tkdnd_path = self.find_tkdnd()
        if tkdnd_path:
            data_files.append((tkdnd_path, 'tkdnd'))
            
        return data_files
        
    def build(self):
        """构建可执行文件"""
        # 清理旧的构建文件
        for path in [self.build_dir, self.dist_dir]:
            if path.exists():
                shutil.rmtree(path)
        
        # 使用 spec 文件构建
        PyInstaller.__main__.run([
            'BlockBench动画生成器.spec',
            '--clean',
            '--noconfirm'
        ])
        
        # 处理历史版本
        version = self.get_version()
        versioned_dir = self.history_dir / f'{self.app_name}_v{version}'
        
        # 创建历史目录
        self.history_dir.mkdir(exist_ok=True)
        if versioned_dir.exists():
            shutil.rmtree(versioned_dir)
            
        # 复制构建结果
        shutil.copytree(
            self.dist_dir / self.app_name,
            versioned_dir
        )
        
        # 创建zip文件
        zip_path = f'{versioned_dir}.zip'
        if os.path.exists(zip_path):
            os.remove(zip_path)
            
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, _, files in os.walk(versioned_dir):
                for file in files:
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(versioned_dir.parent)
                    zipf.write(file_path, arcname)
                    
        print(f"构建完成！")
        print(f"程序文件夹: {versioned_dir}")
        print(f"压缩文件: {zip_path}") 