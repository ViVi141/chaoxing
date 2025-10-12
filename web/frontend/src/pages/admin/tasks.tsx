import { List, useTable, ShowButton } from '@refinedev/antd';
import { Table, Space, Tag, Button, Popconfirm, message, Progress } from 'antd';
import { StopOutlined, ReloadOutlined } from '@ant-design/icons';
import { axiosInstance } from '../../providers/authProvider';

const statusColors: Record<string, string> = {
  pending: 'default',
  running: 'processing',
  completed: 'success',
  failed: 'error',
  cancelled: 'warning',
  paused: 'warning',
};

const statusText: Record<string, string> = {
  pending: '待处理',
  running: '运行中',
  completed: '已完成',
  failed: '失败',
  cancelled: '已取消',
  paused: '已暂停',
};

export const AdminTasksList = () => {
  const { tableProps, tableQueryResult } = useTable({
    resource: 'admin/tasks',
    syncWithLocation: true,
  });

  const handleCancelTask = async (taskId: number) => {
    try {
      await axiosInstance.post(`/admin/tasks/${taskId}/cancel`);
      message.success('任务已取消');
      tableQueryResult?.refetch();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  const handleRetryTask = async (taskId: number) => {
    try {
      await axiosInstance.post(`/tasks/${taskId}/retry`);
      message.success('任务已重新启动');
      tableQueryResult?.refetch();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  return (
    <List 
      title="任务监控（管理员）"
      headerButtons={({ defaultButtons }) => (
        <>
          {defaultButtons}
          <Button
            icon={<ReloadOutlined />}
            onClick={() => tableQueryResult?.refetch()}
          >
            刷新
          </Button>
        </>
      )}
    >
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="id" title="ID" width={80} />
        <Table.Column 
          dataIndex="user_id" 
          title="用户ID"
          width={100}
        />
        <Table.Column dataIndex="course_name" title="课程名称" />
        <Table.Column
          dataIndex="status"
          title="状态"
          render={(status) => (
            <Tag color={statusColors[status]}>
              {statusText[status]}
            </Tag>
          )}
          filters={[
            { text: '待处理', value: 'pending' },
            { text: '运行中', value: 'running' },
            { text: '已完成', value: 'completed' },
            { text: '失败', value: 'failed' },
            { text: '已取消', value: 'cancelled' },
          ]}
        />
        <Table.Column
          dataIndex="progress"
          title="进度"
          width={150}
          render={(progress) => (
            <Progress 
              percent={progress || 0} 
              size="small"
              status={progress === 100 ? 'success' : 'active'}
            />
          )}
        />
        <Table.Column
          dataIndex="created_at"
          title="创建时间"
          render={(date) => new Date(date).toLocaleString('zh-CN')}
        />
        <Table.Column
          title="操作"
          dataIndex="actions"
          fixed="right"
          width={150}
          render={(_, record: any) => (
            <Space size="small">
              <ShowButton hideText size="small" recordItemId={record.id} />
              
              {record.status === 'running' && (
                <Popconfirm
                  title="确定要取消这个任务吗？"
                  onConfirm={() => handleCancelTask(record.id)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Button 
                    size="small" 
                    danger 
                    icon={<StopOutlined />}
                  />
                </Popconfirm>
              )}
              
              {(record.status === 'failed' || record.status === 'cancelled') && (
                <Button
                  size="small"
                  icon={<ReloadOutlined />}
                  onClick={() => handleRetryTask(record.id)}
                >
                  重试
                </Button>
              )}
            </Space>
          )}
        />
      </Table>
    </List>
  );
};

