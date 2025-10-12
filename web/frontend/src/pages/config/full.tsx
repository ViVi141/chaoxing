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
                      <Select.Option value="TikuWangke">网课题库</Select.Option>
                      <Select.Option value="TikuIcodef">Icodef题库</Select.Option>
                      <Select.Option value="TikuAPI">自定义API</Select.Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    noStyle
                    shouldUpdate={(prevValues, currentValues) => 
                      prevValues.provider !== currentValues.provider
                    }
                  >
                    {({ getFieldValue }) => {
                      return getFieldValue('provider') ? (
                        <>
                          <Form.Item
                            label="题库Token"
                            name="token"
                            rules={[{ required: true, message: '请输入题库Token' }]}
                            tooltip="从题库网站获取的API Token"
                          >
                            <Input.Password placeholder="请输入题库Token" size="large" />
                          </Form.Item>

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
                            initialValue={0.8}
                            tooltip="搜到的题目占总题目的比例，达到此比例才提交"
                          >
                            <InputNumber 
                              min={0} 
                              max={1} 
                              step={0.1} 
                              style={{ width: '100%' }} 
                              formatter={value => `${((value ?? 0.8) * 100)}%`}
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
                      ) : null;
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
                      <Select.Option value="PushPlus">PushPlus</Select.Option>
                      <Select.Option value="Bark">Bark</Select.Option>
                      <Select.Option value="DingTalk">钉钉</Select.Option>
                      <Select.Option value="WeChat">企业微信</Select.Option>
                    </Select>
                  </Form.Item>

                  <Form.Item
                    noStyle
                    shouldUpdate={(prevValues, currentValues) => 
                      prevValues.provider !== currentValues.provider
                    }
                  >
                    {({ getFieldValue }) => {
                      return getFieldValue('provider') ? (
                        <>
                          <Form.Item
                            label="Webhook URL"
                            name="url"
                            rules={[
                              { required: true, message: '请输入Webhook URL' },
                              { type: 'url', message: '请输入有效的URL' }
                            ]}
                            tooltip="从通知服务获取的Webhook地址"
                          >
                            <Input placeholder="https://..." size="large" />
                          </Form.Item>

                          <Form.Item
                            label="Token/密钥"
                            name="token"
                            tooltip="部分服务需要额外的Token或密钥"
                          >
                            <Input.Password placeholder="请输入Token（可选）" size="large" />
                          </Form.Item>

                          <Form.Item
                            label="启用通知"
                            name="enabled"
                            initialValue={true}
                            valuePropName="checked"
                          >
                            <Switch checkedChildren="启用" unCheckedChildren="禁用" />
                          </Form.Item>
                        </>
                      ) : null;
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

