#!/usr/bin/env python3
"""
正确构建包的脚本
"""
import os
import subprocess
import sys
import shutil

def build_package():
    """构建包"""
    
    # 清理旧文件
    if os.path.exists('dist'):
        shutil.rmtree('dist')
    if os.path.exists('build'):
        shutil.rmtree('build')
    if os.path.exists('byteiq.egg-info'):
        shutil.rmtree('byteiq.egg-info')
    
    # 创建dist目录
    os.makedirs('dist', exist_ok=True)
    
    # 尝试使用不同的构建方法
    methods = [
        [sys.executable, '-m', 'build', '--sdist'],
        [sys.executable, 'setup.py', 'sdist'],
        [sys.executable, '-m', 'pip', 'wheel', '.', '--no-deps', '-w', 'dist']
    ]
    
    for i, method in enumerate(methods, 1):
        print(f"尝试方法 {i}: {' '.join(method)}")
        try:
            result = subprocess.run(
                method,
                capture_output=True,
                text=True,
                timeout=120,
                cwd=os.getcwd()
            )
            
            print(f"返回码: {result.returncode}")
            if result.stdout:
                print(f"输出: {result.stdout}")
            if result.stderr:
                print(f"错误: {result.stderr}")
            
            # 检查是否生成了文件
            if os.path.exists('dist') and os.listdir('dist'):
                print(f"方法 {i} 成功!")
                for f in os.listdir('dist'):
                    print(f"  生成文件: {f} ({os.path.getsize(os.path.join('dist', f))} bytes)")
                return True
                
        except Exception as e:
            print(f"方法 {i} 失败: {e}")
            continue
    
    print("所有构建方法都失败了")
    return False

if __name__ == "__main__":
    success = build_package()
    if not success:
        print("构建失败，请检查配置")
        sys.exit(1)
    else:
        print("构建成功！")
