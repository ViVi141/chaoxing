import { useEffect, useState } from 'react';
import { useNavigate, useSearchParams } from 'react-router-dom';
import { Card, Result, Button, Spin } from 'antd';
import { LoadingOutlined, CheckCircleOutlined, CloseCircleOutlined } from '@ant-design/icons';
import { axiosInstance } from '../../providers/authProvider';

export const VerifyEmail = () => {
  const [searchParams] = useSearchParams();
  const navigate = useNavigate();
  const [status, setStatus] = useState<'loading' | 'success' | 'error'>('loading');
  const [message, setMessage] = useState('正在验证邮箱...');

  useEffect(() => {
    const token = searchParams.get('token');
    
    if (!token) {
      setStatus('error');
      setMessage('缺少验证令牌');
      return;
    }

    // 调用验证API
    const verifyEmail = async () => {
      try {
        const response = await axiosInstance.post('/auth/verify-email', { token });
        setStatus('success');
        setMessage(response.data.message || '邮箱验证成功！');
      } catch (error: any) {
        setStatus('error');
        setMessage(error.response?.data?.detail || '验证失败，令牌可能已过期');
      }
    };

    verifyEmail();
  }, [searchParams]);

  return (
    <div style={{
      display: 'flex',
      justifyContent: 'center',
      alignItems: 'center',
      minHeight: '100vh',
      background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
    }}>
      <Card style={{ maxWidth: 500, width: '100%', margin: 20 }}>
        {status === 'loading' && (
          <Result
            icon={<Spin indicator={<LoadingOutlined style={{ fontSize: 48 }} spin />} />}
            title="正在验证邮箱"
            subTitle={message}
          />
        )}
        
        {status === 'success' && (
          <Result
            status="success"
            icon={<CheckCircleOutlined style={{ color: '#52c41a' }} />}
            title="邮箱验证成功"
            subTitle={message}
            extra={[
              <Button type="primary" key="login" onClick={() => navigate('/login')}>
                前往登录
              </Button>,
              <Button key="home" onClick={() => navigate('/')}>
                返回首页
              </Button>
            ]}
          />
        )}
        
        {status === 'error' && (
          <Result
            status="error"
            icon={<CloseCircleOutlined style={{ color: '#ff4d4f' }} />}
            title="验证失败"
            subTitle={message}
            extra={[
              <Button type="primary" key="login" onClick={() => navigate('/login')}>
                前往登录
              </Button>,
              <Button key="resend" onClick={() => navigate('/resend-verification')}>
                重新发送验证邮件
              </Button>
            ]}
          />
        )}
      </Card>
    </div>
  );
};

