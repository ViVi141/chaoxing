import { useState, useEffect } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, Form, Input, Button, Alert, Typography, Result } from 'antd';
import { LockOutlined, CheckCircleOutlined } from '@ant-design/icons';
import { axiosInstance } from '../../providers/authProvider';

const { Title, Paragraph } = Typography;

export const ResetPassword = () => {
  const navigate = useNavigate();
  const [searchParams] = useSearchParams();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');

  // 设置页面标题
  useEffect(() => {
    document.title = '重置密码 - 超星学习通管理平台';
  }, []);

  const token = searchParams.get('token');

  if (!token) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <Card style={{ maxWidth: 500, width: '100%', margin: 20 }}>
          <Result
            status="error"
            title="链接无效"
            subTitle="缺少重置令牌，请重新申请密码重置"
            extra={[
              <Button type="primary" key="forgot" onClick={() => navigate('/forgot-password')}>
                重新申请
              </Button>,
              <Button key="login" onClick={() => navigate('/login')}>
                返回登录
              </Button>
            ]}
          />
        </Card>
      </div>
    );
  }

  const onFinish = async (values: any) => {
    if (values.password !== values.confirm_password) {
      setError('两次输入的密码不一致');
      return;
    }

    try {
      setLoading(true);
      setError('');
      
      await axiosInstance.post('/auth/reset-password', {
        token,
        new_password: values.password
      });
      
      setSuccess(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || '重置失败，请重新申请');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <Card style={{ maxWidth: 500, width: '100%', margin: 20 }}>
          <Result
            status="success"
            icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            title="密码重置成功"
            subTitle="您的密码已成功重置，请使用新密码登录"
            extra={[
              <Button type="primary" key="login" onClick={() => navigate('/login')}>
                前往登录
              </Button>
            ]}
          />
        </Card>
      </div>
    );
  }

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card style={{ maxWidth: 500, width: '100%', margin: 20 }}>
        <div style={{ textAlign: 'center', marginBottom: 30 }}>
          <LockOutlined style={{ fontSize: 48, color: '#f5576c', marginBottom: 10 }} />
          <Title level={2}>重置密码</Title>
          <Paragraph type="secondary">
            请输入您的新密码
          </Paragraph>
        </div>

        {error && (
          <Alert
            message="重置失败"
            description={error}
            type="error"
            showIcon
            closable
            onClose={() => setError('')}
            style={{ marginBottom: 20 }}
          />
        )}

        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          size="large"
        >
          <Form.Item
            name="password"
            label="新密码"
            rules={[
              { required: true, message: '请输入新密码' },
              { min: 6, message: '密码至少6个字符' }
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="请输入新密码（至少6个字符）"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item
            name="confirm_password"
            label="确认密码"
            dependencies={['password']}
            rules={[
              { required: true, message: '请确认密码' },
              ({ getFieldValue }) => ({
                validator(_, value) {
                  if (!value || getFieldValue('password') === value) {
                    return Promise.resolve();
                  }
                  return Promise.reject(new Error('两次输入的密码不一致'));
                },
              }),
            ]}
          >
            <Input.Password
              prefix={<LockOutlined />}
              placeholder="请再次输入新密码"
              autoComplete="new-password"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
            >
              重置密码
            </Button>
          </Form.Item>

          <div style={{ textAlign: 'center' }}>
            <Button type="link" onClick={() => navigate('/login')}>
              返回登录
            </Button>
          </div>
        </Form>
      </Card>
    </div>
  );
};

