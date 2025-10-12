import React, { useState, useEffect } from 'react';
import {
  Card,
  Form,
  Input,
  Button,
  Alert,
  Progress,
  Steps,
  Space,
  Typography,
  Divider,
  Modal,
  Descriptions,
  Tag,
  message,
  Table,
  Collapse
} from 'antd';
import {
  DatabaseOutlined,
  CheckCircleOutlined,
  LoadingOutlined,
  WarningOutlined,
  SyncOutlined,
  InfoCircleOutlined,
  ReloadOutlined
} from '@ant-design/icons';
import { useApiUrl } from '@refinedev/core';
import axios from 'axios';

const { Title, Text, Paragraph } = Typography;

interface CurrentConfig {
  deploy_mode: string;
  database_type: string;
  database_url: string;
  broker_type: string;
  celery_broker: string;
  celery_result_backend: string;
}

interface MigrationStatus {
  is_running: boolean;
  current_step: string;
  progress: number;
  message: string;
  result: any;
  error: string | null;
}

export const DatabaseMigration: React.FC = () => {
  const apiUrl = useApiUrl();
  const [form] = Form.useForm();
  
  const [currentConfig, setCurrentConfig] = useState<CurrentConfig | null>(null);
  const [migrationStatus, setMigrationStatus] = useState<MigrationStatus | null>(null);
  const [loading, setLoading] = useState(false);
  const [testingPG, setTestingPG] = useState(false);
  const [testingRedis, setTestingRedis] = useState(false);
  const [pgTestResult, setPgTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [redisTestResult, setRedisTestResult] = useState<{ success: boolean; message: string } | null>(null);
  const [showConfirmModal, setShowConfirmModal] = useState(false);
  const [migrationFormData, setMigrationFormData] = useState<any>(null);
  
  // 获取访问令牌
  const getToken = () => localStorage.getItem('token');
  
  // 加载当前配置
  const loadCurrentConfig = async () => {
    try {
      const response = await axios.get(`${apiUrl}/migration/current-config`, {
        headers: { Authorization: `Bearer ${getToken()}` }
      });
      setCurrentConfig(response.data);
    } catch (error: any) {
      message.error('加载当前配置失败: ' + (error.response?.data?.detail || error.message));
    }
  };
  
  // 轮询迁移状态
  useEffect(() => {
    loadCurrentConfig();
    
    const interval = setInterval(async () => {
      try {
        const response = await axios.get(`${apiUrl}/migration/status`, {
          headers: { Authorization: `Bearer ${getToken()}` }
        });
        setMigrationStatus(response.data);
        
        // 如果迁移完成或失败，停止轮询
        if (response.data.is_running === false && response.data.progress === 100) {
          // 迁移成功完成
          message.success('数据库迁移成功完成！');
        }
      } catch (error) {
        // 忽略错误
      }
    }, 2000); // 每2秒轮询一次
    
    return () => clearInterval(interval);
  }, [apiUrl]);
  
  // 测试PostgreSQL连接
  const testPostgreSQLConnection = async () => {
    const database_url = form.getFieldValue('database_url');
    if (!database_url) {
      message.warning('请先输入PostgreSQL数据库URL');
      return;
    }
    
    setTestingPG(true);
    setPgTestResult(null);
    
    try {
      const response = await axios.post(
        `${apiUrl}/migration/test-postgresql`,
        { database_url },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      
      setPgTestResult({ success: true, message: response.data.message });
      message.success('PostgreSQL连接测试成功！');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message;
      setPgTestResult({ success: false, message: errorMsg });
      message.error('PostgreSQL连接测试失败: ' + errorMsg);
    } finally {
      setTestingPG(false);
    }
  };
  
  // 测试Redis连接
  const testRedisConnection = async () => {
    const redis_url = form.getFieldValue('redis_url');
    if (!redis_url) {
      message.warning('请先输入Redis URL');
      return;
    }
    
    setTestingRedis(true);
    setRedisTestResult(null);
    
    try {
      const response = await axios.post(
        `${apiUrl}/migration/test-redis`,
        { redis_url },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      
      setRedisTestResult({ success: true, message: response.data.message });
      message.success('Redis连接测试成功！');
    } catch (error: any) {
      const errorMsg = error.response?.data?.detail || error.message;
      setRedisTestResult({ success: false, message: errorMsg });
      message.error('Redis连接测试失败: ' + errorMsg);
    } finally {
      setTestingRedis(false);
    }
  };
  
  // 开始迁移
  const startMigration = async (values: any) => {
    setMigrationFormData(values);
    setShowConfirmModal(true);
  };
  
  // 确认并执行迁移
  const confirmMigration = async () => {
    setShowConfirmModal(false);
    setLoading(true);
    
    try {
      const response = await axios.post(
        `${apiUrl}/migration/start`,
        {
          target_database_url: migrationFormData.database_url,
          redis_url: migrationFormData.redis_url,
          confirm: true
        },
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      
      message.success(response.data.message);
      message.warning(response.data.warning, 10);
    } catch (error: any) {
      message.error('启动迁移失败: ' + (error.response?.data?.detail || error.message));
    } finally {
      setLoading(false);
    }
  };
  
  // 重置迁移状态
  const resetMigrationStatus = async () => {
    try {
      await axios.post(
        `${apiUrl}/migration/reset-status`,
        {},
        { headers: { Authorization: `Bearer ${getToken()}` } }
      );
      message.success('迁移状态已重置');
      setMigrationStatus(null);
    } catch (error: any) {
      message.error('重置失败: ' + (error.response?.data?.detail || error.message));
    }
  };
  
  // 获取当前步骤
  const getCurrentStep = () => {
    if (!migrationStatus) return 0;
    if (migrationStatus.progress < 10) return 0;
    if (migrationStatus.progress < 25) return 1;
    if (migrationStatus.progress < 70) return 2;
    if (migrationStatus.progress < 90) return 3;
    if (migrationStatus.progress < 100) return 4;
    return 5;
  };
  
  const isCurrentlySQLite = currentConfig?.database_type === 'SQLite';
  const canMigrate = isCurrentlySQLite && !migrationStatus?.is_running;

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        <DatabaseOutlined /> 数据库迁移管理
      </Title>
      
      <Paragraph type="secondary">
        将当前的SQLite数据库迁移到PostgreSQL + Redis，适合大规模部署（50+用户）
      </Paragraph>
      
      <Space direction="vertical" size="large" style={{ width: '100%' }}>
        {/* 当前配置 */}
        <Card title="当前数据库配置" extra={<Button icon={<ReloadOutlined />} onClick={loadCurrentConfig}>刷新</Button>}>
          {currentConfig ? (
            <Descriptions bordered column={1}>
              <Descriptions.Item label="部署模式">
                <Tag color={currentConfig.deploy_mode === 'simple' ? 'blue' : 'green'}>
                  {currentConfig.deploy_mode === 'simple' ? '简单模式' : '标准模式'}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="数据库类型">
                <Tag color={currentConfig.database_type === 'SQLite' ? 'orange' : 'green'}>
                  {currentConfig.database_type}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="数据库URL">
                <Text code>{currentConfig.database_url}</Text>
              </Descriptions.Item>
              <Descriptions.Item label="消息队列">
                <Tag color={currentConfig.broker_type === '文件系统' ? 'orange' : 'green'}>
                  {currentConfig.broker_type}
                </Tag>
              </Descriptions.Item>
              <Descriptions.Item label="Celery Broker">
                <Text code>{currentConfig.celery_broker}</Text>
              </Descriptions.Item>
            </Descriptions>
          ) : (
            <p>加载中...</p>
          )}
          
          {isCurrentlySQLite && (
            <Alert
              message="当前使用SQLite数据库"
              description="SQLite适合20-30人以下使用。如果您的用户规模超过50人，建议迁移到PostgreSQL + Redis以获得更好的性能。"
              type="info"
              showIcon
              icon={<InfoCircleOutlined />}
              style={{ marginTop: 16 }}
            />
          )}
          
          {!isCurrentlySQLite && (
            <Alert
              message="当前已使用PostgreSQL"
              description="您的系统已经在使用PostgreSQL + Redis，无需迁移。"
              type="success"
              showIcon
              icon={<CheckCircleOutlined />}
              style={{ marginTop: 16 }}
            />
          )}
        </Card>
        
        {/* 迁移状态 */}
        {migrationStatus && (migrationStatus.is_running || migrationStatus.progress > 0) && (
          <Card 
            title={
              <Space>
                {migrationStatus.is_running ? <LoadingOutlined /> : <SyncOutlined />}
                迁移进度
              </Space>
            }
            extra={
              !migrationStatus.is_running && migrationStatus.progress === 100 && (
                <Button onClick={resetMigrationStatus}>重置状态</Button>
              )
            }
          >
            <Steps 
              current={getCurrentStep()} 
              size="small" 
              style={{ marginBottom: 24 }}
              items={[
                { title: '准备', description: '测试连接' },
                { title: '备份', description: '备份SQLite' },
                { title: '迁移', description: '迁移数据' },
                { title: '验证', description: '验证数据' },
                { title: '更新配置', description: '更新.env' },
                { title: '完成', description: '等待重启' },
              ]}
            />
            
            <Progress 
              percent={migrationStatus.progress} 
              status={migrationStatus.error ? 'exception' : (migrationStatus.progress === 100 ? 'success' : 'active')}
              strokeColor={migrationStatus.error ? '#ff4d4f' : undefined}
            />
            
            <div style={{ marginTop: 16 }}>
              <Text strong>当前步骤：</Text> {migrationStatus.current_step || '准备中'}
            </div>
            <div style={{ marginTop: 8 }}>
              <Text strong>状态信息：</Text> {migrationStatus.message || '等待开始...'}
            </div>
            
            {migrationStatus.error && (
              <Alert
                message="迁移失败"
                description={migrationStatus.error}
                type="error"
                showIcon
                style={{ marginTop: 16 }}
              />
            )}
            
            {migrationStatus.result && migrationStatus.result.success && (
              <Alert
                message="迁移成功！"
                description={
                  <div>
                    <p>✅ 备份文件: {migrationStatus.result.backup_file}</p>
                    <p>✅ 迁移记录数: {migrationStatus.result.migrated_records}</p>
                    <p>⚠️ 请重启服务以使用新数据库配置</p>
                  </div>
                }
                type="success"
                showIcon
                style={{ marginTop: 16 }}
              />
            )}
            
            {migrationStatus.result?.verification && (
              <Collapse 
                style={{ marginTop: 16 }}
                items={[
                  {
                    key: '1',
                    label: '验证详情',
                    children: (
                      <Table
                        size="small"
                        dataSource={Object.entries(migrationStatus.result.verification.details).map(([table, data]: [string, any]) => ({
                          table,
                          ...data
                        }))}
                        columns={[
                          { title: '表名', dataIndex: 'table', key: 'table' },
                          { title: '源记录数', dataIndex: 'source_count', key: 'source_count' },
                          { title: '目标记录数', dataIndex: 'target_count', key: 'target_count' },
                          {
                            title: '状态',
                            dataIndex: 'match',
                            key: 'match',
                            render: (match: boolean) => (
                              <Tag color={match ? 'success' : 'error'}>
                                {match ? '✅ 一致' : '❌ 不一致'}
                              </Tag>
                            )
                          }
                        ]}
                        pagination={false}
                      />
                    ),
                  },
                ]}
              />
            )}
          </Card>
        )}
        
        {/* 迁移配置表单 */}
        {canMigrate && (
          <Card title="配置PostgreSQL和Redis">
            <Alert
              message="迁移前请确保"
              description={
                <ul>
                  <li>✅ 已安装PostgreSQL数据库服务器</li>
                  <li>✅ 已安装Redis服务器</li>
                  <li>✅ 已创建PostgreSQL数据库和用户</li>
                  <li>✅ 已备份当前SQLite数据库</li>
                  <li>⚠️ 迁移过程中服务将不可用（约1-5分钟）</li>
                  <li>⚠️ 迁移完成后需要手动重启服务</li>
                </ul>
              }
              type="warning"
              showIcon
              icon={<WarningOutlined />}
              style={{ marginBottom: 24 }}
            />
            
            <Form
              form={form}
              layout="vertical"
              onFinish={startMigration}
              initialValues={{
                database_url: 'postgresql+asyncpg://chaoxing_user:password@localhost:5432/chaoxing_db',
                redis_url: 'redis://:password@localhost:6379/0'
              }}
            >
              <Form.Item
                label="PostgreSQL数据库URL"
                name="database_url"
                rules={[{ required: true, message: '请输入PostgreSQL数据库URL' }]}
                extra="格式: postgresql+asyncpg://用户名:密码@主机:端口/数据库名"
              >
                <Input.TextArea 
                  rows={2}
                  placeholder="postgresql+asyncpg://chaoxing_user:password@localhost:5432/chaoxing_db"
                />
              </Form.Item>
              
              <Form.Item>
                <Space>
                  <Button
                    icon={<CheckCircleOutlined />}
                    onClick={testPostgreSQLConnection}
                    loading={testingPG}
                  >
                    测试PostgreSQL连接
                  </Button>
                  
                  {pgTestResult && (
                    <Tag color={pgTestResult.success ? 'success' : 'error'}>
                      {pgTestResult.success ? '✅' : '❌'} {pgTestResult.message}
                    </Tag>
                  )}
                </Space>
              </Form.Item>
              
              <Divider />
              
              <Form.Item
                label="Redis URL"
                name="redis_url"
                rules={[{ required: true, message: '请输入Redis URL' }]}
                extra="格式: redis://:密码@主机:端口/数据库编号"
              >
                <Input.TextArea 
                  rows={2}
                  placeholder="redis://:password@localhost:6379/0"
                />
              </Form.Item>
              
              <Form.Item>
                <Space>
                  <Button
                    icon={<CheckCircleOutlined />}
                    onClick={testRedisConnection}
                    loading={testingRedis}
                  >
                    测试Redis连接
                  </Button>
                  
                  {redisTestResult && (
                    <Tag color={redisTestResult.success ? 'success' : 'error'}>
                      {redisTestResult.success ? '✅' : '❌'} {redisTestResult.message}
                    </Tag>
                  )}
                </Space>
              </Form.Item>
              
              <Divider />
              
              <Form.Item>
                <Space>
                  <Button
                    type="primary"
                    htmlType="submit"
                    icon={<SyncOutlined />}
                    loading={loading}
                    disabled={!pgTestResult?.success || !redisTestResult?.success}
                    danger
                  >
                    开始迁移
                  </Button>
                  
                  <Text type="secondary">
                    请先测试两个连接都成功后再开始迁移
                  </Text>
                </Space>
              </Form.Item>
            </Form>
          </Card>
        )}
        
        {/* 迁移说明 */}
        <Card title="迁移说明">
          <Collapse
            items={[
              {
                key: 'steps',
                label: '📝 迁移步骤说明',
                children: (
                  <ol>
                    <li><strong>准备阶段</strong>：测试目标数据库连接是否正常</li>
                    <li><strong>备份阶段</strong>：自动备份当前SQLite数据库到backups目录</li>
                    <li><strong>创建表</strong>：在PostgreSQL中创建所有表结构</li>
                    <li><strong>迁移数据</strong>：将所有数据从SQLite复制到PostgreSQL</li>
                    <li><strong>验证数据</strong>：对比两个数据库的记录数，确保一致</li>
                    <li><strong>更新配置</strong>：自动修改.env文件，切换到PostgreSQL</li>
                    <li><strong>重启服务</strong>：需要手动重启后端和Celery服务</li>
                  </ol>
                ),
              },
              {
                key: 'warnings',
                label: '⚠️ 注意事项',
                children: (
                  <ul>
                    <li>迁移过程中系统将不可用，请选择业务低峰期进行</li>
                    <li>迁移时间取决于数据量，通常1-5分钟</li>
                    <li>确保PostgreSQL和Redis服务正常运行</li>
                    <li>建议先在测试环境验证迁移流程</li>
                    <li>迁移前请确保有足够的磁盘空间</li>
                    <li>原SQLite数据库会自动备份，不会被删除</li>
                  </ul>
                ),
              },
              {
                key: 'restart',
                label: '🔄 如何重启服务',
                children: (
                  <>
                    <Paragraph>
                      <Title level={5}>Windows环境：</Title>
                      <pre>
{`# 停止当前服务（Ctrl+C）
# 然后重新运行：
cd web/backend
python app.py

# 新终端
cd web/backend  
celery -A celery_app worker --loglevel=info`}
                      </pre>
                    </Paragraph>
                    
                    <Paragraph>
                      <Title level={5}>Linux/Docker环境：</Title>
                      <pre>
{`# Docker Compose
docker-compose restart backend celery

# 或手动重启
sudo systemctl restart chaoxing-backend
sudo systemctl restart chaoxing-celery`}
                      </pre>
                    </Paragraph>
                  </>
                ),
              },
              {
                key: 'faq',
                label: '❓ 常见问题',
                children: (
                  <>
                    <Paragraph>
                      <Text strong>Q: 迁移失败怎么办？</Text><br />
                      A: 系统会自动备份原数据库，可以回滚。检查错误日志，修复问题后重试。
                    </Paragraph>
                    
                    <Paragraph>
                      <Text strong>Q: 迁移后发现数据不对？</Text><br />
                      A: 可以手动将备份的.db文件恢复，然后修改.env文件切回SQLite。
                    </Paragraph>
                    
                    <Paragraph>
                      <Text strong>Q: 可以从PostgreSQL迁回SQLite吗？</Text><br />
                      A: 理论上可以，但不推荐。建议保留SQLite备份文件。
                    </Paragraph>
                  </>
                ),
              },
            ]}
          />
        </Card>
      </Space>
      
      {/* 确认对话框 */}
      <Modal
        title="⚠️ 确认迁移"
        open={showConfirmModal}
        onOk={confirmMigration}
        onCancel={() => setShowConfirmModal(false)}
        okText="确认迁移"
        cancelText="取消"
        okButtonProps={{ danger: true }}
      >
        <Alert
          message="重要提示"
          description={
            <div>
              <p><strong>您即将执行数据库迁移操作，此操作将：</strong></p>
              <ul>
                <li>✅ 自动备份当前SQLite数据库</li>
                <li>🔄 将所有数据迁移到PostgreSQL</li>
                <li>⚙️ 自动修改.env配置文件</li>
                <li>⚠️ 需要您手动重启服务</li>
              </ul>
              <p style={{ marginTop: 16 }}>
                <strong>目标配置：</strong>
              </p>
              <p><Text code>{migrationFormData?.database_url}</Text></p>
              <p><Text code>{migrationFormData?.redis_url}</Text></p>
              <p style={{ marginTop: 16, color: 'red' }}>
                <WarningOutlined /> 迁移过程中系统将不可用，确定要继续吗？
              </p>
            </div>
          }
          type="warning"
          showIcon
        />
      </Modal>
    </div>
  );
};

