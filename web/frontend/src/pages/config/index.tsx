import { Card, Form, Input, InputNumber, Button, message } from 'antd';
import { useState } from 'react';
import { axiosInstance } from '../../providers/authProvider';

export const ConfigPage = () => {
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);

  const onFinish = async (values: any) => {
    try {
      setLoading(true);
      await axiosInstance.post('/user/config', values);
      message.success('配置保存成功！');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '保存失败');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px', maxWidth: 800 }}>
      <Card title="超星账号配置">
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
        >
          <Form.Item
            label="超星手机号"
            name="cx_username"
            rules={[{ required: true, message: '请输入超星手机号' }]}
          >
            <Input placeholder="请输入11位手机号" />
          </Form.Item>

          <Form.Item
            label="超星密码"
            name="cx_password"
            rules={[{ required: true, message: '请输入密码' }]}
          >
            <Input.Password placeholder="请输入密码" />
          </Form.Item>

          <Form.Item
            label="播放倍速"
            name="speed"
            initialValue={1.5}
            rules={[{ required: true }]}
          >
            <InputNumber min={1} max={2} step={0.1} style={{ width: '100%' }} />
          </Form.Item>

          <Form.Item>
            <Button type="primary" htmlType="submit" loading={loading} size="large">
              保存配置
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

