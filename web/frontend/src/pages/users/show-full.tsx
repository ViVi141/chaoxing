import { Show } from '@refinedev/antd';
import { useShow } from '@refinedev/core';
import { Card, Descriptions, Tag, List, Empty, Statistic, Row, Col } from 'antd';
import { useEffect, useState } from 'react';
import { axiosInstance } from '../../providers/authProvider';

export const UserShowFull = () => {
  const { queryResult } = useShow();
  const { data, isLoading } = queryResult;
  const record = data?.data;

  const [userTasks, setUserTasks] = useState<any[]>([]);
  const [userStats, setUserStats] = useState<any>({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (record?.id) {
      loadUserDetails(Number(record.id));
    }
  }, [record?.id]);

  const loadUserDetails = async (userId: number) => {
    try {
      setLoading(true);
      const [tasksRes, statsRes] = await Promise.all([
        axiosInstance.get(`/users/${userId}/tasks`, { params: { page: 1, page_size: 10 } }),
        axiosInstance.get(`/users/${userId}/statistics`),
      ]);
      
      setUserTasks(tasksRes.data.items || []);
      setUserStats(statsRes.data || {});
    } catch (error) {
      console.error('加载用户详情失败:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <Show isLoading={isLoading}>
      {/* 基本信息 */}
      <Card title="基本信息" style={{ marginBottom: 16 }}>
        <Descriptions column={2}>
          <Descriptions.Item label="用户ID">{record?.id}</Descriptions.Item>
          <Descriptions.Item label="用户名">{record?.username}</Descriptions.Item>
          <Descriptions.Item label="邮箱">
            {record?.email || '未设置'}
          </Descriptions.Item>
          <Descriptions.Item label="角色">
            <Tag color={record?.role === 'admin' ? 'gold' : 'blue'}>
              {record?.role === 'admin' ? '管理员' : '普通用户'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="账号状态">
            <Tag color={record?.is_active ? 'success' : 'default'}>
              {record?.is_active ? '激活' : '禁用'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="注册时间">
            {record?.created_at ? new Date(record.created_at).toLocaleString('zh-CN') : '-'}
          </Descriptions.Item>
          <Descriptions.Item label="最后登录">
            {record?.last_login ? new Date(record.last_login).toLocaleString('zh-CN') : '从未登录'}
          </Descriptions.Item>
        </Descriptions>
      </Card>

      {/* 用户统计 */}
      <Card title="用户统计" style={{ marginBottom: 16 }} loading={loading}>
        <Row gutter={16}>
          <Col span={8}>
            <Statistic title="总任务数" value={userStats.totalTasks || 0} />
          </Col>
          <Col span={8}>
            <Statistic 
              title="已完成" 
              value={userStats.completedTasks || 0}
              valueStyle={{ color: '#52c41a' }}
            />
          </Col>
          <Col span={8}>
            <Statistic 
              title="失败任务" 
              value={userStats.failedTasks || 0}
              valueStyle={{ color: '#ff4d4f' }}
            />
          </Col>
        </Row>
      </Card>

      {/* 最近任务 */}
      <Card title="最近任务" loading={loading}>
        {userTasks.length > 0 ? (
          <List
            dataSource={userTasks}
            renderItem={(task: any) => (
              <List.Item>
                <List.Item.Meta
                  title={<a href={`/tasks/show/${task.id}`}>{task.course_name}</a>}
                  description={
                    <span>
                      <Tag color={task.status === 'completed' ? 'success' : 'processing'}>
                        {task.status}
                      </Tag>
                      <span style={{ marginLeft: 8 }}>
                        进度: {task.progress}%
                      </span>
                      <span style={{ marginLeft: 16, color: '#999' }}>
                        {new Date(task.created_at).toLocaleString('zh-CN')}
                      </span>
                    </span>
                  }
                />
              </List.Item>
            )}
          />
        ) : (
          <Empty description="暂无任务记录" />
        )}
      </Card>

      {/* 配置信息 */}
      {record?.config && (
        <Card title="配置信息" style={{ marginTop: 16 }}>
          <Descriptions column={2}>
            <Descriptions.Item label="超星账号">
              {record.config.cx_username || '未配置'}
            </Descriptions.Item>
            <Descriptions.Item label="播放倍速">
              {record.config.speed || 1.5}x
            </Descriptions.Item>
            <Descriptions.Item label="题库配置">
              {record.config.tiku_config?.provider || '未配置'}
            </Descriptions.Item>
            <Descriptions.Item label="通知配置">
              {record.config.notification_config?.provider || '未配置'}
            </Descriptions.Item>
          </Descriptions>
        </Card>
      )}
    </Show>
  );
};

