import { useGetIdentity } from '@refinedev/core';
import { Card, Row, Col, Statistic, Typography } from 'antd';
import { UserOutlined, FileTextOutlined, ClockCircleOutlined } from '@ant-design/icons';

const { Title } = Typography;

interface Identity {
  username: string;
  role: string;
}

export const DashboardPage = () => {
  const { data: identity } = useGetIdentity<Identity>();

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>欢迎回来，{identity?.username}！</Title>
      
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="总用户数"
              value={0}
              prefix={<UserOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="总任务数"
              value={0}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>
        <Col xs={24} sm={12} lg={8}>
          <Card>
            <Statistic
              title="运行中任务"
              value={0}
              prefix={<ClockCircleOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Card style={{ marginTop: 24 }}>
        <Title level={4}>快速开始</Title>
        <p>1. 在"配置管理"中设置您的超星账号</p>
        <p>2. 在"任务管理"中创建学习任务</p>
        <p>3. 查看任务进度和日志</p>
      </Card>
    </div>
  );
};

