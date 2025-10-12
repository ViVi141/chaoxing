import { Card, Form, Input, InputNumber, Button, message, Tabs, Select, Switch, Divider, Typography, Alert } from 'antd';
import { SaveOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { axiosInstance } from '../../providers/authProvider';

const { Title, Paragraph } = Typography;

export const ConfigPageFull = () => {
  const [accountForm] = Form.useForm();
  const [tikuForm] = Form.useForm();
  const [notificationForm] = Form.useForm();
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadConfig();
  }, []);

  const loadConfig = async () => {
    try {
      const response = await axiosInstance.get('/user/config');
      const config = response.data;

      // 设置超星账号配置
      accountForm.setFieldsValue({
        cx_username: config.cx_username,
        speed: config.speed || 1.5,
        notopen_action: config.notopen_action || 'retry',
      });

      // 设置题库配置
      if (config.tiku_config) {
        tikuForm.setFieldsValue(config.tiku_config);
      }

      // 设置通知配置
      if (config.notification_config) {
        notificationForm.setFieldsValue(config.notification_config);
      }
    } catch (error: any) {
      if (error.response?.status !== 404) {
        message.error('加载配置失败');
      }
    }
  };

  const saveAccountConfig = async (values: any) => {
    try {
      setLoading(true);
      await axiosInstance.put('/user/config', {
        cx_username: values.cx_username,
        cx_password: values.cx_password,
        speed: values.speed,
        notopen_action: values.notopen_action,
      });
      message.success('超星账号配置保存成功！');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  const saveTikuConfig = async (values: any) => {
    try {
      setLoading(true);
      await axiosInstance.put('/user/config', {
        tiku_config: values
      });
      message.success('题库配置保存成功！');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  const saveNotificationConfig = async (values: any) => {
    try {
      setLoading(true);
      await axiosInstance.put('/user/config', {
        notification_config: values
      });
      message.success('通知配置保存成功！');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: 1200, margin: '0 auto' }}>
      <Title level={2}>配置管理</Title>
      <Paragraph type="secondary">
        配置您的超星账号、题库和通知设置
      </Paragraph>

      <Tabs
        defaultActiveKey="account"
        items={[
          {
            key: 'account',
            label: '超星账号',
            children: (
              <Card>
                <Alert
                  message="账号安全"
                  description="密码会加密存储在数据库中，请放心填写。每个任务都会使用这里配置的账号登录。"
                  type="info"
                  showIcon
                  style={{ marginBottom: 24 }}
                />

                <Form
                  form={accountForm}
                  layout="vertical"
                  onFinish={saveAccountConfig}
                >
                  <Form.Item
                    label="超星手机号"
                    name="cx_username"
                    rules={[
                      { required: true, message: '请输入超星手机号' },
                      { pattern: /^1[3-9]\d{9}$/, message: '请输入有效的11位手机号' }
                    ]}
                  >
                    <Input placeholder="请输入11位手机号" size="large" />
                  </Form.Item>

                  <Form.Item
                    label="超星密码"
                    name="cx_password"
                    rules={[{ required: true, message: '请输入密码' }]}
                  >
                    <Input.Password placeholder="请输入密码" size="large" />
                  </Form.Item>

                  <Divider />

                  <Title level={5}>学习设置</Title>

                          <Form.Item
                            label="视频播放倍速"
                            name="speed"
                            initialValue={1.5}
                            rules={[{ required: true }]}
                            tooltip="视频播放速度，范围1.0-2.0倍"
                          >
                            <InputNumber 
                              min={1} 
                              max={2} 
                              step={0.1} 
                              style={{ width: '100%' }} 
                              formatter={value => `${value ?? 1.5}x`}
                              size="large"
                            />
                          </Form.Item>

                  <Form.Item
                    label="未开放章节处理方式"
                    name="notopen_action"
                    initialValue="retry"
                    tooltip="遇到未开放的章节时如何处理"
                  >
                    <Select size="large">
                      <Select.Option value="retry">重试上一章节</Select.Option>
                      <Select.Option value="continue">跳过继续</Select.Option>
                      <Select.Option value="ask">询问用户</Select.Option>
                    </Select>
                  </Form.Item>

                  <Form.Item>
                    <Button 
                      type="primary" 
                      htmlType="submit" 
                      loading={loading} 
                      size="large"
                      icon={<SaveOutlined />}
                      block
                    >
                      保存配置
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            ),
          },
          {
            key: 'tiku',
            label: '题库配置',
            children: (
              <Card>
                <Alert
                  message="题库说明"
                  description="配置题库后，系统会自动使用题库答题。对于有章节检测且任务点需要解锁的课程，必须配置题库。"
                  type="info"
                  showIcon
                  style={{ marginBottom: 24 }}
                />

                <Form
                  form={tikuForm}
                  layout="vertical"
                  onFinish={saveTikuConfig}
                >
                  <Form.Item
                    label="题库提供商"
                    name="provider"
                    tooltip="选择要使用的题库服务"
                  >
                    <Select size="large" placeholder="请选择题库" allowClear>
                      <Select.Option value="TikuYanxi">言溪题库</Select.Option>
                      <Select.Option value="TikuLike">LIKE知识库</Select.Option>
                      <Select.Option value="TikuAdapter">TikuAdapter</Select.Option>
                      <Select.Option value="AI">AI大模型（OpenAI兼容）</Select.Option>
                      <Select.Option value="SiliconFlow">硅基流动AI ⚡</Select.Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    noStyle
                    shouldUpdate={(prevValues, currentValues) => 
                      prevValues.provider !== currentValues.provider
                    }
                  >
                    {({ getFieldValue }) => {
                      const provider = getFieldValue('provider');
                      
                      // 通用配置
                      const commonFields = (
                        <>
                          <Form.Item
                            label="查询延迟（秒）"
                            name="delay"
                            initialValue={1}
                            tooltip="每次查询题库的延迟时间"
                          >
                            <InputNumber 
                              min={0} 
                              max={10} 
                              step={0.5} 
                              style={{ width: '100%' }} 
                              size="large"
                            />
                          </Form.Item>

                          <Form.Item
                            label="题目覆盖率"
                            name="cover_rate"
                            initialValue={0.9}
                            tooltip="搜到的题目占总题目的比例，达到此比例才提交"
                          >
                            <InputNumber 
                              min={0} 
                              max={1} 
                              step={0.1} 
                              style={{ width: '100%' }} 
                              formatter={value => `${((value ?? 0.9) * 100)}%`}
                              size="large"
                            />
                          </Form.Item>

                          <Form.Item
                            label="自动提交"
                            name="submit"
                            initialValue={false}
                            valuePropName="checked"
                            tooltip="达到覆盖率后是否自动提交答案"
                          >
                            <Switch 
                              checkedChildren="自动提交" 
                              unCheckedChildren="仅保存" 
                            />
                          </Form.Item>
                        </>
                      );

                      // 言溪题库
                      if (provider === 'TikuYanxi') {
                        return (
                          <>
                            <Form.Item
                              label="题库Token"
                              name="tokens"
                              rules={[{ required: true, message: '请输入题库Token' }]}
                              tooltip="从言溪题库获取的Token，多个用逗号分隔"
                              extra={<a href="https://tk.enncy.cn/" target="_blank" rel="noreferrer">获取Token →</a>}
                            >
                              <Input.Password placeholder="多个Token用逗号分隔" size="large" />
                            </Form.Item>
                            {commonFields}
                          </>
                        );
                      }

                      // LIKE知识库
                      if (provider === 'TikuLike') {
                        return (
                          <>
                            <Form.Item
                              label="LIKE Token"
                              name="tokens"
                              rules={[{ required: true, message: '请输入LIKE Token' }]}
                              extra={<a href="https://www.datam.site/" target="_blank" rel="noreferrer">获取Token →</a>}
                            >
                              <Input.Password placeholder="请输入LIKE Token" size="large" />
                            </Form.Item>
                            <Form.Item label="联网搜索" name="likeapi_search" valuePropName="checked" initialValue={false}>
                              <Switch />
                            </Form.Item>
                            <Form.Item label="模型选择" name="likeapi_model" initialValue="deepseek-v3">
                              <Select>
                                <Select.Option value="deepseek-v3">DeepSeek V3</Select.Option>
                                <Select.Option value="gpt-4o">GPT-4o</Select.Option>
                              </Select>
                            </Form.Item>
                            {commonFields}
                          </>
                        );
                      }

                      // TikuAdapter
                      if (provider === 'TikuAdapter') {
                        return (
                          <>
                            <Form.Item
                              label="TikuAdapter URL"
                              name="url"
                              rules={[
                                { required: true, message: '请输入TikuAdapter URL' },
                                { type: 'url', message: '请输入有效的URL' }
                              ]}
                              extra={<a href="https://github.com/DokiDoki1103/tikuAdapter" target="_blank" rel="noreferrer">项目地址 →</a>}
                            >
                              <Input placeholder="http://localhost:8000" size="large" />
                            </Form.Item>
                            {commonFields}
                          </>
                        );
                      }

                      // AI大模型
                      if (provider === 'AI') {
                        return (
                          <>
                            <Alert
                              message="OpenAI兼容API"
                              description="支持所有兼容OpenAI格式的API（如DeepSeek、Moonshot等）"
                              type="info"
                              style={{ marginBottom: 16 }}
                            />
                            <Form.Item
                              label="API端点"
                              name="endpoint"
                              rules={[{ required: true, message: '请输入API端点' }]}
                              tooltip="API地址，可能需要带/v1路径"
                            >
                              <Input placeholder="https://api.example.com/v1" size="large" />
                            </Form.Item>
                            <Form.Item
                              label="API Key"
                              name="key"
                              rules={[{ required: true, message: '请输入API Key' }]}
                            >
                              <Input.Password placeholder="sk-..." size="large" />
                            </Form.Item>
                            <Form.Item
                              label="模型名称"
                              name="model"
                              rules={[{ required: true, message: '请输入模型名称' }]}
                            >
                              <Input placeholder="gpt-4o-mini" size="large" />
                            </Form.Item>
                            <Form.Item label="请求间隔（秒）" name="min_interval_seconds" initialValue={3}>
                              <InputNumber min={0} max={60} style={{ width: '100%' }} />
                            </Form.Item>
                            <Form.Item label="HTTP代理（可选）" name="http_proxy">
                              <Input placeholder="http://proxy.example.com" size="large" />
                            </Form.Item>
                            {commonFields}
                          </>
                        );
                      }

                      // 硅基流动
                      if (provider === 'SiliconFlow') {
                        return (
                          <>
                            <Alert
                              message="硅基流动AI - 推荐！"
                              description="性价比极高的AI答题服务，支持DeepSeek-R1等先进模型"
                              type="success"
                              style={{ marginBottom: 16 }}
                            />
                            <Form.Item
                              label="API Key"
                              name="siliconflow_key"
                              rules={[{ required: true, message: '请输入硅基流动API Key' }]}
                              extra={<a href="https://cloud.siliconflow.cn/account/ak" target="_blank" rel="noreferrer">获取API Key →</a>}
                            >
                              <Input.Password placeholder="sk-..." size="large" />
                            </Form.Item>
                            <Form.Item 
                              label="模型选择" 
                              name="siliconflow_model" 
                              initialValue="deepseek-ai/DeepSeek-R1"
                              extra={<a href="https://docs.siliconflow.cn/cn/api-reference/chat-completions/chat-completions" target="_blank" rel="noreferrer">查看支持的模型 →</a>}
                            >
                              <Select>
                                <Select.Option value="deepseek-ai/DeepSeek-R1">DeepSeek-R1（推荐）</Select.Option>
                                <Select.Option value="deepseek-ai/DeepSeek-V3">DeepSeek-V3</Select.Option>
                                <Select.Option value="Qwen/Qwen2.5-72B-Instruct">Qwen2.5-72B</Select.Option>
                              </Select>
                            </Form.Item>
                            <Form.Item 
                              label="API端点" 
                              name="siliconflow_endpoint" 
                              initialValue="https://api.siliconflow.cn/v1/chat/completions"
                            >
                              <Input size="large" />
                            </Form.Item>
                            <Form.Item label="请求间隔（秒）" name="min_interval_seconds" initialValue={3}>
                              <InputNumber min={0} max={60} style={{ width: '100%' }} />
                            </Form.Item>
                            {commonFields}
                          </>
                        );
                      }

                      return null;
                    }}
                  </Form.Item>

                  <Form.Item>
                    <Button 
                      type="primary" 
                      htmlType="submit" 
                      loading={loading} 
                      size="large"
                      icon={<SaveOutlined />}
                      block
                    >
                      保存配置
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            ),
          },
          {
            key: 'notification',
            label: '通知配置',
            children: (
              <Card>
                <Alert
                  message="通知说明"
                  description="配置后，系统会在任务完成或出现错误时通过外部服务推送通知。"
                  type="info"
                  showIcon
                  style={{ marginBottom: 24 }}
                />

                <Form
                  form={notificationForm}
                  layout="vertical"
                  onFinish={saveNotificationConfig}
                >
                  <Form.Item
                    label="通知服务"
                    name="provider"
                    tooltip="选择通知推送服务"
                  >
                    <Select size="large" placeholder="请选择通知服务" allowClear>
                      <Select.Option value="ServerChan">Server酱</Select.Option>
                      <Select.Option value="Qmsg">Qmsg酱</Select.Option>
                      <Select.Option value="Bark">Bark（iOS）</Select.Option>
                      <Select.Option value="SMTP">📧 SMTP邮件</Select.Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    noStyle
                    shouldUpdate={(prevValues, currentValues) => 
                      prevValues.provider !== currentValues.provider
                    }
                  >
                    {({ getFieldValue }) => {
                      const provider = getFieldValue('provider');

                      // Server酱、Qmsg、Bark（需要URL）
                      if (provider === 'ServerChan' || provider === 'Qmsg' || provider === 'Bark') {
                        return (
                          <>
                            <Form.Item
                              label="Webhook URL"
                              name="url"
                              rules={[
                                { required: true, message: '请输入Webhook URL' },
                                { type: 'url', message: '请输入有效的URL' }
                              ]}
                              tooltip="从通知服务获取的Webhook地址"
                              extra={
                                provider === 'ServerChan' ? <a href="https://sct.ftqq.com/" target="_blank" rel="noreferrer">获取URL →</a> :
                                provider === 'Qmsg' ? <a href="https://qmsg.zendee.cn/" target="_blank" rel="noreferrer">获取URL →</a> :
                                provider === 'Bark' ? <a href="https://bark.day.app/" target="_blank" rel="noreferrer">获取URL →</a> : null
                              }
                            >
                              <Input placeholder="https://..." size="large" />
                            </Form.Item>
                          </>
                        );
                      }

                      // SMTP邮件
                      if (provider === 'SMTP') {
                        return (
                          <>
                            <Alert
                              message="SMTP邮件通知"
                              description="配置您的邮箱SMTP服务，任务完成或出错时会发送邮件通知"
                              type="info"
                              style={{ marginBottom: 16 }}
                            />
                            <Form.Item
                              label="SMTP服务器"
                              name="smtp_host"
                              rules={[{ required: true, message: '请输入SMTP服务器地址' }]}
                              tooltip="例如：smtp.gmail.com、smtp.qq.com"
                            >
                              <Input placeholder="smtp.gmail.com" size="large" />
                            </Form.Item>

                            <Form.Item
                              label="SMTP端口"
                              name="smtp_port"
                              initialValue={587}
                              rules={[{ required: true, message: '请输入SMTP端口' }]}
                              tooltip="TLS通常使用587端口，SSL使用465端口"
                            >
                              <InputNumber min={1} max={65535} style={{ width: '100%' }} size="large" />
                            </Form.Item>

                            <Form.Item
                              label="发件邮箱/用户名"
                              name="smtp_username"
                              rules={[
                                { required: true, message: '请输入邮箱地址' },
                                { type: 'email', message: '请输入有效的邮箱地址' }
                              ]}
                              tooltip="通常是您的完整邮箱地址"
                            >
                              <Input placeholder="your_email@gmail.com" size="large" />
                            </Form.Item>

                            <Form.Item
                              label="SMTP密码/授权码"
                              name="smtp_password"
                              rules={[{ required: true, message: '请输入SMTP密码' }]}
                              tooltip="Gmail需使用应用专用密码，QQ/163需使用授权码"
                            >
                              <Input.Password placeholder="密码或授权码" size="large" />
                            </Form.Item>

                            <Form.Item
                              label="接收通知的邮箱"
                              name="smtp_to_email"
                              rules={[
                                { required: true, message: '请输入接收邮箱' },
                                { type: 'email', message: '请输入有效的邮箱地址' }
                              ]}
                              tooltip="通知将发送到此邮箱"
                            >
                              <Input placeholder="recipient@example.com" size="large" />
                            </Form.Item>

                            <Form.Item
                              label="发件人名称"
                              name="smtp_from_name"
                              initialValue="超星学习通"
                            >
                              <Input size="large" />
                            </Form.Item>

                            <Form.Item
                              label="使用TLS加密"
                              name="smtp_use_tls"
                              initialValue={true}
                              valuePropName="checked"
                              tooltip="大多数SMTP服务器需要TLS（587端口）或SSL（465端口）"
                            >
                              <Switch checkedChildren="TLS(587)" unCheckedChildren="SSL(465)" />
                            </Form.Item>
                          </>
                        );
                      }

                      return null;
                    }}
                  </Form.Item>

                  <Form.Item>
                    <Button 
                      type="primary" 
                      htmlType="submit" 
                      loading={loading} 
                      size="large"
                      icon={<SaveOutlined />}
                      block
                    >
                      保存配置
                    </Button>
                  </Form.Item>
                </Form>
              </Card>
            ),
          },
        ]}
      />
    </div>
  );
};

