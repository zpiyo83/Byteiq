#!/usr/bin/env python3
"""
ByteIQ GUI 启动脚本
简化的启动脚本，用于快速启动Web GUI界面
"""

import os
import sys
import subprocess
import webbrowser
import time
import threading
import socket

def install_dependencies():
    """安装必要的依赖"""
    try:
        import flask
        import flask_socketio
        print("✅ Web GUI依赖已安装")
        return True
    except ImportError:
        print("📦 正在安装Web GUI依赖...")
        try:
            subprocess.run([sys.executable, "-m", "pip", "install", "flask", "flask-socketio"], 
                         check=True, capture_output=True)
            print("✅ 依赖安装完成")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ 依赖安装失败: {e}")
            return False

def check_port_available(port):
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_available_port(start_port=25059, max_attempts=10):
    """查找可用端口"""
    for i in range(max_attempts):
        port = start_port + i
        if check_port_available(port):
            return port
    return None

def start_gui():
    """启动GUI界面"""
    print("🚀 启动ByteIQ Web GUI...")
    
    # 检查端口并找到可用端口
    port = 25059
    if not check_port_available(port):
        print(f"⚠️  端口 {port} 已被占用，正在寻找可用端口...")
        available_port = find_available_port(port)
        if available_port:
            port = available_port
            print(f"✅ 找到可用端口: {port}")
        else:
            print(f"❌ 无法找到可用端口 (尝试范围: {port}-{port+9})")
            print("请手动停止占用端口的程序，或稍后重试")
            return
    
    print(f"📍 访问地址: http://localhost:{port}")
    print("🌐 浏览器将在3秒后自动打开")
    print("⏹️  按 Ctrl+C 停止服务器")
    print("-" * 50)
    
    # 延迟打开浏览器
    def open_browser():
        time.sleep(3)
        try:
            webbrowser.open(f'http://localhost:{port}')
            print("🌐 浏览器已打开")
        except Exception as e:
            print(f"⚠️  无法自动打开浏览器: {e}")
            print(f"请手动访问: http://localhost:{port}")
    
    # 启动浏览器线程
    browser_thread = threading.Thread(target=open_browser, daemon=True)
    browser_thread.start()
    
    # 启动Web服务器
    try:
        from web_gui import start_web_gui
        start_web_gui(port=port, auto_open=False)
    except KeyboardInterrupt:
        print("\n🛑 Web GUI已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        if "Address already in use" in str(e) or "10048" in str(e):
            print("💡 提示: 端口被占用，请尝试重新运行脚本")

if __name__ == '__main__':
    print("=" * 50)
    print("🧠 ByteIQ Web GUI 启动器")
    print("=" * 50)
    
    # 检查并安装依赖
    if not install_dependencies():
        print("❌ 无法安装依赖，退出")
        sys.exit(1)
    
    # 启动GUI
    start_gui()
