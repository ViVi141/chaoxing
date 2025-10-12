# -*- coding: utf-8 -*-
"""
SMTP邮件功能测试脚本
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from email_service import EmailService
from config import settings
from api.logger import logger


def test_smtp_connection():
    """测试SMTP连接"""
    print("="*60)
    print("测试SMTP连接")
    print("="*60)
    
    if not settings.SMTP_ENABLED:
        print("❌ SMTP未启用（SMTP_ENABLED=false）")
        print("请在.env中设置SMTP_ENABLED=true")
        return False
    
    if not settings.SMTP_USERNAME or not settings.SMTP_PASSWORD:
        print("❌ SMTP配置不完整")
        print(f"SMTP_USERNAME: {settings.SMTP_USERNAME or '(未配置)'}")
        print(f"SMTP_PASSWORD: {'***' if settings.SMTP_PASSWORD else '(未配置)'}")
        return False
    
    print(f"✅ SMTP已启用")
    print(f"   服务器: {settings.SMTP_HOST}:{settings.SMTP_PORT}")
    print(f"   用户名: {settings.SMTP_USERNAME}")
    print(f"   使用TLS: {settings.SMTP_USE_TLS}")
    print(f"   发件人: {settings.SMTP_FROM_EMAIL}")
    
    return True


def test_send_test_email():
    """发送测试邮件"""
    print("\n"+"="*60)
    print("发送测试邮件")
    print("="*60)
    
    email_service = EmailService()
    
    # 使用发件邮箱作为收件地址（发给自己）
    test_email = settings.SMTP_FROM_EMAIL
    
    if not test_email:
        print("❌ 未配置发件邮箱")
        return False
    
    print(f"收件人: {test_email}")
    print("正在发送...")
    
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }
            .content { background: #f9f9f9; padding: 30px; border-radius: 0 0 10px 10px; }
            .success { background: #d4edda; border-left: 4px solid #28a745; padding: 15px; margin: 15px 0; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>✅ SMTP测试成功</h1>
            </div>
            <div class="content">
                <p>恭喜！您的SMTP配置正确。</p>
                <div class="success">
                    <p><strong>测试详情：</strong></p>
                    <ul>
                        <li>SMTP服务器: {}</li>
                        <li>发件人: {}</li>
                        <li>收件人: {}</li>
                        <li>测试时间: {}</li>
                    </ul>
                </div>
                <p>现在您可以使用以下邮件功能：</p>
                <ul>
                    <li>✅ 注册邮箱验证</li>
                    <li>✅ 忘记密码</li>
                    <li>✅ 任务通知</li>
                    <li>✅ 欢迎邮件</li>
                </ul>
            </div>
        </div>
    </body>
    </html>
    """.format(
        settings.SMTP_HOST,
        settings.SMTP_FROM_EMAIL,
        test_email,
        __import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )
    
    success = email_service.send_email(
        to_email=test_email,
        subject="【超星学习通】SMTP测试邮件",
        html_content=html_content,
        text_content="这是一封SMTP测试邮件。如果您收到此邮件，说明SMTP配置正确。"
    )
    
    if success:
        print("✅ 测试邮件发送成功！")
        print(f"   请检查邮箱: {test_email}")
        print("   （注意查看垃圾邮件文件夹）")
        return True
    else:
        print("❌ 测试邮件发送失败")
        print("   请检查SMTP配置和网络连接")
        return False


def test_verification_email():
    """测试验证邮件"""
    print("\n"+"="*60)
    print("测试验证邮件模板")
    print("="*60)
    
    email_service = EmailService()
    test_email = settings.SMTP_FROM_EMAIL
    
    if not test_email:
        print("❌ 未配置发件邮箱")
        return False
    
    verification_url = "http://localhost:5173/verify-email?token=test_token_123456"
    
    success = email_service.send_verification_email(
        to_email=test_email,
        username="测试用户",
        verification_url=verification_url
    )
    
    if success:
        print("✅ 验证邮件发送成功！")
        print(f"   请检查邮箱: {test_email}")
        return True
    else:
        print("❌ 验证邮件发送失败")
        return False


