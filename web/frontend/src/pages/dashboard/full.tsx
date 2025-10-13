import { useGetIdentity } from '@refinedev/core';
import { Card, Row, Col, Statistic, Typography, List, Avatar, Tag, Progress, Empty, Spin, Space, Alert } from 'antd';
import { 
  UserOutlined, 
  FileTextOutlined, 
  CheckCircleOutlined,
  CloseCircleOutlined,
  SyncOutlined,
  GiftOutlined
} from '@ant-design/icons';
import { useEffect, useState } from 'react';
import { axiosInstance } from '../../providers/authProvider';

const { Title, Text } = Typography;

interface Identity {
  username: string;
  role: string;
}

interface DashboardStats {
  totalUsers?: number;
  totalTasks?: number;
  runningTasks?: number;
  completedTasks?: number;
  failedTasks?: number;
}

interface RecentTask {
  id: number;
  course_name: string;
  status: string;
  progress: number;
  created_at: string;
}

const statusColors: Record<string, string> = {
  pending: 'default',
  running: 'processing',
  completed: 'success',
  failed: 'error',
  cancelled: 'warning',
};

const statusText: Record<string, string> = {
  pending: '待处理',
  running: '运行中',
  completed: '已完成',
  failed: '失败',
  cancelled: '已取消',
};

export const DashboardPageFull = () => {
  const { data: identity } = useGetIdentity<Identity>();
  const [stats, setStats] = useState<DashboardStats>({});
  const [recentTasks, setRecentTasks] = useState<RecentTask[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDashboardData();
  }, []);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      
      // 加载统计数据
      const statsResponse = await axiosInstance.get('/admin/statistics');
      setStats(statsResponse.data);

      // 加载最近任务
      const tasksResponse = await axiosInstance.get('/tasks', {
        params: { page: 1, page_size: 5 }
      });
      setRecentTasks(tasksResponse.data.items || []);
    } catch (error) {
      console.error('加载仪表盘数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div style={{ padding: '24px', textAlign: 'center' }}>
        <Spin size="large" />
      </div>
    );
  }

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>
        欢迎回来，{identity?.username}！
        {identity?.role === 'admin' && (
          <Tag color="gold" style={{ marginLeft: 12 }}>管理员</Tag>
        )}
      </Title>

      <Text type="secondary">
        这是您的控制面板，可以查看系统概况和最近任务
      </Text>

      {/* 统计卡片 */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        {identity?.role === 'admin' && (
          <Col xs={24} sm={12} lg={6}>
            <Card>
              <Statistic
                title="总用户数"
                value={stats.totalUsers || 0}
                prefix={<UserOutlined />}
                valueStyle={{ color: '#3f8600' }}
              />
            </Card>
          </Col>
        )}
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="总任务数"
              value={stats.totalTasks || 0}
              prefix={<FileTextOutlined />}
              valueStyle={{ color: '#1890ff' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="运行中"
              value={stats.runningTasks || 0}
              prefix={<SyncOutlined spin />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="已完成"
              value={stats.completedTasks || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="失败"
              value={stats.failedTasks || 0}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 最近任务 */}
      <Card 
        title="最近任务" 
        style={{ marginTop: 24 }}
        extra={
          <a href="/tasks" onClick={(e) => { e.preventDefault(); window.location.href = '/tasks'; }}>
            查看全部
          </a>
        }
      >
        {recentTasks.length > 0 ? (
          <List
            itemLayout="horizontal"
            dataSource={recentTasks}
            renderItem={(task) => (
              <List.Item>
                <List.Item.Meta
                  avatar={<Avatar icon={<FileTextOutlined />} />}
                  title={
                    <a href={`/tasks/show/${task.id}`}>
                      {task.course_name}
                    </a>
                  }
                  description={
                    <Space direction="vertical" style={{ width: '100%' }}>
                      <div>
                        <Tag color={statusColors[task.status]}>
                          {statusText[task.status]}
                        </Tag>
                        <Text type="secondary" style={{ marginLeft: 8 }}>
                          {new Date(task.created_at).toLocaleString('zh-CN')}
                        </Text>
                      </div>
                      <Progress 
                        percent={task.progress} 
                        size="small"
                        status={task.status === 'running' ? 'active' : undefined}
                      />
                    </Space>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty description="暂无任务" />
        )}
      </Card>

      {/* 快速开始指南 */}
      <Card title="快速开始" style={{ marginTop: 24 }}>
        <List>
          <List.Item>
            <Text>1. 前往 <a href="/config">配置管理</a> 设置您的超星学习通账号</Text>
          </List.Item>
          <List.Item>
            <Text>2. 在 <a href="/tasks/create">任务管理</a> 中创建新的学习任务</Text>
          </List.Item>
          <List.Item>
            <Text>3. 查看任务进度和日志，系统会自动完成学习任务点</Text>
          </List.Item>
          {identity?.role === 'admin' && (
            <List.Item>
              <Text>4. 作为管理员，您可以在 <a href="/admin">管理后台</a> 查看所有用户和任务</Text>
            </List.Item>
          )}
        </List>
      </Card>

      {/* 友情提示 - 彩蛋 */}
      {identity?.role !== 'admin' && (
        <Alert
          message={
            <Space>
              <GiftOutlined style={{ color: '#52c41a' }} />
              <span>友情提示</span>
            </Space>
          }
          description={
            <div style={{ fontSize: 13, lineHeight: 1.6 }}>
              <p style={{ marginBottom: 8 }}>
                💡 <strong>本项目是开源免费软件</strong>（GPL-3.0协议），任何人都可以自由使用。
              </p>
              <p style={{ marginBottom: 8 }}>
                ⚠️ 如果有人向您收取使用费用或强制要求付款，<strong>这不符合本项目的开源精神</strong>。
              </p>
              <p style={{ marginBottom: 0 }}>
                ✨ 您有权利免费使用本服务。如有疑问，请访问项目开源地址：
                <a 
                  href="https://github.com/ViVi141/chaoxing" 
                  target="_blank" 
                  rel="noopener noreferrer"
                  style={{ marginLeft: 4 }}
                >
                  GitHub仓库
                </a>
              </p>
            </div>
          }
          type="info"
          showIcon
          closable
          style={{ 
            marginTop: 24,
            background: 'linear-gradient(135deg, #f0f9ff 0%, #e0f2fe 100%)',
            border: '1px solid #bae6fd'
          }}
        />
      )}
    </div>
  );
};

