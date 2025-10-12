import { Card, Row, Col, Statistic, Table, Tag, Typography, List, Progress } from 'antd';
import { 
  UserOutlined, 
  FileTextOutlined, 
  ClockCircleOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  WarningOutlined
} from '@ant-design/icons';
import { useEffect, useState } from 'react';
import { axiosInstance } from '../../providers/authProvider';

const { Title, Text } = Typography;

// 状态颜色映射
const statusColors: Record<string, string> = {
  pending: 'default',
  running: 'processing',
  completed: 'success',
  failed: 'error',
  cancelled: 'warning',
};

// 状态文本映射
const statusText: Record<string, string> = {
  pending: '等待中',
  running: '运行中',
  completed: '已完成',
  failed: '失败',
  cancelled: '已取消',
};

export const AdminDashboard = () => {
  const [stats, setStats] = useState<any>({});
  const [recentUsers, setRecentUsers] = useState<any[]>([]);
  const [activeTasks, setActiveTasks] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      
      const [statsRes, usersRes, tasksRes] = await Promise.all([
        axiosInstance.get('/admin/statistics'),
        axiosInstance.get('/admin/users', { params: { page: 1, page_size: 5 } }),
        axiosInstance.get('/admin/tasks', { params: { page: 1, page_size: 10, status: 'running' } }),
      ]);

      setStats(statsRes.data);
      setRecentUsers(usersRes.data.items || []);
      setActiveTasks(tasksRes.data.items || []);
    } catch (error) {
      console.error('加载数据失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '24px' }}>
      <Title level={2}>管理员控制台</Title>

      {/* 统计概览 */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
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
              title="运行中任务"
              value={stats.runningTasks || 0}
              prefix={<ClockCircleOutlined />}
              valueStyle={{ color: '#faad14' }}
            />
          </Card>
        </Col>
        
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日完成"
              value={stats.todayCompleted || 0}
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="今日失败"
              value={stats.todayFailed || 0}
              prefix={<CloseCircleOutlined />}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="活跃用户"
              value={stats.activeUsers || 0}
              prefix={<UserOutlined />}
              valueStyle={{ color: '#722ed1' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="系统警告"
              value={stats.warnings || 0}
              prefix={<WarningOutlined />}
              valueStyle={{ color: '#fa8c16' }}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="成功率"
              value={stats.successRate || 0}
              suffix="%"
              prefix={<CheckCircleOutlined />}
              valueStyle={{ color: '#52c41a' }}
            />
          </Card>
        </Col>
      </Row>

      {/* 最近注册用户 */}
      <Card title="最近注册用户" style={{ marginTop: 24 }} loading={loading}>
        <Table
          dataSource={recentUsers}
          rowKey="id"
          pagination={false}
          columns={[
            {
              title: 'ID',
              dataIndex: 'id',
              width: 80,
            },
            {
              title: '用户名',
              dataIndex: 'username',
            },
            {
              title: '角色',
              dataIndex: 'role',
              render: (role) => (
                <Tag color={role === 'admin' ? 'gold' : 'blue'}>
                  {role === 'admin' ? '管理员' : '普通用户'}
                </Tag>
              ),
            },
            {
              title: '状态',
              dataIndex: 'is_active',
              render: (active) => (
                <Tag color={active ? 'success' : 'default'}>
                  {active ? '激活' : '禁用'}
                </Tag>
              ),
            },
            {
              title: '注册时间',
              dataIndex: 'created_at',
              render: (date) => new Date(date).toLocaleString('zh-CN'),
            },
          ]}
        />
      </Card>

      {/* 活跃任务 */}
      <Card title="运行中的任务" style={{ marginTop: 24 }} loading={loading}>
        <Table
          dataSource={activeTasks}
          rowKey="id"
          pagination={false}
          columns={[
            {
              title: 'ID',
              dataIndex: 'id',
              width: 80,
            },
            {
              title: '用户',
              dataIndex: 'user_id',
              render: (userId) => `用户#${userId}`,
            },
            {
              title: '课程名称',
              dataIndex: 'course_name',
            },
            {
              title: '状态',
              dataIndex: 'status',
              render: (status) => (
                <Tag color={statusColors[status]}>
                  {statusText[status]}
                </Tag>
              ),
            },
            {
              title: '进度',
              dataIndex: 'progress',
              render: (progress) => (
                <div style={{ width: 120 }}>
                  <Progress 
                    percent={progress || 0} 
                    size="small"
                    status="active"
                  />
                </div>
              ),
            },
            {
              title: '创建时间',
              dataIndex: 'created_at',
              render: (date) => new Date(date).toLocaleString('zh-CN'),
            },
          ]}
        />
      </Card>

      {/* 系统信息 */}
      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} lg={12}>
          <Card title="系统信息">
            <Row gutter={[16, 16]}>
              <Col span={12}>
                <Text type="secondary">系统版本</Text>
                <div><Text strong>v2.0.0 (Refine)</Text></div>
              </Col>
              <Col span={12}>
                <Text type="secondary">部署模式</Text>
                <div><Text strong>简单模式</Text></div>
              </Col>
              <Col span={12}>
                <Text type="secondary">数据库</Text>
                <div><Text strong>SQLite</Text></div>
              </Col>
              <Col span={12}>
                <Text type="secondary">任务队列</Text>
                <div><Text strong>Celery</Text></div>
              </Col>
            </Row>
          </Card>
        </Col>

        <Col xs={24} lg={12}>
          <Card title="快捷操作">
            <List>
              <List.Item>
                <a href="/admin/users">管理用户</a>
              </List.Item>
              <List.Item>
                <a href="/admin/tasks">监控任务</a>
              </List.Item>
              <List.Item>
                <a href="/admin/logs">查看日志</a>
              </List.Item>
              <List.Item>
                <a href="/config">系统配置</a>
              </List.Item>
            </List>
          </Card>
        </Col>
      </Row>
    </div>
  );
};