def test_password_reset_email():
    """测试密码重置邮件"""
    print("\n"+"="*60)
    print("测试密码重置邮件模板")
    print("="*60)
    
    email_service = EmailService()
    test_email = settings.SMTP_FROM_EMAIL
    
    if not test_email:
        print("❌ 未配置发件邮箱")
        return False
    
    reset_url = "http://localhost:5173/reset-password?token=test_reset_token_123456"
    
    success = email_service.send_password_reset_email(
        to_email=test_email,
        username="测试用户",
        reset_url=reset_url
    )
    
    if success:
        print("✅ 密码重置邮件发送成功！")
        print(f"   请检查邮箱: {test_email}")
        return True
    else:
        print("❌ 密码重置邮件发送失败")
        return False


def test_welcome_email():
    """测试欢迎邮件"""
    print("\n"+"="*60)
    print("测试欢迎邮件模板")
    print("="*60)
    
    email_service = EmailService()
    test_email = settings.SMTP_FROM_EMAIL
    
    if not test_email:
        print("❌ 未配置发件邮箱")
        return False
    
    success = email_service.send_welcome_email(
        to_email=test_email,
        username="测试用户"
    )
    
    if success:
        print("✅ 欢迎邮件发送成功！")
        print(f"   请检查邮箱: {test_email}")
        return True
    else:
        print("❌ 欢迎邮件发送失败")
        return False


def main():
    """主测试流程"""
    print("""
╔═══════════════════════════════════════════════════════════╗
║           超星学习通 SMTP邮件功能测试                     ║
║                                                           ║
║  请先在.env中配置SMTP参数                                 ║
║  测试邮件将发送到配置的发件邮箱                           ║
╚═══════════════════════════════════════════════════════════╝
    """)
    
    results = {
        "SMTP连接": False,
        "测试邮件": False,
        "验证邮件": False,
        "重置邮件": False,
        "欢迎邮件": False
    }
    
    # 1. 测试SMTP连接
    results["SMTP连接"] = test_smtp_connection()
    
    if not results["SMTP连接"]:
        print("\n" + "="*60)
        print("❌ SMTP配置有误，无法继续测试")
        print("="*60)
        print("\n请按照以下步骤配置：")
        print("1. 复制 web/backend/.env.example 为 .env")
        print("2. 在.env中配置SMTP参数")
        print("3. 设置 SMTP_ENABLED=true")
        print("4. 重新运行此测试")
        return
    
    # 2. 测试基础邮件发送
    results["测试邮件"] = test_send_test_email()
    
    if not results["测试邮件"]:
        print("\n" + "="*60)
        print("❌ 邮件发送失败，请检查：")
        print("="*60)
        print("1. SMTP服务器地址和端口是否正确")
        print("2. 用户名和密码是否正确")
        print("3. 是否开启了SMTP服务")
        print("4. 网络连接是否正常")
        print("5. 防火墙是否阻止SMTP端口")
        return
    
    # 3. 测试各类邮件模板
    results["验证邮件"] = test_verification_email()
    results["重置邮件"] = test_password_reset_email()
    results["欢迎邮件"] = test_welcome_email()
    
    # 总结
    print("\n" + "="*60)
    print("测试结果总结")
    print("="*60)
    
    for name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{name:12s}: {status}")
    
    passed = sum(1 for r in results.values() if r)
    total = len(results)
    success_rate = (passed / total) * 100
    
    print(f"\n成功率: {success_rate:.1f}% ({passed}/{total})")
    
    if success_rate == 100:
        print("\n🎉 所有测试通过！SMTP配置完美！")
        print("现在可以使用完整的邮件功能了。")
    elif success_rate >= 80:
        print("\n⚠️  大部分测试通过，建议检查失败的项目")
    else:
        print("\n❌ 测试未通过，请检查SMTP配置")
    
    print("\n" + "="*60)


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n\n测试出错: {e}")
        import traceback
        traceback.print_exc()

