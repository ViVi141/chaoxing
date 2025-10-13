import { Show } from '@refinedev/antd';
import { Descriptions, Card, Tag, Typography, Space, Button } from 'antd';
import { useShow, useNavigation } from '@refinedev/core';
import { EditOutlined, ArrowLeftOutlined } from '@ant-design/icons';

const { Text } = Typography;

export const AdminUserShow = () => {
  const { query } = useShow({ resource: 'admin/users' });
  const { data, isLoading } = query;
  const { list, edit } = useNavigation();

  const record = data?.data;

  return (
    <Show
      isLoading={isLoading}
      title="用户详情"
      headerButtons={({ defaultButtons }) => (
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />}
            onClick={() => list('admin/users')}
          >
            返回列表
          </Button>
          <Button
            type="primary"
            icon={<EditOutlined />}
            onClick={() => record?.id && edit('admin/users', record.id)}
          >
            编辑用户
          </Button>
          {defaultButtons}
        </Space>
      )}
    >
      <Card title="基本信息" style={{ marginBottom: 16 }}>
        <Descriptions bordered column={2}>
          <Descriptions.Item label="用户ID">
            {record?.id}
          </Descriptions.Item>
          <Descriptions.Item label="用户名">
            <Text strong>{record?.username}</Text>
          </Descriptions.Item>
          <Descriptions.Item label="邮箱" span={2}>
            {record?.email || <Text type="secondary">未设置</Text>}
          </Descriptions.Item>
          <Descriptions.Item label="角色">
            <Tag color={record?.role === 'admin' ? 'gold' : 'blue'}>
              {record?.role === 'admin' ? '管理员' : '普通用户'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="账号状态">
            <Tag color={record?.is_active ? 'success' : 'default'}>
              {record?.is_active ? '✅ 激活' : '⭕ 禁用'}
            </Tag>
          </Descriptions.Item>
          <Descriptions.Item label="邮箱验证">
            <Tag color={record?.email_verified ? 'success' : 'warning'}>
              {record?.email_verified ? '✅ 已验证' : '⚠️ 未验证'}
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

      {record?.config && (
        <Card title="学习配置" style={{ marginBottom: 16 }}>
          <Descriptions bordered column={2}>
            <Descriptions.Item label="超星账号" span={2}>
              {record.config.cx_username || <Text type="secondary">未配置</Text>}
            </Descriptions.Item>
            <Descriptions.Item label="超星密码">
              {record.config.cx_password_encrypted ? (
                <Text type="success">✅ 已加密存储</Text>
              ) : (
                <Text type="secondary">未配置</Text>
              )}
            </Descriptions.Item>
            <Descriptions.Item label="使用Cookies">
              <Tag color={record.config.use_cookies ? 'processing' : 'default'}>
                {record.config.use_cookies ? '是' : '否'}
              </Tag>
            </Descriptions.Item>
            <Descriptions.Item label="视频速度">
              {record.config.video_speed || 1.0}x
            </Descriptions.Item>
            <Descriptions.Item label="未开放章节处理">
              <Tag>{record.config.notopen_action || 'continue'}</Tag>
            </Descriptions.Item>
          </Descriptions>
        </Card>
      )}

      {record?.config?.tiku_config && (
        <Card title="题库配置">
          <Descriptions bordered column={2}>
            <Descriptions.Item label="题库提供商">
              <Tag color="blue">{record.config.tiku_config.provider || '未配置'}</Tag>
            </Descriptions.Item>
            <Descriptions.Item label="自动提交">
              <Tag color={record.config.tiku_config.submit ? 'success' : 'default'}>
                {record.config.tiku_config.submit ? '✅ 开启' : '⭕ 关闭'}
              </Tag>
            </Descriptions.Item>
            {record.config.tiku_config.tokens && (
              <Descriptions.Item label="Tokens" span={2}>
                <Text code>{record.config.tiku_config.tokens.substring(0, 20)}...</Text>
              </Descriptions.Item>
            )}
          </Descriptions>
        </Card>
      )}
    </Show>
  );
};

