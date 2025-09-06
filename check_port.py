#!/usr/bin/env python3
"""
端口检查工具 - 检查并释放被占用的端口
"""

import socket
import subprocess
import sys

def check_port_available(port):
    """检查端口是否可用"""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def find_process_using_port(port):
    """查找占用端口的进程"""
    try:
        result = subprocess.run(['netstat', '-ano'], capture_output=True, text=True)
        lines = result.stdout.split('\n')
        
        for line in lines:
            if f':{port}' in line and 'LISTENING' in line:
                parts = line.split()
                if len(parts) >= 5:
                    pid = parts[-1]
                    return pid
    except Exception:
        pass
    return None

def kill_process(pid):
    """终止进程"""
    try:
        subprocess.run(['taskkill', '/F', '/PID', pid], capture_output=True)
        return True
    except Exception:
        return False

def main():
    port = 25059
    print(f"🔍 检查端口 {port}...")
    
    if check_port_available(port):
        print(f"✅ 端口 {port} 可用")
        return
    
    print(f"❌ 端口 {port} 被占用")
    
    # 查找占用进程
    pid = find_process_using_port(port)
    if pid:
        print(f"📋 占用进程 PID: {pid}")
        
        choice = input("是否要终止该进程? (y/N): ").strip().lower()
        if choice == 'y':
            if kill_process(pid):
                print(f"✅ 进程已终止")
                if check_port_available(port):
                    print(f"✅ 端口 {port} 现在可用")
                else:
                    print(f"⚠️  端口仍被占用")
            else:
                print(f"❌ 无法终止进程")
    else:
        print("❓ 无法找到占用进程")
    
    print("\n💡 其他解决方案:")
    print("1. 重启命令提示符")
    print("2. 重启计算机")
    print("3. 使用任务管理器手动结束相关进程")

if __name__ == '__main__':
    main()
