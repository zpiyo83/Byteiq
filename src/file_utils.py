import os

def get_directory_structure(root_dir):
    """
    生成目录结构的树状表示
    
    Args:
        root_dir (str): 根目录路径
    
    Returns:
        str: 目录结构的树状表示字符串
    """
    structure = []
    for root, dirs, files in os.walk(root_dir):
        # 计算当前目录的相对路径
        level = root.replace(root_dir, '').count(os.sep)
        indent = ' ' * 4 * level
        structure.append(f"{indent}{os.path.basename(root)}/")
        
        subindent = ' ' * 4 * (level + 1)
        for file in files:
            structure.append(f"{subindent}- {file}")
    
    return '\n'.join(structure)
