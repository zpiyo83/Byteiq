# test_command_processor.py

import unittest
from unittest.mock import patch, MagicMock
import sys
import os

# 将项目根目录添加到Python路径中
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.command_processor import handle_hacpp_command
from src.modes import hacpp_mode

class TestHacppCommand(unittest.TestCase):

    def setUp(self):
        """在每次测试前重置HACPP模式"""
        hacpp_mode.deactivate()

    @patch('builtins.input', return_value='2255')
    @patch('builtins.print')
    def test_activate_hacpp_mode_success(self, mock_print, mock_input):
        """测试成功激活HACPP模式"""
        handle_hacpp_command(['/hacpp'])
        self.assertTrue(hacpp_mode.is_active)
        self.assertTrue(hacpp_mode.authenticated)
        mock_print.assert_any_call("\x1b[32m✓ HACPP模式已激活\x1b[0m")

    @patch('builtins.input', return_value='wrong_code')
    @patch('builtins.print')
    def test_activate_hacpp_mode_fail(self, mock_print, mock_input):
        """测试使用错误的测试码激活HACPP模式"""
        handle_hacpp_command(['/hacpp'])
        self.assertFalse(hacpp_mode.is_active)
        mock_print.assert_any_call("\x1b[31m✗ 测试码错误\x1b[0m")

    @patch('builtins.input', return_value='gpt-3.5-turbo')
    @patch('builtins.print')
    def test_set_cheap_model_success(self, mock_print, mock_input):
        """测试成功设置便宜模型"""
        hacpp_mode.activate('2255')  # 先激活
        handle_hacpp_command(['/hacpp', 'model'])
        self.assertEqual(hacpp_mode.cheap_model, 'gpt-3.5-turbo')
        self.assertTrue(hacpp_mode.is_hacpp_active())
        mock_print.assert_any_call("\x1b[32m✓ 便宜模型已设置: gpt-3.5-turbo\x1b[0m")

    @patch('builtins.print')
    def test_set_cheap_model_not_activated(self, mock_print):
        """测试在未激活HACPP模式时设置便宜模型"""
        handle_hacpp_command(['/hacpp', 'model'])
        self.assertIsNone(hacpp_mode.cheap_model)
        mock_print.assert_any_call("\x1b[31m错误：请先激活HACPP模式\x1b[0m")

    @patch('builtins.print')
    def test_hacpp_status_command(self, mock_print):
        """测试 /hacpp status 命令"""
        # 未激活状态
        handle_hacpp_command(['/hacpp', 'status'])
        mock_print.assert_any_call("\x1b[31mHACPP模式状态: 未激活\x1b[0m")

        # 已激活但未设置模型
        hacpp_mode.activate('2255')
        handle_hacpp_command(['/hacpp', 'status'])
        mock_print.assert_any_call("\x1b[33mHACPP模式状态: 已认证，但未设置便宜模型\x1b[0m")

        # 完全激活
        hacpp_mode.set_cheap_model('gpt-3.5-turbo')
        handle_hacpp_command(['/hacpp', 'status'])
        mock_print.assert_any_call("\x1b[32mHACPP模式状态: 激活\x1b[0m")

    @patch('builtins.print')
    def test_deactivate_hacpp_mode(self, mock_print):
        """测试关闭HACPP模式"""
        hacpp_mode.activate('2255')
        hacpp_mode.set_cheap_model('gpt-3.5-turbo')
        self.assertTrue(hacpp_mode.is_hacpp_active())

        handle_hacpp_command(['/hacpp', 'off'])
        self.assertFalse(hacpp_mode.is_hacpp_active())
        self.assertFalse(hacpp_mode.is_active)
        self.assertIsNone(hacpp_mode.cheap_model)
        mock_print.assert_any_call("\x1b[33mHACPP模式已关闭\x1b[0m")

if __name__ == '__main__':
    unittest.main()

