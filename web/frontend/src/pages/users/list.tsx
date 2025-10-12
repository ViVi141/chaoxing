import { List, useTable, EditButton, ShowButton, DeleteButton } from '@refinedev/antd';
import { Table, Space } from 'antd';

export const UserList = () => {
  const { tableProps } = useTable({
    syncWithLocation: true,
  });

  return (
    <List>
      <Table {...tableProps} rowKey="id">
        <Table.Column dataIndex="id" title="ID" />
        <Table.Column dataIndex="username" title="用户名" />
        <Table.Column dataIndex="email" title="邮箱" />
        <Table.Column dataIndex="role" title="角色" />
        <Table.Column
          dataIndex="is_active"
          title="状态"
          render={(value) => (value ? '激活' : '禁用')}
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

