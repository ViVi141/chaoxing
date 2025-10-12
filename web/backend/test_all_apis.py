# -*- coding: utf-8 -*-
"""
完整的API测试脚本
测试所有后端API端点的功能
"""
import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import httpx
from typing import Optional, Dict, Any
from datetime import datetime

# API基础URL
BASE_URL = "http://localhost:8000"

# 全局变量
admin_token: Optional[str] = None
user_token: Optional[str] = None
test_user_id: Optional[int] = None
test_task_id: Optional[int] = None
test_config_id: Optional[int] = None


class APITester:
    """API测试器"""
    
    def __init__(self, base_url: str = BASE_URL):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=30.0)
        self.results = {
            "passed": 0,
            "failed": 0,
            "errors": []
        }
    
    async def close(self):
        """关闭客户端"""
        await self.client.aclose()
    
    def log(self, message: str, level: str = "INFO"):
        """打印日志"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        colors = {
            "INFO": "\033[94m",  # 蓝色
            "SUCCESS": "\033[92m",  # 绿色
            "ERROR": "\033[91m",  # 红色
            "WARNING": "\033[93m",  # 黄色
        }
        reset = "\033[0m"
        color = colors.get(level, "")
        print(f"{color}[{timestamp}] {level}: {message}{reset}")
    
    async def test_endpoint(
        self,
        name: str,
        method: str,
        endpoint: str,
        expected_status: int = 200,
        headers: Optional[Dict] = None,
        json_data: Optional[Dict] = None,
        params: Optional[Dict] = None
    ) -> Optional[Dict[str, Any]]:
        """测试单个端点"""
        try:
            self.log(f"测试: {name}")
            self.log(f"  {method} {endpoint}", "INFO")
            
            url = f"{self.base_url}{endpoint}"
            
            response = await self.client.request(
                method=method,
                url=url,
                headers=headers,
                json=json_data,
                params=params
            )
            
            if response.status_code == expected_status:
                self.log(f"  [OK] Pass (Status: {response.status_code})", "SUCCESS")
                self.results["passed"] += 1
                try:
                    return response.json()
                except:
                    return None
            else:
                self.log(f"  [FAIL] Failed (Expected: {expected_status}, Got: {response.status_code})", "ERROR")
                self.log(f"  Response: {response.text[:200]}", "ERROR")
                self.results["failed"] += 1
                self.results["errors"].append({
                    "name": name,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:200]
                })
                return None
                
        except Exception as e:
            self.log(f"  [ERROR] Exception: {str(e)}", "ERROR")
            self.results["failed"] += 1
            self.results["errors"].append({
                "name": name,
                "error": str(e)
            })
            return None
    
    def get_auth_header(self, token: str) -> Dict[str, str]:
        """获取认证头"""
        return {"Authorization": f"Bearer {token}"}


async def run_tests():
    """运行所有测试"""
    global admin_token, user_token, test_user_id, test_task_id, test_config_id
    
    tester = APITester()
    
    try:
        tester.log("="*60, "INFO")
        tester.log("开始API测试", "INFO")
        tester.log("="*60, "INFO")
        
        # ========== 1. 健康检查 ==========
        tester.log("\n【1. 健康检查】", "INFO")
        
        await tester.test_endpoint(
            name="根路径",
            method="GET",
            endpoint="/",
            expected_status=200
        )
        
        await tester.test_endpoint(
            name="健康检查",
            method="GET",
            endpoint="/api/health",
            expected_status=200
        )
        
        # ========== 2. 认证API测试 ==========
        tester.log("\n【2. 认证API测试】", "INFO")
        
        # 2.1 注册新用户
        register_data = {
            "username": f"testuser_{datetime.now().timestamp()}",
            "email": f"test_{datetime.now().timestamp()}@example.com",
            "password": "Test@123456"
        }
        
        register_response = await tester.test_endpoint(
            name="用户注册",
            method="POST",
            endpoint="/api/auth/register",
            expected_status=201,
            json_data=register_data
        )
        
        if register_response:
            user_token = register_response.get("access_token")
            test_user_id = register_response.get("user", {}).get("id")
            tester.log(f"  新用户ID: {test_user_id}", "SUCCESS")
        
        # 2.2 管理员登录（使用Form Data格式）
        # 注意：FastAPI的OAuth2PasswordRequestForm需要form data，不是JSON
        import urllib.parse
        admin_login_data = urllib.parse.urlencode({
            "username": "admin",
            "password": "Admin@123"
        })
        
        # 使用form data格式
        response = await tester.client.post(
            f"{tester.base_url}/api/auth/login",
            content=admin_login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            tester.log("测试: 管理员登录", "INFO")
            tester.log(f"  [OK] Pass (Status: {response.status_code})", "SUCCESS")
            tester.results["passed"] += 1
            admin_login_response = response.json()
        else:
            tester.log("测试: 管理员登录", "INFO")
            tester.log(f"  [FAIL] Failed (Expected: 200, Got: {response.status_code})", "ERROR")
            tester.results["failed"] += 1
            admin_login_response = None
        
        if admin_login_response:
            admin_token = admin_login_response.get("access_token")
            tester.log(f"  管理员Token: {admin_token[:20]}...", "SUCCESS")
        
        # 2.3 用户登录（使用Form Data格式）
        user_login_data = urllib.parse.urlencode({
            "username": register_data["username"],
            "password": register_data["password"]
        })
        
        response = await tester.client.post(
            f"{tester.base_url}/api/auth/login",
            content=user_login_data,
            headers={"Content-Type": "application/x-www-form-urlencoded"}
        )
        
        if response.status_code == 200:
            tester.log("测试: 用户登录", "INFO")
            tester.log(f"  [OK] Pass (Status: {response.status_code})", "SUCCESS")
            tester.results["passed"] += 1
            user_login_response = response.json()
        else:
            tester.log("测试: 用户登录", "INFO")
            tester.log(f"  [FAIL] Failed (Expected: 200, Got: {response.status_code})", "ERROR")
            tester.results["failed"] += 1
            user_login_response = None
        
        if user_login_response:
            user_token = user_login_response.get("access_token")
        
        # 2.4 获取当前用户信息
        if user_token:
            await tester.test_endpoint(
                name="获取当前用户信息",
                method="GET",
                endpoint="/api/auth/me",
                expected_status=200,
                headers=tester.get_auth_header(user_token)
            )
        
        # ========== 3. 用户配置API测试 ==========
        tester.log("\n【3. 用户配置API测试】", "INFO")
        
        if user_token:
            # 3.1 获取用户配置
            config_response = await tester.test_endpoint(
                name="获取用户配置",
                method="GET",
                endpoint="/api/user/config",
                expected_status=200,
                headers=tester.get_auth_header(user_token)
            )
            
            if config_response:
                test_config_id = config_response.get("id")
            
            # 3.2 更新用户配置
            config_update_data = {
                "cx_username": "13800138000",
                "cx_password": "test_password_123",
                "use_cookies": False,
                "speed": 1.5,
                "notopen_action": "retry",
                "tiku_config": {
                    "provider": "icodef",
                    "submit": True,
                    "cover_rate": 0.9
                },
                "notification_config": {
                    "provider": "dingtalk",
                    "url": "https://example.com/webhook"
                }
            }
            
            await tester.test_endpoint(
                name="更新用户配置",
                method="PUT",
                endpoint="/api/user/config",
                expected_status=200,
                headers=tester.get_auth_header(user_token),
                json_data=config_update_data
            )
            
            # 3.3 获取用户资料
            await tester.test_endpoint(
                name="获取用户资料",
                method="GET",
                endpoint="/api/user/profile",
                expected_status=200,
                headers=tester.get_auth_header(user_token)
            )
        
        # ========== 4. 任务API测试 ==========
        tester.log("\n【4. 任务API测试】", "INFO")
        
        if user_token:
            # 4.1 创建任务
            task_create_data = {
                "name": f"测试任务_{datetime.now().strftime('%H%M%S')}",
                "course_ids": ["123456", "789012"]
            }
            
            task_response = await tester.test_endpoint(
                name="创建任务",
                method="POST",
                endpoint="/api/tasks",
                expected_status=201,
                headers=tester.get_auth_header(user_token),
                json_data=task_create_data
            )
            
            if task_response:
                test_task_id = task_response.get("id")
                tester.log(f"  任务ID: {test_task_id}", "SUCCESS")
            
            # 4.2 获取任务列表
            await tester.test_endpoint(
                name="获取任务列表",
                method="GET",
                endpoint="/api/tasks",
                expected_status=200,
                headers=tester.get_auth_header(user_token),
                params={"page": 1, "page_size": 10}
            )
            
            # 4.3 获取任务详情
            if test_task_id:
                await tester.test_endpoint(
                    name="获取任务详情",
                    method="GET",
                    endpoint=f"/api/tasks/{test_task_id}",
                    expected_status=200,
                    headers=tester.get_auth_header(user_token)
                )
                
                # 4.4 更新任务
                task_update_data = {
                    "name": f"更新后的任务_{datetime.now().strftime('%H%M%S')}"
                }
                
                await tester.test_endpoint(
                    name="更新任务",
                    method="PUT",
                    endpoint=f"/api/tasks/{test_task_id}",
                    expected_status=200,
                    headers=tester.get_auth_header(user_token),
                    json_data=task_update_data
                )
                
                # 4.5 获取任务日志
                await tester.test_endpoint(
                    name="获取任务日志",
                    method="GET",
                    endpoint=f"/api/tasks/{test_task_id}/logs",
                    expected_status=200,
                    headers=tester.get_auth_header(user_token)
                )
                
                # 4.6 启动任务
                # 注意：任务会启动但可能在执行时失败（正常行为）
                await tester.test_endpoint(
                    name="启动任务",
                    method="POST",
                    endpoint=f"/api/tasks/{test_task_id}/start",
                    expected_status=200,  # 任务启动成功
                    headers=tester.get_auth_header(user_token)
                )
        
        # ========== 5. 管理员API测试 ==========
        tester.log("\n【5. 管理员API测试】", "INFO")
        
        if admin_token:
            # 5.1 获取所有用户
            await tester.test_endpoint(
                name="获取所有用户（管理员）",
                method="GET",
                endpoint="/api/admin/users",
                expected_status=200,
                headers=tester.get_auth_header(admin_token),
                params={"page": 1, "page_size": 10}
            )
            
            # 5.2 获取用户详情
            if test_user_id:
                await tester.test_endpoint(
                    name="获取用户详情（管理员）",
                    method="GET",
                    endpoint=f"/api/admin/users/{test_user_id}",
                    expected_status=200,
                    headers=tester.get_auth_header(admin_token)
                )
                
                # 5.3 更新用户
                user_update_data = {
                    "email": f"updated_{datetime.now().timestamp()}@example.com"
                }
                
                await tester.test_endpoint(
                    name="更新用户（管理员）",
                    method="PUT",
                    endpoint=f"/api/admin/users/{test_user_id}",
                    expected_status=200,
                    headers=tester.get_auth_header(admin_token),
                    json_data=user_update_data
                )
            
            # 5.4 获取所有任务
            await tester.test_endpoint(
                name="获取所有任务（管理员）",
                method="GET",
                endpoint="/api/admin/tasks",
                expected_status=200,
                headers=tester.get_auth_header(admin_token),
                params={"page": 1, "page_size": 10}
            )
            
            # 5.5 获取统计数据
            await tester.test_endpoint(
                name="获取统计数据（管理员）",
                method="GET",
                endpoint="/api/admin/statistics",
                expected_status=200,
                headers=tester.get_auth_header(admin_token)
            )
            
            # 5.6 获取系统日志
            await tester.test_endpoint(
                name="获取系统日志（管理员）",
                method="GET",
                endpoint="/api/admin/logs",
                expected_status=200,
                headers=tester.get_auth_header(admin_token),
                params={"page": 1, "page_size": 20}
            )
        
        # ========== 6. 权限测试 ==========
        tester.log("\n【6. 权限测试】", "INFO")
        
        if user_token:
            # 普通用户访问管理员API（应该失败）
            await tester.test_endpoint(
                name="Normal user access admin API (Should be 403)",
                method="GET",
                endpoint="/api/admin/statistics",
                expected_status=403,
                headers=tester.get_auth_header(user_token)
            )
        
        # 无token访问受保护API（应该失败）
        await tester.test_endpoint(
            name="No token access protected API (Should be 401)",
            method="GET",
            endpoint="/api/user/config",
            expected_status=401
        )
        
        # ========== 7. 清理测试数据 ==========
        tester.log("\n【7. 清理测试数据】", "INFO")
        
        # 删除测试任务（先取消再删除）
        if admin_token and test_task_id:
            # 先取消任务
            await tester.test_endpoint(
                name="取消测试任务",
                method="POST",
                endpoint=f"/api/tasks/{test_task_id}/cancel",
                expected_status=200,
                headers=tester.get_auth_header(user_token)
            )
            
            # 再删除任务
            await tester.test_endpoint(
                name="删除测试任务",
                method="DELETE",
                endpoint=f"/api/tasks/{test_task_id}",
                expected_status=200,
                headers=tester.get_auth_header(user_token)
            )
        
        # 删除测试用户
        if admin_token and test_user_id:
            await tester.test_endpoint(
                name="删除测试用户（管理员）",
                method="DELETE",
                endpoint=f"/api/admin/users/{test_user_id}",
                expected_status=200,
                headers=tester.get_auth_header(admin_token)
            )
        
        # ========== 测试总结 ==========
        tester.log("\n" + "="*60, "INFO")
        tester.log("测试完成", "INFO")
        tester.log("="*60, "INFO")
        tester.log(f"通过: {tester.results['passed']}", "SUCCESS")
        tester.log(f"失败: {tester.results['failed']}", "ERROR" if tester.results['failed'] > 0 else "INFO")
        
        if tester.results["errors"]:
            tester.log("\n失败的测试:", "ERROR")
            for i, error in enumerate(tester.results["errors"], 1):
                tester.log(f"{i}. {error.get('name', 'Unknown')}", "ERROR")
                if "error" in error:
                    tester.log(f"   错误: {error['error']}", "ERROR")
                else:
                    tester.log(f"   期望: {error.get('expected')}, 实际: {error.get('actual')}", "ERROR")
        
        success_rate = (tester.results['passed'] / (tester.results['passed'] + tester.results['failed'])) * 100
        tester.log(f"\n成功率: {success_rate:.1f}%", "SUCCESS" if success_rate >= 80 else "WARNING")
        
    finally:
        await tester.close()


if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════╗
║        超星学习通 API 完整测试脚本                        ║
║                                                           ║
║  确保后端服务已启动: python run_app.py                   ║
║  测试端点: http://localhost:8000                          ║
╚═══════════════════════════════════════════════════════════╝
""")
    
    try:
        asyncio.run(run_tests())
    except KeyboardInterrupt:
        print("\n\n测试已取消")
    except Exception as e:
        print(f"\n\n测试出错: {e}")
        import traceback
        traceback.print_exc()

