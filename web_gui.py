#!/usr/bin/env python3
"""
ByteIQ Web GUI - Flask后端服务器
提供网页界面访问CLI的所有功能
"""

import os
import sys
import json
import threading
import webbrowser
import socket
from flask import Flask, render_template, request, jsonify, session
from flask_socketio import SocketIO, emit
import uuid
from datetime import datetime

# 添加src目录到Python路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.config import load_config, save_config
from src.ai_client import ai_client
from src.todo_manager import todo_manager
from src.commands import get_available_commands, get_command_descriptions

app = Flask(__name__, template_folder='templates', static_folder='static')
app.config['SECRET_KEY'] = 'byteiq-web-gui-secret-key'
socketio = SocketIO(app, cors_allowed_origins="*")

class WebGUIManager:
    """Web GUI管理器"""
    
    def __init__(self):
        self.active_sessions = {}
        self.ai_responses = {}
    
    def create_session(self):
        """创建新的会话"""
        session_id = str(uuid.uuid4())
        self.active_sessions[session_id] = {
            'created_at': datetime.now(),
            'last_activity': datetime.now(),
            'context': []
        }
        return session_id
    
    def get_session(self, session_id):
        """获取会话信息"""
        return self.active_sessions.get(session_id)
    
    def update_session_activity(self, session_id):
        """更新会话活动时间"""
        if session_id in self.active_sessions:
            self.active_sessions[session_id]['last_activity'] = datetime.now()

web_manager = WebGUIManager()

@app.route('/')
def index():
    """主页"""
    return render_template('index.html')

@app.route('/api/config', methods=['GET'])
def get_config():
    """获取配置信息"""
    config = load_config()
    # 隐藏敏感信息
    safe_config = {
        'language': config.get('language', 'zh-CN'),
        'model': config.get('model', 'gpt-3.5-turbo'),
        'api_key_set': bool(config.get('api_key')),
        'theme': config.get('theme', 'dark')
    }
    return jsonify(safe_config)

