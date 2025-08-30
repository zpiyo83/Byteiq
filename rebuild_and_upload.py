#!/usr/bin/env python3
"""
重新构建并上传ByteIQ包到PyPI
"""
import os
import shutil
import subprocess
import sys
from pathlib import Path

# 强制使用 UTF-8，避免 Windows 控制台 GBK 编码导致 rich 进度条报错
os.environ.setdefault("PYTHONIOENCODING", "utf-8")
os.environ.setdefault("PYTHONUTF8", "1")


def run_command(cmd, check=True):
    """运行命令并显示输出"""
    print(f"执行命令: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.stdout:
        print(result.stdout)
    if result.stderr:
        print(result.stderr)
    if check and result.returncode != 0:
        print(f"命令执行失败，退出码: {result.returncode}")
        sys.exit(1)
    return result


def clean_build_dirs():
    """清理构建目录"""
    dirs_to_clean = ['dist', 'build', 'byteiq.egg-info', 'src/byteiq.egg-info']

    for dir_name in dirs_to_clean:
        dir_path = Path(dir_name)
        if dir_path.exists():
            print(f"清理目录: {dir_path}")
            shutil.rmtree(dir_path)
        else:
            print(f"目录不存在，跳过: {dir_path}")


def build_package():
    """仅构建 wheel"""
    print("开始构建包 (wheel-only)...")

    # 仅构建 wheel，避免生成源码包 sdist
    run_command("python -m build --wheel")

    # 检查构建结果
    dist_dir = Path("dist")
    if dist_dir.exists():
        files = list(dist_dir.glob("*.whl"))
        print(f"构建完成，生成文件:")
        for file in files:
            print(f"  - {file.name} ({file.stat().st_size} bytes)")
    else:
        print("错误: dist目录不存在")
        sys.exit(1)


def upload_to_pypi():
    """仅上传 wheel"""
    print("开始上传到PyPI (wheel-only)...")

    # 优先从环境变量读取 API Token
    api_token = os.environ.get("TWINE_PASSWORD", "")
    if not api_token:
        print("错误: 未设置环境变量 TWINE_PASSWORD")
        sys.exit(1)

    # 仅上传 .whl，并禁用进度条
    cmd = (
        'python -m twine upload dist/*.whl '
        '--username __token__ '
        f'--password {api_token} '
        '--verbose '
        '--disable-progress-bar'
    )
    run_command(cmd)


def main():
    """主函数"""
    print("ByteIQ包重新构建和上传脚本 (wheel-only)")
    print("=" * 50)

    try:
        # 步骤1: 清理旧的构建文件
        print("\n步骤1: 清理旧的构建文件")
        clean_build_dirs()

        # 步骤2: 仅构建 wheel
        print("\n步骤2: 仅构建 wheel")
        build_package()

        # 步骤3: 仅上传 wheel
        print("\n步骤3: 仅上传 wheel")
        upload_to_pypi()

        print("\n✅ 成功完成所有步骤!")

    except Exception as e:
        print(f"\n❌ 错误: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
