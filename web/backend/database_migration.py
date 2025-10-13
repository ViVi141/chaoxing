# -*- coding: utf-8 -*-
"""
数据库迁移工具 - SQLite迁移到PostgreSQL
支持Web界面调用，带进度回调
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

import json
import asyncio
from typing import Optional, Callable, Dict, Any
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
import aiosqlite

from api.logger import logger
from models import (
    User,
    UserConfig,
    Task,
    TaskLog,
    SystemLog,
    EmailVerification,
    SystemConfig,
)


class DatabaseMigrationError(Exception):
    """迁移错误"""

    pass


class DatabaseMigrator:
    """数据库迁移器"""

    def __init__(
        self,
        source_db_url: str,
        target_db_url: str,
        progress_callback: Optional[Callable] = None,
    ):
        """
        初始化迁移器

        Args:
            source_db_url: 源数据库URL（SQLite）
            target_db_url: 目标数据库URL（PostgreSQL）
            progress_callback: 进度回调函数 callback(step, progress, message)
        """
        self.source_db_url = source_db_url
        self.target_db_url = target_db_url
        self.progress_callback = progress_callback

        # 表迁移顺序（考虑外键依赖）
        self.table_order = [
            "users",
            "user_configs",
            "tasks",
            "task_logs",
            "system_logs",
            "email_verifications",
            "system_configs",
        ]

        self.models_map = {
            "users": User,
            "user_configs": UserConfig,
            "tasks": Task,
            "task_logs": TaskLog,
            "system_logs": SystemLog,
            "email_verifications": EmailVerification,
            "system_configs": SystemConfig,
        }

    def _report_progress(self, step: str, progress: int, message: str):
        """报告进度"""
        logger.info(f"[迁移进度 {progress}%] {step}: {message}")
        if self.progress_callback:
            try:
                self.progress_callback(step, progress, message)
            except Exception as e:
                logger.warning(f"进度回调失败: {e}")

    async def test_target_connection(self) -> bool:
        """测试目标数据库连接"""
        try:
            engine = create_async_engine(self.target_db_url, echo=False)
            async with engine.connect() as conn:
                await conn.execute(text("SELECT 1"))
            await engine.dispose()
            logger.info("✅ 目标数据库连接测试成功")
            return True
        except Exception as e:
            logger.error(f"❌ 目标数据库连接测试失败: {e}")
            raise DatabaseMigrationError(f"无法连接到目标数据库: {str(e)}")

    async def backup_source_database(self, backup_path: str) -> str:
        """备份源数据库"""
        try:
            self._report_progress("备份", 5, "正在备份SQLite数据库...")

            # 提取SQLite文件路径
            if ":///" in self.source_db_url:
                db_file = self.source_db_url.split(":///")[-1]
                # 处理相对路径
                if db_file.startswith("./"):
                    db_file = db_file[2:]

                source_path = Path(db_file)
                if not source_path.exists():
                    raise DatabaseMigrationError(f"源数据库文件不存在: {source_path}")

                # 生成备份文件名
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_file = Path(backup_path) / f"chaoxing_backup_{timestamp}.db"
                backup_file.parent.mkdir(parents=True, exist_ok=True)

                # 复制文件
                import shutil

                shutil.copy2(source_path, backup_file)

                self._report_progress("备份", 10, f"备份完成: {backup_file}")
                logger.info(f"✅ 数据库备份成功: {backup_file}")
                return str(backup_file)
            else:
                raise DatabaseMigrationError("不支持的数据库URL格式")

        except Exception as e:
            logger.error(f"❌ 备份失败: {e}")
            raise DatabaseMigrationError(f"备份失败: {str(e)}")

    async def create_target_tables(self):
        """在目标数据库创建表结构"""
        try:
            self._report_progress("创建表", 15, "正在创建PostgreSQL表结构...")

            # 导入Base
            from database import Base

            # 创建异步引擎
            engine = create_async_engine(self.target_db_url, echo=False)

            # 创建所有表
            async with engine.begin() as conn:
                await conn.run_sync(Base.metadata.create_all)

            await engine.dispose()

            self._report_progress("创建表", 20, "表结构创建完成")
            logger.info("✅ 目标数据库表创建成功")

        except Exception as e:
            logger.error(f"❌ 创建表失败: {e}")
            raise DatabaseMigrationError(f"创建表失败: {str(e)}")

    async def migrate_table_data(
        self, table_name: str, source_session, target_session: AsyncSession
    ) -> int:
        """迁移单个表的数据"""
        try:
            model = self.models_map.get(table_name)
            if not model:
                logger.warning(f"跳过未知表: {table_name}")
                return 0

            # 从源数据库读取所有数据
            source_data = source_session.query(model).all()
            count = len(source_data)

            if count == 0:
                logger.info(f"表 {table_name} 无数据，跳过")
                return 0

            logger.info(f"开始迁移表 {table_name}，共 {count} 条记录")

            # 批量插入到目标数据库
            batch_size = 100
            for i in range(0, count, batch_size):
                batch = source_data[i : i + batch_size]

                # 转换为字典
                batch_dicts = []
                for item in batch:
                    # 获取所有列
                    item_dict = {}
                    for column in model.__table__.columns:
                        value = getattr(item, column.name)
                        item_dict[column.name] = value
                    batch_dicts.append(item_dict)

                # 批量插入
                for item_dict in batch_dicts:
                    new_obj = model(**item_dict)
                    target_session.add(new_obj)

                await target_session.flush()

                progress = min(99, int((i + batch_size) / count * 30) + 40)
                logger.debug(f"  已迁移 {min(i+batch_size, count)}/{count} 条")

            await target_session.commit()
            logger.info(f"✅ 表 {table_name} 迁移完成，共 {count} 条记录")
            return count

        except Exception as e:
            await target_session.rollback()
            logger.error(f"❌ 表 {table_name} 迁移失败: {e}")
            raise DatabaseMigrationError(f"表 {table_name} 迁移失败: {str(e)}")

    async def migrate_all_data(self):
        """迁移所有表数据"""
        try:
            self._report_progress("迁移数据", 25, "开始迁移数据...")

            # 创建源数据库连接（同步）
            source_engine = create_engine(
                self.source_db_url.replace("aiosqlite", "sqlite")
            )
            SourceSession = sessionmaker(bind=source_engine)
            source_session = SourceSession()

            # 创建目标数据库连接（异步）
            target_engine = create_async_engine(self.target_db_url, echo=False)
            TargetSessionLocal = async_sessionmaker(
                target_engine, class_=AsyncSession, expire_on_commit=False
            )

            total_migrated = 0

            async with TargetSessionLocal() as target_session:
                for idx, table_name in enumerate(self.table_order):
                    progress = 25 + int((idx / len(self.table_order)) * 45)
                    self._report_progress(
                        "迁移数据", progress, f"正在迁移表: {table_name}..."
                    )

                    count = await self.migrate_table_data(
                        table_name, source_session, target_session
                    )
                    total_migrated += count

            # 关闭连接
            source_session.close()
            source_engine.dispose()
            await target_engine.dispose()

            self._report_progress(
                "迁移数据", 70, f"数据迁移完成，共 {total_migrated} 条记录"
            )
            logger.info(f"✅ 所有数据迁移完成，共 {total_migrated} 条记录")

            return total_migrated

        except Exception as e:
            logger.error(f"❌ 数据迁移失败: {e}")
            raise DatabaseMigrationError(f"数据迁移失败: {str(e)}")

    async def verify_migration(self) -> Dict[str, Any]:
        """验证迁移结果"""
        try:
            self._report_progress("验证", 75, "正在验证迁移结果...")

            # 连接两个数据库
            source_engine = create_engine(
                self.source_db_url.replace("aiosqlite", "sqlite")
            )
            target_engine = create_async_engine(self.target_db_url, echo=False)

            verification_results = {}
            all_match = True

            async with target_engine.connect() as target_conn:
                with source_engine.connect() as source_conn:
                    for table_name in self.table_order:
                        # 源数据库计数
                        source_count = source_conn.execute(
                            text(f"SELECT COUNT(*) FROM {table_name}")
                        ).scalar()

                        # 目标数据库计数
                        target_count = await target_conn.execute(
                            text(f"SELECT COUNT(*) FROM {table_name}")
                        )
                        target_count = target_count.scalar()

                        match = source_count == target_count
                        verification_results[table_name] = {
                            "source_count": source_count,
                            "target_count": target_count,
                            "match": match,
                        }

                        if not match:
                            all_match = False
                            logger.warning(
                                f"⚠️ 表 {table_name} 记录数不匹配: "
                                f"源={source_count}, 目标={target_count}"
                            )
                        else:
                            logger.info(
                                f"✅ 表 {table_name} 验证通过: {source_count} 条记录"
                            )

            source_engine.dispose()
            await target_engine.dispose()

            if all_match:
                self._report_progress("验证", 85, "✅ 所有表验证通过")
                logger.info("✅ 迁移验证成功，所有数据一致")
            else:
                self._report_progress("验证", 85, "⚠️ 部分表记录数不匹配")
                logger.warning("⚠️ 迁移验证发现不一致")

            return {"all_match": all_match, "details": verification_results}

        except Exception as e:
            logger.error(f"❌ 验证失败: {e}")
            raise DatabaseMigrationError(f"验证失败: {str(e)}")

    async def update_env_file(
        self, env_file_path: str, postgres_url: str, redis_url: str
    ):
        """更新.env配置文件"""
        try:
            self._report_progress("更新配置", 90, "正在更新.env配置文件...")

            env_path = Path(env_file_path)

            # 读取现有配置
            if env_path.exists():
                with open(env_path, "r", encoding="utf-8") as f:
                    lines = f.readlines()
            else:
                lines = []

            # 更新配置项
            updates = {
                "DEPLOY_MODE": "standard",
                "DATABASE_URL": postgres_url,
                "CELERY_BROKER_URL": redis_url,
                "CELERY_RESULT_BACKEND": redis_url,
            }

            new_lines = []
            updated_keys = set()

            for line in lines:
                updated = False
                for key, value in updates.items():
                    if line.startswith(f"{key}=") or line.startswith(f"#{key}="):
                        new_lines.append(f"{key}={value}\n")
                        updated_keys.add(key)
                        updated = True
                        break
                if not updated:
                    new_lines.append(line)

            # 添加未找到的配置项
            for key, value in updates.items():
                if key not in updated_keys:
                    new_lines.append(f"\n# 自动迁移添加\n{key}={value}\n")

            # 写回文件
            with open(env_path, "w", encoding="utf-8") as f:
                f.writelines(new_lines)

            self._report_progress("更新配置", 95, "配置文件更新完成")
            logger.info(f"✅ .env配置文件已更新: {env_path}")

        except Exception as e:
            logger.error(f"❌ 更新配置文件失败: {e}")
            raise DatabaseMigrationError(f"更新配置文件失败: {str(e)}")

    async def run_full_migration(
        self, backup_path: str, env_file_path: str, redis_url: str
    ) -> Dict[str, Any]:
        """运行完整迁移流程"""
        migration_result = {
            "success": False,
            "backup_file": None,
            "migrated_records": 0,
            "verification": None,
            "error": None,
        }

        try:
            logger.info("=" * 60)
            logger.info("开始数据库迁移: SQLite -> PostgreSQL")
            logger.info("=" * 60)

            # 1. 测试目标数据库连接
            self._report_progress("准备", 0, "测试目标数据库连接...")
            await self.test_target_connection()

            # 2. 备份源数据库
            backup_file = await self.backup_source_database(backup_path)
            migration_result["backup_file"] = backup_file

            # 3. 创建目标表
            await self.create_target_tables()

            # 4. 迁移数据
            migrated_count = await self.migrate_all_data()
            migration_result["migrated_records"] = migrated_count

            # 5. 验证迁移
            verification = await self.verify_migration()
            migration_result["verification"] = verification

            # 6. 更新.env文件
            await self.update_env_file(env_file_path, self.target_db_url, redis_url)

            # 完成
            self._report_progress("完成", 100, "✅ 迁移完成！请重启服务使配置生效")
            logger.info("=" * 60)
            logger.info("✅ 数据库迁移成功完成！")
            logger.info(f"📦 备份文件: {backup_file}")
            logger.info(f"📊 迁移记录: {migrated_count} 条")
            logger.info("🔄 请重启服务以使用新数据库")
            logger.info("=" * 60)

            migration_result["success"] = True
            return migration_result

        except Exception as e:
            migration_result["error"] = str(e)
            logger.error("=" * 60)
            logger.error(f"❌ 迁移失败: {e}")
            logger.error("=" * 60)
            raise


# 测试函数
async def test_migration():
    """测试迁移功能"""
    source_url = "sqlite+aiosqlite:///./data/chaoxing.db"
    target_url = (
        "postgresql+asyncpg://chaoxing_user:password@localhost:5432/chaoxing_db"
    )

    def progress_callback(step, progress, message):
        print(f"[{progress}%] {step}: {message}")

    migrator = DatabaseMigrator(source_url, target_url, progress_callback)

    result = await migrator.run_full_migration(
        backup_path="./backups",
        env_file_path="./.env",
        redis_url="redis://localhost:6379/0",
    )

    print("\n迁移结果:")
    print(json.dumps(result, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    asyncio.run(test_migration())
