import { List, useTable } from '@refinedev/antd';
import { Table, Space, Tag, Button, Popconfirm, message, Progress, Tooltip } from 'antd';
import { 
  PlayCircleOutlined, 
  StopOutlined, 
  ReloadOutlined, 
  DeleteOutlined,
  EyeOutlined,
  PauseCircleOutlined
} from '@ant-design/icons';
import { useState } from 'react';
import { axiosInstance } from '../../providers/authProvider';
import { useNavigate } from 'react-router-dom';

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

export const TaskList = () => {
  const { tableProps, tableQueryResult } = useTable({
    syncWithLocation: true,
  });
  
  const [actionLoading, setActionLoading] = useState<Record<number, boolean>>({});
  const [selectedRowKeys, setSelectedRowKeys] = useState<React.Key[]>([]);
  const navigate = useNavigate();

  const { refetch } = tableQueryResult;

  // 快捷操作函数
  const handleQuickAction = async (taskId: number, action: string, actionName: string) => {
    setActionLoading(prev => ({ ...prev, [taskId]: true }));
    try {
      await axiosInstance.post(`/tasks/${taskId}/${action}`);
      message.success(`${actionName}成功`);
      refetch();
    } catch (error: any) {
      message.error(error.response?.data?.detail || `${actionName}失败`);
    } finally {
      setActionLoading(prev => ({ ...prev, [taskId]: false }));
    }
  };

  // 删除任务
  const handleDelete = async (taskId: number) => {
    try {
      await axiosInstance.delete(`/tasks/${taskId}`);
      message.success('删除成功');
      refetch();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  // 批量操作
  const handleBatchAction = async (action: string, actionName: string) => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择任务');
      return;
    }

    try {
      await Promise.all(
        selectedRowKeys.map(id => axiosInstance.post(`/tasks/${id}/${action}`))
      );
      message.success(`批量${actionName}成功`);
      setSelectedRowKeys([]);
      refetch();
    } catch (error: any) {
      message.error(`批量${actionName}失败`);
    }
  };

  // 批量删除
  const handleBatchDelete = async () => {
    if (selectedRowKeys.length === 0) {
      message.warning('请先选择任务');
      return;
    }

    try {
      await Promise.all(
        selectedRowKeys.map(id => axiosInstance.delete(`/tasks/${id}`))
      );
      message.success('批量删除成功');
      setSelectedRowKeys([]);
      refetch();
    } catch (error: any) {
      message.error('批量删除失败');
    }
  };

  const rowSelection = {
    selectedRowKeys,
    onChange: (newSelectedRowKeys: React.Key[]) => {
      setSelectedRowKeys(newSelectedRowKeys);
    },
  };

  return (
    <List
      headerButtons={({ defaultButtons }) => (
        <>
          {defaultButtons}
          {selectedRowKeys.length > 0 && (
            <Space>
              <Button
                type="primary"
                icon={<PlayCircleOutlined />}
                onClick={() => handleBatchAction('start', '启动')}
              >
                批量启动 ({selectedRowKeys.length})
              </Button>
              <Button
                icon={<StopOutlined />}
                onClick={() => handleBatchAction('cancel', '取消')}
              >
                批量取消
              </Button>
              <Popconfirm
                title="确定要删除选中的任务吗？"
                description="此操作不可恢复"
                onConfirm={handleBatchDelete}
                okText="确定"
                cancelText="取消"
              >
                <Button danger icon={<DeleteOutlined />}>
                  批量删除
                </Button>
              </Popconfirm>
            </Space>
          )}
        </>
      )}
    >
      <Table 
        {...tableProps} 
        rowKey="id"
        rowSelection={rowSelection}
        scroll={{ x: 1200 }}
      >
        <Table.Column 
          dataIndex="id" 
          title="ID" 
          width={80}
          sorter={(a: any, b: any) => a.id - b.id}
        />
        
        <Table.Column 
          dataIndex="name" 
          title="任务名称" 
          width={200}
          ellipsis={{ showTitle: false }}
          render={(value: string) => (
            <Tooltip placement="topLeft" title={value}>
              {value || '未命名任务'}
            </Tooltip>
          )}
        />
        
        <Table.Column
          dataIndex="status"
          title="状态"
          width={120}
          filters={[
            { text: '待处理', value: 'pending' },
            { text: '运行中', value: 'running' },
            { text: '已完成', value: 'completed' },
            { text: '失败', value: 'failed' },
            { text: '已取消', value: 'cancelled' },
          ]}
          onFilter={(value: any, record: any) => record.status === value}
          render={(value: string) => (
            <Tag color={statusColors[value] || 'default'}>
              {statusText[value] || value}
            </Tag>
          )}
        />
        
        <Table.Column
          dataIndex="progress"
          title="进度"
          width={150}
          sorter={(a: any, b: any) => (a.progress || 0) - (b.progress || 0)}
          render={(value: number) => (
            <Progress 
              percent={value || 0} 
              size="small"
              status={value === 100 ? 'success' : 'active'}
            />
          )}
        />
        
        <Table.Column
          dataIndex="created_at"
          title="创建时间"
          width={180}
          sorter={(a: any, b: any) => new Date(a.created_at).getTime() - new Date(b.created_at).getTime()}
          render={(value: string) => new Date(value).toLocaleString('zh-CN')}
        />
        
        <Table.Column
          title="快速操作"
          width={200}
          fixed="right"
          render={(_, record: any) => (
            <Space size="small">
              {/* 查看 */}
              <Tooltip title="查看详情">
                <Button
                  type="link"
                  size="small"
                  icon={<EyeOutlined />}
                  onClick={() => navigate(`/tasks/show/${record.id}`)}
                />
              </Tooltip>

              {/* 启动 */}
              {record.status === 'pending' && (
                <Tooltip title="启动任务">
                  <Button
                    type="link"
                    size="small"
                    icon={<PlayCircleOutlined />}
                    loading={actionLoading[record.id]}
                    onClick={() => handleQuickAction(record.id, 'start', '启动')}
                    style={{ color: '#52c41a' }}
                  />
                </Tooltip>
              )}

              {/* 暂停 */}
              {record.status === 'running' && (
                <Tooltip title="暂停任务">
                  <Button
                    type="link"
                    size="small"
                    icon={<PauseCircleOutlined />}
                    loading={actionLoading[record.id]}
                    onClick={() => handleQuickAction(record.id, 'pause', '暂停')}
                    style={{ color: '#faad14' }}
                  />
                </Tooltip>
              )}

              {/* 取消 */}
              {record.status === 'running' && (
                <Tooltip title="取消任务">
                  <Button
                    type="link"
                    size="small"
                    icon={<StopOutlined />}
                    loading={actionLoading[record.id]}
                    onClick={() => handleQuickAction(record.id, 'cancel', '取消')}
                    danger
                  />
                </Tooltip>
              )}

              {/* 重试 */}
              {(record.status === 'failed' || record.status === 'cancelled') && (
                <Tooltip title="重试任务">
                  <Button
                    type="link"
                    size="small"
                    icon={<ReloadOutlined />}
                    loading={actionLoading[record.id]}
                    onClick={() => handleQuickAction(record.id, 'retry', '重试')}
                    style={{ color: '#1890ff' }}
                  />
                </Tooltip>
              )}

              {/* 删除 */}
              {(record.status === 'completed' || record.status === 'failed' || record.status === 'cancelled') && (
                <Popconfirm
                  title="确定要删除此任务吗？"
                  description="此操作不可恢复"
                  onConfirm={() => handleDelete(record.id)}
                  okText="确定"
                  cancelText="取消"
                >
                  <Tooltip title="删除任务 (Del)">
                    <Button
                      type="link"
                      size="small"
                      icon={<DeleteOutlined />}
                      danger
                    />
                  </Tooltip>
                </Popconfirm>
              )}
            </Space>
          )}
        />
      </Table>
    </List>
  );
};
