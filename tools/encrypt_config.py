# -*- coding: utf-8 -*-
"""
配置文件加密工具
用于将配置文件中的明文密码加密
"""
import sys
from pathlib import Path

# 添加父目录到sys.path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.secure_config import migrate_config_to_encrypted


def main():
    """主函数"""
    print("=" * 60)
    print("超星学习通配置文件加密工具")
    print("=" * 60)
    print()

    # 获取配置文件路径
    if len(sys.argv) > 1:
        config_path = sys.argv[1]
    else:
        config_path = input("请输入配置文件路径（默认: config.ini）: ").strip()
        if not config_path:
            config_path = "config.ini"

    # 检查文件是否存在
    if not Path(config_path).exists():
        print(f"错误: 配置文件不存在: {config_path}")
        sys.exit(1)

    print(f"正在处理配置文件: {config_path}")
    print()

    # 执行加密
    success = migrate_config_to_encrypted(config_path)

    print()
    if success:
        print("✓ 配置文件密码加密成功！")
        print()
        print("注意事项:")
        print("1. 加密密钥已保存到 .config_key 文件")
        print("2. 请妥善保管该文件，丢失后无法解密密码")
        print("3. 不要将 .config_key 文件上传到公共仓库")
        print("4. 已将 password_encrypted 设置为 true")
    else:
        print("✗ 配置文件密码加密失败！")
        print("请查看日志了解详细错误信息")
        sys.exit(1)

    print()
    print("=" * 60)


if __name__ == "__main__":
    main()
