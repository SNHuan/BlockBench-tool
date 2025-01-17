import PyInstaller.__main__
import os
import shutil
import time
import sys

def clean_build():
    """清理构建文件夹"""
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            try:
                shutil.rmtree(dir_name)
            except PermissionError:
                print(f"请先关闭正在运行的程序，然后重试...")
                print("按回车键继续...")
                input()
                try:
                    shutil.rmtree(dir_name)
                except Exception as e:
                    print(f"清理失败，请手动删除 {dir_name} 文件夹后重试")
                    print(f"错误信息: {str(e)}")
                    exit(1)

def build_exe():
    """打包程序"""
    # 获取conda环境中的Python DLL文件路径
    if 'conda' in sys.version.lower():
        # 如果是conda环境，DLL在conda根目录
        python_dir = os.path.dirname(os.path.dirname(sys.executable))
    else:
        # 普通Python环境
        python_dir = os.path.dirname(sys.executable)
        
    python_dll = os.path.join(python_dir, 'python310.dll')
    
    if not os.path.exists(python_dll):
        print(f"警告: 找不到 python310.dll 在 {python_dll}")
        print("尝试不使用DLL继续构建...")
        dll_option = []
    else:
        dll_option = [f'--add-binary={python_dll};.']
    
    PyInstaller.__main__.run([
        'main.py',                        # 主程序文件
        '--name=BlockBench动画生成器',     # 程序名称
        '--windowed',                     # 使用 GUI 模式
        '--noconsole',                    # 不显示控制台
        '--add-data=src;src',             # 添加源代码
        '--clean',                        # 清理临时文件
        '--noconfirm',                    # 不确认覆盖
        '--onedir',                       # 生成文件夹模式
        # 添加必要的依赖
        '--hidden-import=PIL._tkinter_finder',
        '--hidden-import=customtkinter',
        '--hidden-import=CTkMessagebox',
        '--hidden-import=tkinter',
        '--hidden-import=tkinter.filedialog',
        '--hidden-import=PIL',
        '--hidden-import=PIL.Image',
        '--hidden-import=tkinterdnd2',    # 添加拖放支持
        # 添加运行时依赖
        '--hidden-import=_tkinter',
        '--hidden-import=tkinter.ttk',
        '--hidden-import=json',
        # 打包选项
        '--noupx',                        # 不使用UPX压缩
        '--collect-all=customtkinter',     # 收集所有customtkinter文件
        '--collect-all=CTkMessagebox',     # 收集所有CTkMessagebox文件
        '--collect-all=tkinterdnd2',      # 收集所有tkinterdnd2文件
        # 添加Python路径
        f'--paths={python_dir}',          # Python安装目录
        '--paths=.',                      # 当前目录
    ] + dll_option)  # 动态添加DLL选项

def post_build():
    """构建后处理"""
    dist_dir = os.path.join('dist', 'BlockBench动画生成器')
    
    # 创建models文件夹
    os.makedirs(os.path.join(dist_dir, 'models'), exist_ok=True)
    
    # 创建启动器
    launcher_content = """@echo off
chcp 65001 > nul
cd /d "%~dp0BlockBench动画生成器"
start "" "BlockBench动画生成器.exe"
"""
    
    with open('dist/启动.bat', 'w', encoding='utf-8') as f:
        f.write(launcher_content)
    
    # 复制README文件
    if os.path.exists('README.md'):
        shutil.copy2('README.md', dist_dir)

    print("构建完成！程序文件在:", dist_dir)
    print("请使用 启动.bat 运行程序")

if __name__ == '__main__':
    print("开始构建...")
    print("注意：请确保没有程序正在运行...")
    time.sleep(1)
    
    # 清理旧的构建文件
    clean_build()
    
    # 打包程序
    build_exe()
    
    # 构建后处理
    post_build() 