import { useState, useEffect } from 'react';
import { Card, Form, Input, InputNumber, Switch, Button, message, Tabs, Alert, Space, Descriptions, Tag } from 'antd';
import { SaveOutlined, ReloadOutlined, MailOutlined, SettingOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { axiosInstance } from '../../providers/authProvider';

export const SystemConfig = () => {
  const [smtpForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [templates, setTemplates] = useState<any[]>([]);
  const [currentConfig, setCurrentConfig] = useState<any>(null);
  const [testEmail, setTestEmail] = useState<string>('');
  const [systemParams, setSystemParams] = useState<any>(null);
  const [editableConfigs, setEditableConfigs] = useState<any>(null);
  const [editingConfig, setEditingConfig] = useState<{[key: string]: any}>({});

  // 加载SMTP配置
  const loadSMTPConfig = async () => {
    try {
      const response = await axiosInstance.get('/system-config/smtp');
      setCurrentConfig(response.data);
      smtpForm.setFieldsValue(response.data);
    } catch (error: any) {
      message.error('加载配置失败');
    }
  };

  // 加载SMTP模板
  const loadTemplates = async () => {
    try {
      const response = await axiosInstance.get('/system-config/smtp-templates');
      setTemplates(response.data.templates || []);
    } catch (error: any) {
      console.error('加载模板失败:', error);
    }
  };

  // 加载系统参数
  const loadSystemParams = async () => {
    try {
      const response = await axiosInstance.get('/system-config/system-params');
      setSystemParams(response.data);
    } catch (error: any) {
      console.error('加载系统参数失败:', error);
    }
  };

  // 加载可编辑配置
  const loadEditableConfigs = async () => {
    try {
      const response = await axiosInstance.get('/system-config/editable-configs');
      setEditableConfigs(response.data.configs);
    } catch (error: any) {
      console.error('加载可编辑配置失败:', error);
    }
  };

  // 更新单个配置
  const updateConfig = async (key: string, value: any) => {
    try {
      setLoading(true);
      await axiosInstance.put('/system-config/editable-config', { key, value });
      message.success(`配置 ${key} 已更新`);
      loadEditableConfigs();
      setEditingConfig({});
    } catch (error: any) {
      message.error(error.response?.data?.detail || '更新失败');
    } finally {
      setLoading(false);
    }
  };

  // 初始化可编辑配置
  const initEditableConfigs = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.post('/system-config/init-editable-configs');
      message.success(response.data.message);
      loadEditableConfigs();
    } catch (error: any) {
      message.error('初始化失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadSMTPConfig();
    loadTemplates();
    loadSystemParams();
    loadEditableConfigs();
  }, []);

  // 保存SMTP配置
  const saveSMTPConfig = async (values: any) => {
    try {
      setLoading(true);
      await axiosInstance.put('/system-config/smtp', values);
      message.success('SMTP配置已保存');
      loadSMTPConfig();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  // 测试SMTP
  const testSMTP = async () => {
    try {
      setTestLoading(true);
      const payload = testEmail ? { to_email: testEmail } : {};
      const response = await axiosInstance.post('/system-config/smtp/test', payload);
      message.success(response.data.detail || response.data.message || 'SMTP测试成功');
    } catch (error: any) {
      message.error(error.response?.data?.detail || 'SMTP测试失败');
    } finally {
      setTestLoading(false);
    }
  };

  // 应用模板
  const applyTemplate = (template: any) => {
    smtpForm.setFieldsValue({
      smtp_host: template.smtp_host,
      smtp_port: template.smtp_port,
      smtp_use_tls: template.smtp_use_tls,
    });
    message.info(`已应用${template.name}配置模板`);
  };

  // 初始化默认配置
  const initDefaults = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.post('/system-config/init-defaults');
      message.success(response.data.message);
      loadSMTPConfig();
    } catch (error: any) {
      message.error('初始化失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: 24 }}>
      <Card
        title={
          <Space>
            <SettingOutlined />
            <span>系统配置</span>
          </Space>
        }
        extra={
          <Button icon={<ReloadOutlined />} onClick={loadSMTPConfig}>
            刷新
          </Button>
        }
      >
        <Alert
          message="管理员专用"
          description="这里可以配置系统级参数，包括SMTP邮件服务、任务限制等。修改后立即生效。"
          type="info"
          showIcon
          style={{ marginBottom: 24 }}
        />

        <Tabs 
          defaultActiveKey="smtp"
          items={[
            {
              key: 'editable',
              label: (
                <span>
                  <ThunderboltOutlined />
                  在线配置
                </span>
              ),
              children: (
                <Card>
                  <Alert
                    message="在线配置管理"
                    description="这些配置可以在线修改并立即生效，无需重启服务。"
                    type="success"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  {!editableConfigs && (
                    <Button onClick={initEditableConfigs} type="primary" icon={<SettingOutlined />}>
                      初始化配置
                    </Button>
                  )}

                  {editableConfigs && (
                    <>
                      <Descriptions bordered column={1} size="small">
                        {Object.entries(editableConfigs).map(([key, config]: [string, any]) => (
                          <Descriptions.Item
                            key={key}
                            label={
                              <div>
                                <strong>{config.description}</strong>
                                <div style={{ fontSize: 11, color: '#999', marginTop: 4 }}>
                                  {key}
                                </div>
                              </div>
                            }
                          >
                            <Space>
                              {editingConfig[key] !== undefined ? (
                                <>
                                  <InputNumber
                                    value={editingConfig[key]}
                                    onChange={(value) => setEditingConfig({ ...editingConfig, [key]: value })}
                                    min={config.min}
                                    max={config.max}
                                    style={{ width: 150 }}
                                  />
                                  <Button
                                    type="primary"
                                    size="small"
                                    onClick={() => updateConfig(key, editingConfig[key])}
                                    loading={loading}
                                  >
                                    保存
                                  </Button>
                                  <Button
                                    size="small"
                                    onClick={() => {
                                      const newEditing = { ...editingConfig };
                                      delete newEditing[key];
                                      setEditingConfig(newEditing);
                                    }}
                                  >
                                    取消
                                  </Button>
                                </>
                              ) : (
                                <>
                                  <strong style={{ color: '#1890ff' }}>{config.value}</strong>
                                  <span style={{ color: '#999', fontSize: 12 }}>
                                    (默认: {config.default}, 范围: {config.min}-{config.max})
                                  </span>
                                  <Button
                                    type="link"
                                    size="small"
                                    onClick={() => setEditingConfig({ ...editingConfig, [key]: config.value })}
                                  >
                                    修改
                                  </Button>
                                </>
                              )}
                            </Space>
                          </Descriptions.Item>
                        ))}
                      </Descriptions>

                      <Alert
                        message="配置说明"
                        description={
                          <ul style={{ marginBottom: 0, paddingLeft: 20 }}>
                            <li>修改后立即生效，无需重启服务</li>
                            <li>所有用户的新任务将使用新配置</li>
                            <li>已创建的任务不受影响</li>
                          </ul>
                        }
                        type="info"
                        showIcon
                        style={{ marginTop: 16 }}
                      />
                    </>
                  )}
                </Card>
              ),
            },
            {
              key: 'smtp',
              label: (
                <span>
                  <MailOutlined />
                  SMTP邮件配置
                </span>
              ),
              children: (
                <>
            <Card title="SMTP服务器配置" style={{ marginBottom: 16 }}>
              <Form
                form={smtpForm}
                layout="vertical"
                onFinish={saveSMTPConfig}
                initialValues={{
                  smtp_enabled: false,
                  smtp_port: 587,
                  smtp_use_tls: true,
                  smtp_from_name: '超星学习通',
                }}
              >
                <Form.Item
                  name="smtp_enabled"
                  label="启用SMTP"
                  valuePropName="checked"
                  extra="开启后才会发送邮件（注册验证、密码重置等）"
                >
                  <Switch />
                </Form.Item>

                <Form.Item
                  label="SMTP服务器"
                  name="smtp_host"
                  rules={[{ required: true, message: '请输入SMTP服务器地址' }]}
                >
                  <Input placeholder="例如: smtp.gmail.com" />
                </Form.Item>

                <Form.Item
                  label="SMTP端口"
                  name="smtp_port"
                  rules={[{ required: true, message: '请输入SMTP端口' }]}
                >
                  <InputNumber min={1} max={65535} style={{ width: '100%' }} />
                </Form.Item>

                <Form.Item
                  label="SMTP用户名"
                  name="smtp_username"
                  rules={[{ required: true, message: '请输入SMTP用户名' }]}
                  extra="通常是您的邮箱地址"
                >
                  <Input placeholder="your_email@gmail.com" />
                </Form.Item>

                <Form.Item
                  label="SMTP密码"
                  name="smtp_password"
                  extra="Gmail请使用应用专用密码，留空则不修改"
                >
                  <Input.Password placeholder="留空则不修改当前密码" />
                </Form.Item>

                <Form.Item
                  label="发件人邮箱"
                  name="smtp_from_email"
                  rules={[
                    { required: true, message: '请输入发件人邮箱' },
                    { type: 'email', message: '请输入有效的邮箱地址' }
                  ]}
                >
                  <Input placeholder="your_email@gmail.com" />
                </Form.Item>

                <Form.Item
                  label="发件人名称"
                  name="smtp_from_name"
                  rules={[{ required: true, message: '请输入发件人名称' }]}
                >
                  <Input placeholder="超星学习通" />
                </Form.Item>

                <Form.Item
                  name="smtp_use_tls"
                  label="使用TLS"
                  valuePropName="checked"
                  extra="大多数SMTP服务器需要TLS加密"
                >
                  <Switch />
                </Form.Item>

                <Form.Item>
                  <Space>
                    <Button
                      type="primary"
                      htmlType="submit"
                      icon={<SaveOutlined />}
                      loading={loading}
                    >
                      保存配置
                    </Button>
                  </Space>
                </Form.Item>
              </Form>

              {/* SMTP测试区域 */}
              <Card title="测试SMTP配置" size="small" style={{ marginTop: 16, backgroundColor: '#f5f5f5' }}>
                <Alert
                  message="测试说明"
                  description="填写接收邮箱地址，留空则发送到当前管理员邮箱。请确保已保存SMTP配置后再测试。"
                  type="info"
                  showIcon
                  style={{ marginBottom: 16 }}
                />
                <Space.Compact style={{ width: '100%' }}>
                  <Input
                    placeholder="接收邮箱（留空发送到管理员邮箱）"
                    value={testEmail}
                    onChange={(e) => setTestEmail(e.target.value)}
                    type="email"
                    size="large"
                  />
                  <Button
                    type="primary"
                    icon={<ThunderboltOutlined />}
                    onClick={testSMTP}
                    loading={testLoading}
                    size="large"
                  >
                    发送测试邮件
                  </Button>
                </Space.Compact>
              </Card>
            </Card>

            {/* 快速配置模板 */}
            <Card title="快速配置模板" style={{ marginTop: 16 }}>
              <Alert
                message="选择邮箱提供商"
                description="点击下方按钮快速应用常用邮箱的SMTP配置"
                type="info"
                showIcon
                style={{ marginBottom: 16 }}
              />
              
              <Space wrap>
                {templates.map((template) => (
                  <Card
                    key={template.name}
                    size="small"
                    hoverable
                    onClick={() => applyTemplate(template)}
                    style={{ cursor: 'pointer', minWidth: 200 }}
                  >
                    <Card.Meta
                      title={template.name}
                      description={
                        <div>
                          <div>{template.smtp_host}:{template.smtp_port}</div>
                          <div style={{ fontSize: 12, color: '#999', marginTop: 4 }}>
                            {template.note}
                          </div>
                        </div>
                      }
                    />
                  </Card>
                ))}
              </Space>
            </Card>

            {/* 当前配置状态 */}
            {currentConfig && (
              <Card title="当前配置状态" style={{ marginTop: 16 }}>
                <Descriptions bordered column={2}>
                  <Descriptions.Item label="SMTP状态">
                    {currentConfig.smtp_enabled ? (
                      <span style={{ color: '#52c41a' }}>✅ 已启用</span>
                    ) : (
                      <span style={{ color: '#999' }}>⭕ 未启用</span>
                    )}
                  </Descriptions.Item>
                  <Descriptions.Item label="服务器">
                    {currentConfig.smtp_host || '(未配置)'}
                  </Descriptions.Item>
                  <Descriptions.Item label="端口">
                    {currentConfig.smtp_port || '(未配置)'}
                  </Descriptions.Item>
                  <Descriptions.Item label="用户名">
                    {currentConfig.smtp_username || '(未配置)'}
                  </Descriptions.Item>
                  <Descriptions.Item label="密码">
                    {currentConfig.smtp_password ? '***已配置***' : '(未配置)'}
                  </Descriptions.Item>
                  <Descriptions.Item label="TLS">
                    {currentConfig.smtp_use_tls ? '✅ 启用' : '⭕ 禁用'}
                  </Descriptions.Item>
                </Descriptions>
              </Card>
            )}
                </>
              ),
            },
            {
              key: 'system',
              label: (
                <span>
                  <SettingOutlined />
                  系统设置
                </span>
              ),
              children: (
                <Card>
                  <Alert
                    message="系统配置管理"
                    description="管理系统级配置，修改后立即生效"
                    type="info"
                    showIcon
                    style={{ marginBottom: 24 }}
                  />

                  <Descriptions bordered column={1} style={{ marginBottom: 24 }}>
                    <Descriptions.Item label="前端地址">
                      {window.location.origin}
                    </Descriptions.Item>
                    <Descriptions.Item label="后端API">
                      {window.location.protocol}//{window.location.hostname}:5000
                    </Descriptions.Item>
                    <Descriptions.Item label="配置版本">
                      v2.5.4
                    </Descriptions.Item>
                  </Descriptions>

                  {systemParams && (
                    <Card title="系统参数（只读）" size="small" style={{ marginBottom: 16 }}>
                      <Alert
                        message="参数说明"
                        description="这些参数从.env配置文件读取，无法在线修改。如需修改，请编辑.env文件并重启服务。"
                        type="warning"
                        showIcon
                        style={{ marginBottom: 16 }}
                      />
                      
                      <Descriptions bordered column={2} size="small">
                        <Descriptions.Item label="应用名称" span={2}>
                          {systemParams.app?.name}
                        </Descriptions.Item>
                        <Descriptions.Item label="版本">
                          {systemParams.app?.version}
                        </Descriptions.Item>
                        <Descriptions.Item label="调试模式">
                          {systemParams.app?.debug ? '✅ 开启' : '⭕ 关闭'}
                        </Descriptions.Item>
                        <Descriptions.Item label="部署模式">
                          <Tag color={systemParams.deploy?.mode === 'simple' ? 'blue' : 'green'}>
                            {systemParams.deploy?.mode === 'simple' ? '简单模式 (SQLite)' : '标准模式 (PostgreSQL)'}
                          </Tag>
                        </Descriptions.Item>
                        <Descriptions.Item label="监听端口">
                          {systemParams.app?.host}:{systemParams.app?.port}
                        </Descriptions.Item>
                        <Descriptions.Item label="每用户最大并发任务">
                          {systemParams.task?.max_concurrent_tasks_per_user}
                        </Descriptions.Item>
                        <Descriptions.Item label="任务超时时间">
                          {systemParams.task?.task_timeout} 秒 ({Math.floor(systemParams.task?.task_timeout / 60)}分钟)
                        </Descriptions.Item>
                        <Descriptions.Item label="默认分页大小">
                          {systemParams.pagination?.default_page_size}
                        </Descriptions.Item>
                        <Descriptions.Item label="最大分页大小">
                          {systemParams.pagination?.max_page_size}
                        </Descriptions.Item>
                        <Descriptions.Item label="JWT过期时间">
                          {systemParams.security?.jwt_expire_minutes} 分钟
                        </Descriptions.Item>
                        <Descriptions.Item label="邮箱验证过期">
                          {systemParams.security?.email_verification_expire_minutes} 分钟
                        </Descriptions.Item>
                      </Descriptions>
                    </Card>
                  )}

                  <Card title="功能列表" size="small" style={{ marginBottom: 16 }}>
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div>
                        <strong>✅ SMTP邮件配置</strong>
                        <div style={{ color: '#666', fontSize: 12 }}>
                          支持邮箱验证、密码重置、系统通知邮件
                        </div>
                      </div>
                      
                      <div>
                        <strong>✅ 用户题库配置</strong>
                        <div style={{ color: '#666', fontSize: 12 }}>
                          支持6种题库：言溪、LIKE知识库、TikuAdapter、AI大模型、DeepSeek🔥、硅基流动⚡
                        </div>
                        <div style={{ color: '#999', fontSize: 11, marginTop: 4 }}>
                          AI/DeepSeek/硅基流动支持在线验证🧪
                        </div>
                      </div>
                      
                      <div>
                        <strong>✅ 用户通知配置</strong>
                        <div style={{ color: '#666', fontSize: 12 }}>
                          支持Server酱、Qmsg、Bark、SMTP邮件通知
                        </div>
                      </div>

                      <div>
                        <strong>✅ 数据库迁移</strong>
                        <div style={{ color: '#666', fontSize: 12 }}>
                          图形化界面迁移SQLite到PostgreSQL
                        </div>
                      </div>
                      
                      <div>
                        <strong>✅ 任务自动恢复</strong>
                        <div style={{ color: '#666', fontSize: 12 }}>
                          系统崩溃后自动恢复运行中任务，管理员可手动触发
                        </div>
                      </div>
                    </Space>
                  </Card>

                  <Card title="高级操作" size="small">
                    <Space>
                      <Button onClick={initDefaults} type="default">
                        初始化默认配置
                      </Button>
                      <Button 
                        type="link" 
                        onClick={() => window.open('/admin/database-migration', '_self')}
                      >
                        数据库迁移
                      </Button>
                    </Space>
                  </Card>
                </Card>
              ),
            },
          ]}
        />
      </Card>
    </div>
  );
};

