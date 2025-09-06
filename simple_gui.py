#!/usr/bin/env python3
"""
简化的ByteIQ Web GUI启动器
使用最基本的Flask配置，避免端口绑定问题
"""

import os
import sys
import time
import webbrowser
import threading

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def start_simple_gui():
    """启动简化版GUI"""
    try:
        from flask import Flask, render_template, request, jsonify
        from src.config import load_config, save_config
        from src.todo_manager import todo_manager
        from src.commands import get_available_commands, get_command_descriptions
        
        app = Flask(__name__, template_folder='templates', static_folder='static')
        
        @app.route('/')
        def index():
            return render_template('index.html')
        
        @app.route('/api/config', methods=['GET'])
        def get_config():
            config = load_config()
            return jsonify({
                'language': config.get('language', 'zh-CN'),
                'model': config.get('model', 'gpt-3.5-turbo'),
                'api_key_set': bool(config.get('api_key')),
                'theme': config.get('theme', 'dark')
            })
        
        @app.route('/api/todos', methods=['GET'])
        def get_todos():
            todos = todo_manager.get_root_todos()
            todo_list = []
            for todo in todos:
                todo_list.append({
                    'id': todo.id,
                    'title': todo.title,
                    'description': todo.description,
                    'status': todo.status,
                    'priority': todo.priority,
                    'progress': todo.progress
                })
            return jsonify(todo_list)
        
        # 查找可用端口
        import socket
        def find_port():
            for port in range(25059, 25070):
                try:
                    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                        s.bind(('127.0.0.1', port))
                        return port
                except OSError:
                    continue
            return None
        
        port = find_port()
        if not port:
            print("❌ 无法找到可用端口")
            return
        
        print(f"🌐 启动简化版Web GUI...")
        print(f"📍 访问地址: http://localhost:{port}")
        
        # 延迟打开浏览器
        def open_browser():
            time.sleep(2)
            try:
                webbrowser.open(f'http://localhost:{port}')
                print("🌐 浏览器已打开")
            except Exception as e:
                print(f"⚠️  请手动访问: http://localhost:{port}")
        
        threading.Thread(target=open_browser, daemon=True).start()
        
        # 启动Flask应用
        app.run(host='127.0.0.1', port=port, debug=False, use_reloader=False)
        
    except KeyboardInterrupt:
        print("\n🛑 Web GUI已停止")
    except Exception as e:
        print(f"❌ 启动失败: {e}")
        print("💡 请尝试:")
        print("   1. 安装依赖: pip install flask")
        print("   2. 重启命令提示符")

if __name__ == '__main__':
    start_simple_gui()
