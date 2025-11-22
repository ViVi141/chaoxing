import { List, useTable, EditButton, DeleteButton, ShowButton } from '@refinedev/antd';
import { Table, Space, Tag, Switch, message } from 'antd';
import { useEffect } from 'react';
import { axiosInstance } from '../../providers/authProvider';

export const AdminUsersList = () => {
  const tableResult = useTable({
    resource: 'admin/users',
    syncWithLocation: true,
  });

  // 设置页面标题
  useEffect(() => {
    document.title = '用户管理 - 超星学习通管理平台';
  }, []);

  const handleToggleActive = async (userId: number, currentStatus: boolean) => {
    try {
      await axiosInstance.put(`/admin/users/${userId}`, {
        is_active: !currentStatus
      });
      message.success('用户状态已更新');
      window.location.reload();
    } catch (error: any) {
      message.error(error.response?.data?.detail || '操作失败');
    }
  };

  return (
    <List title="用户管理（管理员）">
      <Table {...tableResult.tableProps} rowKey="id">
        <Table.Column dataIndex="id" title="ID" width={80} />
        <Table.Column dataIndex="username" title="用户名" />
        <Table.Column 
          dataIndex="email" 
          title="邮箱"
          render={(email) => email || '-'}
        />
        <Table.Column
          dataIndex="role"
          title="角色"
          render={(role) => (
            <Tag color={role === 'admin' ? 'gold' : 'blue'}>
              {role === 'admin' ? '管理员' : '普通用户'}
            </Tag>
          )}
        />
        <Table.Column
          dataIndex="is_active"
          title="状态"
          render={(isActive, record: any) => (
            <Switch
              checked={isActive}
              onChange={() => handleToggleActive(record.id, isActive)}
              checkedChildren="激活"
              unCheckedChildren="禁用"
            />
          )}
        />
        <Table.Column
          dataIndex="created_at"
          title="注册时间"
          render={(date) => new Date(date).toLocaleString('zh-CN')}
        />
        <Table.Column
          dataIndex="last_login"
          title="最后登录"
          render={(date) => date ? new Date(date).toLocaleString('zh-CN') : '从未登录'}
        />
        <Table.Column
          title="操作"
          dataIndex="actions"
          render={(_, record: any) => (
            <Space>
              <ShowButton hideText size="small" recordItemId={record.id} />
              <EditButton hideText size="small" recordItemId={record.id} />
              <DeleteButton hideText size="small" recordItemId={record.id} />
            </Space>
          )}
        />
      </Table>
    </List>
  );
};

