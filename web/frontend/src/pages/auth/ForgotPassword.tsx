import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Card, Form, Input, Button, Alert, Typography } from 'antd';
import { MailOutlined, ArrowLeftOutlined } from '@ant-design/icons';
import { axiosInstance } from '../../providers/authProvider';

const { Title, Paragraph } = Typography;

export const ForgotPassword = () => {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [loading, setLoading] = useState(false);
  const [submitted, setSubmitted] = useState(false);
  const [error, setError] = useState('');

  const onFinish = async (values: any) => {
    try {
      setLoading(true);
      setError('');
      
      await axiosInstance.post('/auth/forgot-password', {
        email: values.email
      });
      
      setSubmitted(true);
    } catch (err: any) {
      setError(err.response?.data?.detail || '发送失败，请稍后重试');
    } finally {
      setLoading(false);
    }
  };

  if (submitted) {
    return (
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
      }}>
        <Card style={{ maxWidth: 500, width: '100%', margin: 20 }}>
          <div style={{ textAlign: 'center' }}>
            <MailOutlined style={{ fontSize: 64, color: '#52c41a', marginBottom: 20 }} />
            <Title level={3}>邮件已发送</Title>
            <Paragraph type="secondary">
              如果该邮箱已注册，您将收到密码重置邮件。
            </Paragraph>
            <Paragraph type="secondary">
              请检查您的邮箱（包括垃圾邮件文件夹），并按照邮件中的说明重置密码。
            </Paragraph>
            <Paragraph type="secondary" style={{ marginTop: 20 }}>
              重置链接将在30分钟后过期
            </Paragraph>
            <Button type="primary" onClick={() => navigate('/login')} style={{ marginTop: 20 }}>
              返回登录
            </Button>
          </div>
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
        <Button
          type="link"
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/login')}
          style={{ marginBottom: 20, padding: 0 }}
        >
          返回登录
        </Button>
        
        <div style={{ textAlign: 'center', marginBottom: 30 }}>
          <MailOutlined style={{ fontSize: 48, color: '#667eea', marginBottom: 10 }} />
          <Title level={2}>忘记密码</Title>
          <Paragraph type="secondary">
            输入您的注册邮箱，我们将发送密码重置链接
          </Paragraph>
        </div>

        {error && (
          <Alert
            message="发送失败"
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
            name="email"
            rules={[
              { required: true, message: '请输入邮箱' },
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input
              prefix={<MailOutlined />}
              placeholder="请输入注册邮箱"
              autoComplete="email"
            />
          </Form.Item>

          <Form.Item>
            <Button
              type="primary"
              htmlType="submit"
              loading={loading}
              block
            >
              发送重置链接
            </Button>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
};

