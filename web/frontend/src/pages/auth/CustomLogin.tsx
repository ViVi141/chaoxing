import { useLogin } from '@refinedev/core';
import { Form, Input, Button, Checkbox, Card, Typography, Space } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';

const { Title, Text } = Typography;

export const CustomLogin = () => {
  const { mutate: login, isPending } = useLogin();

  const onFinish = (values: any) => {
    login(values);
  };

  return (
    <div
      style={{
        height: '100vh',
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
      }}
    >
      <Card
        style={{
          width: 400,
          boxShadow: '0 20px 60px rgba(0,0,0,0.3)',
          borderRadius: 8,
        }}
      >
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div style={{ textAlign: 'center' }}>
            <Title level={2} style={{ marginBottom: 8 }}>
              超星学习通管理平台
            </Title>
            <Text type="secondary">登录您的账户</Text>
          </div>

          <Form
            name="login"
            onFinish={onFinish}
            layout="vertical"
            requiredMark={false}
            initialValues={{ remember: true }}
          >
            <Form.Item
              name="username"
              label="用户名或邮箱"
              rules={[{ required: true, message: '请输入用户名或邮箱' }]}
            >
              <Input
                size="large"
                prefix={<UserOutlined />}
                placeholder="admin"
              />
            </Form.Item>

            <Form.Item
              name="password"
              label="密码"
              rules={[{ required: true, message: '请输入密码' }]}
            >
              <Input.Password
                size="large"
                prefix={<LockOutlined />}
                placeholder="••••••••"
              />
            </Form.Item>

            <Form.Item name="remember" valuePropName="checked" noStyle>
              <Checkbox>记住我</Checkbox>
            </Form.Item>

            <Form.Item style={{ marginTop: 24, marginBottom: 0 }}>
              <Button
                type="primary"
                size="large"
                htmlType="submit"
                block
                loading={isPending}
              >
                登录
              </Button>
            </Form.Item>
          </Form>

          <div style={{ textAlign: 'center' }}>
            <a href="/forgot-password" style={{ color: '#667eea' }}>
              忘记密码？
            </a>
            <span style={{ margin: '0 8px', color: '#d9d9d9' }}>·</span>
            <a href="/register" style={{ color: '#667eea' }}>
              注册账号
            </a>
          </div>

          <div
            style={{
              textAlign: 'center',
              padding: '16px',
              background: '#f0f7ff',
              borderRadius: 4,
              marginTop: 8,
              border: '1px solid #d6e4ff',
            }}
          >
            <div style={{ marginBottom: 4 }}>
              <Text type="secondary" style={{ fontSize: 12 }}>
                💡 <strong>默认管理员账号</strong>
              </Text>
            </div>
            <Text type="secondary" style={{ fontSize: 12 }}>
              用户名：<strong>admin</strong> · 密码：<strong>Admin@123</strong>
            </Text>
          </div>

          <div style={{ textAlign: 'center', marginTop: 8 }}>
            <Text type="secondary" style={{ fontSize: 11 }}>
              🎁 开源免费项目 · GPL-3.0 · 
              <a 
                href="https://github.com/ViVi141/chaoxing" 
                target="_blank" 
                rel="noopener noreferrer"
                style={{ marginLeft: 4, color: '#667eea' }}
              >
                GitHub
              </a>
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  );
};