@app.route('/api/config', methods=['POST'])
def update_config():
    """更新配置"""
    try:
        data = request.json
        config = load_config()
        
        if 'language' in data:
            config['language'] = data['language']
        if 'model' in data:
            config['model'] = data['model']
        if 'api_key' in data and data['api_key']:
            config['api_key'] = data['api_key']
        if 'theme' in data:
            config['theme'] = data['theme']
        
        if save_config(config):
            return jsonify({'success': True, 'message': '配置已保存'})
        else:
            return jsonify({'success': False, 'message': '保存失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/commands', methods=['GET'])
def get_commands():
    """获取可用命令列表"""
    commands = get_available_commands()
    descriptions = get_command_descriptions()
    
    command_list = []
    for cmd in commands:
        command_list.append({
            'command': cmd,
            'description': descriptions.get(cmd, '')
        })
    
    return jsonify(command_list)

@app.route('/api/todos', methods=['GET'])
def get_todos():
    """获取TODO列表"""
    try:
        todos = todo_manager.get_root_todos()
        todo_list = []
        
        for todo in todos:
            todo_list.append({
                'id': todo.id,
                'title': todo.title,
                'description': todo.description,
                'status': todo.status,
                'priority': todo.priority,
                'progress': todo.progress,
                'created_at': todo.created_at.isoformat() if todo.created_at else None,
                'updated_at': todo.updated_at.isoformat() if todo.updated_at else None
            })
        
        return jsonify(todo_list)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/todos', methods=['POST'])
def add_todo():
    """添加新TODO"""
    try:
        data = request.json
        title = data.get('title', '').strip()
        description = data.get('description', '').strip()
        priority = data.get('priority', 'medium')
        
        if not title:
            return jsonify({'success': False, 'message': '任务标题不能为空'})
        
        todo_id = todo_manager.add_todo(title, description, priority)
        return jsonify({'success': True, 'todo_id': todo_id, 'message': '任务已添加'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/todos/<todo_id>', methods=['PUT'])
def update_todo(todo_id):
    """更新TODO"""
    try:
        data = request.json
        status = data.get('status')
        progress = data.get('progress', 0)
        
        success = todo_manager.update_todo(todo_id, status=status, progress=progress)
        if success:
            return jsonify({'success': True, 'message': '任务已更新'})
        else:
            return jsonify({'success': False, 'message': '更新失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/todos/<todo_id>', methods=['DELETE'])
def delete_todo(todo_id):
    """删除TODO"""
    try:
        success = todo_manager.delete_todo(todo_id)
        if success:
            return jsonify({'success': True, 'message': '任务已删除'})
        else:
            return jsonify({'success': False, 'message': '删除失败'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/chat', methods=['POST'])
def chat():
    """处理AI对话 - 直接调用CLI处理逻辑"""
    try:
        data = request.json
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            return jsonify({'success': False, 'message': '消息不能为空'})
        
        # 检查API密钥
        config = load_config()
        if not config.get('api_key'):
            return jsonify({'success': False, 'message': '请先设置API密钥'})
        
        # 创建或获取会话
        if not session_id:
            session_id = web_manager.create_session()
        
        web_manager.update_session_activity(session_id)
        
        # 直接调用CLI的AI处理逻辑
        try:
            # 导入CLI处理函数
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from byteiq import process_ai_conversation
            
            # 捕获CLI输出
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            # 重定向输出并调用CLI处理逻辑
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                process_ai_conversation(message)
            
            # 获取输出结果
            cli_output = output_buffer.getvalue()
            cli_errors = error_buffer.getvalue()
            
            # 构建响应
            final_response = cli_output.strip() if cli_output.strip() else "处理完成"
            if cli_errors.strip():
                final_response += f"\n\n**错误信息:**\n{cli_errors.strip()}"
            
            return jsonify({
                'success': True,
                'response': final_response,
                'session_id': session_id,
                'cli_mode': True
            })
            
        except Exception as e:
            return jsonify({'success': False, 'message': f'CLI处理错误: {str(e)}'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/analyze', methods=['POST'])
def analyze_project():
    """分析项目"""
    try:
        from src.project_analyzer import project_analyzer
        
        analysis_result = project_analyzer.analyze_project()
        
        if analysis_result:
            # 生成BYTEIQ.md文件
            output_path = project_analyzer.generate_byteiq_md(ai_client=ai_client)
            
            return jsonify({
                'success': True,
                'message': '项目分析完成',
                'analysis': {
                    'project_type': analysis_result['project_type'],
                    'tech_stack': analysis_result['tech_stack'],
                    'total_files': analysis_result['file_structure']['total_files'],
                    'project_size': analysis_result['project_info']['size']['size_mb'],
                    'languages': analysis_result['code_features']['languages'],
                    'frameworks': analysis_result['code_features']['frameworks']
                }
            })
        else:
            return jsonify({'success': False, 'message': '项目分析失败'})
            
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@app.route('/api/context', methods=['GET'])
def get_context_status():
    """获取上下文状态"""
    try:
        stats = ai_client.context_manager.get_context_stats()
        return jsonify(stats)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/context/clear', methods=['POST'])
def clear_context():
    """清除上下文"""
    try:
        ai_client.context_manager.clear_context()
        return jsonify({'success': True, 'message': '上下文已清除'})
    except Exception as e:
        return jsonify({'success': False, 'message': str(e)})

@socketio.on('connect')
def handle_connect():
    """WebSocket连接"""
    session_id = web_manager.create_session()
    emit('session_created', {'session_id': session_id})

@socketio.on('disconnect')
def handle_disconnect():
    """WebSocket断开连接"""
    pass

@socketio.on('ai_message')
def handle_ai_message(data):
    """处理AI消息 (WebSocket版本) - 直接调用CLI处理逻辑"""
    try:
        message = data.get('message', '').strip()
        session_id = data.get('session_id')
        
        if not message:
            emit('ai_error', {'message': '消息不能为空'})
            return
        
        # 检查API密钥
        config = load_config()
        if not config.get('api_key'):
            emit('ai_error', {'message': '请先设置API密钥'})
            return
        
        # 发送处理开始信号
        emit('ai_processing', {'message': '正在处理...'})
        
        # 直接调用CLI的AI处理逻辑
        try:
            # 导入CLI处理函数
            import sys
            import os
            sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
            from byteiq import process_ai_conversation
            
            # 捕获CLI输出
            import io
            from contextlib import redirect_stdout, redirect_stderr
            
            output_buffer = io.StringIO()
            error_buffer = io.StringIO()
            
            # 重定向输出并调用CLI处理逻辑
            with redirect_stdout(output_buffer), redirect_stderr(error_buffer):
                process_ai_conversation(message)
            
            # 获取输出结果
            cli_output = output_buffer.getvalue()
            cli_errors = error_buffer.getvalue()
            
            # 构建响应
            final_response = cli_output.strip() if cli_output.strip() else "处理完成"
            if cli_errors.strip():
                final_response += f"\n\n**错误信息:**\n{cli_errors.strip()}"
            
            emit('ai_response', {
                'response': final_response,
                'session_id': session_id,
                'cli_mode': True
            })
            
        except Exception as e:
            emit('ai_error', {'message': f'CLI处理错误: {str(e)}'})
            
    except Exception as e:
        emit('ai_error', {'message': str(e)})

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

def start_web_gui(port=25059, auto_open=True):
    """启动Web GUI"""
    print(f"🌐 启动ByteIQ Web GUI...")
    
    # 尝试多个端口，添加重试机制
    max_retries = 3
    for retry in range(max_retries):
        # 检查端口是否可用
        if not check_port_available(port):
            print(f"⚠️  端口 {port} 已被占用，正在寻找可用端口...")
            available_port = find_available_port(port)
            if available_port:
                port = available_port
                print(f"✅ 找到可用端口: {port}")
            else:
                print(f"❌ 无法找到可用端口 (尝试范围: {port}-{port+9})")
                if retry < max_retries - 1:
                    print(f"🔄 等待2秒后重试... ({retry+1}/{max_retries})")
                    import time
                    time.sleep(2)
                    continue
                else:
                    print(f"请手动停止占用端口的程序，或稍后重试")
                    return
        
        print(f"📍 访问地址: http://localhost:{port}")
        
        if auto_open:
            # 延迟打开浏览器
            def open_browser():
                import time
                time.sleep(2)
                try:
                    webbrowser.open(f'http://localhost:{port}')
                except Exception as e:
                    print(f"⚠️  无法打开浏览器: {e}")
            
            threading.Thread(target=open_browser, daemon=True).start()
        
        try:
            # 使用更安全的绑定配置
            socketio.run(app, 
                        host='127.0.0.1',  # 只绑定本地地址
                        port=port, 
                        debug=False,
                        use_reloader=False)  # 禁用重载器
            break  # 成功启动，跳出重试循环
            
        except KeyboardInterrupt:
            print("\n🛑 Web GUI已停止")
            break
            
        except Exception as e:
            error_msg = str(e)
            print(f"❌ Web GUI启动失败: {error_msg}")
            
            if "Address already in use" in error_msg or "10048" in error_msg:
                if retry < max_retries - 1:
                    print(f"🔄 端口冲突，尝试下一个端口... ({retry+1}/{max_retries})")
                    port += 1  # 尝试下一个端口
                    import time
                    time.sleep(1)
                    continue
                else:
                    print(f"💡 多次重试失败，请尝试:")
                    print(f"   1. 重启命令提示符")
                    print(f"   2. 运行: netstat -ano | findstr :{port-max_retries+1}")
                    print(f"   3. 使用任务管理器结束相关进程")
                    print(f"   4. 重启计算机")
            else:
                print(f"💡 其他错误，请检查:")
                print(f"   1. Python环境是否正常")
                print(f"   2. Flask依赖是否正确安装")
                print(f"   3. 防火墙设置")
            break

if __name__ == '__main__':
    start_web_gui()
