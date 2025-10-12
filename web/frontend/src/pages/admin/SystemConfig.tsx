import { useState, useEffect } from 'react';
import { Card, Form, Input, InputNumber, Switch, Button, message, Tabs, Alert, Space, Descriptions } from 'antd';
import { SaveOutlined, ReloadOutlined, MailOutlined, SettingOutlined, ThunderboltOutlined } from '@ant-design/icons';
import { axiosInstance } from '../../providers/authProvider';

export const SystemConfig = () => {
  const [smtpForm] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [testLoading, setTestLoading] = useState(false);
  const [templates, setTemplates] = useState<any[]>([]);
  const [currentConfig, setCurrentConfig] = useState<any>(null);

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

  useEffect(() => {
    loadSMTPConfig();
    loadTemplates();
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
      const response = await axiosInstance.post('/system-config/smtp/test');
      message.success(response.data.message || 'SMTP测试成功');
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
                    <Button
                      icon={<ThunderboltOutlined />}
                      onClick={testSMTP}
                      loading={testLoading}
                    >
                      测试SMTP
                    </Button>
                  </Space>
                </Form.Item>
              </Form>
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
                      v2.2.1
                    </Descriptions.Item>
                  </Descriptions>

                  <Card title="配置选项" size="small" style={{ marginBottom: 16 }}>
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
                          支持5种题库：言溪、LIKE知识库、TikuAdapter、AI大模型、硅基流动AI
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

