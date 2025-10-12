import { Show, TextField, EmailField, DateField } from '@refinedev/antd';
import { useShow } from '@refinedev/core';
import { Typography } from 'antd';

const { Title } = Typography;

export const UserShow = () => {
  const { queryResult } = useShow();
  const { data, isLoading } = queryResult;

  const record = data?.data;

  return (
    <Show isLoading={isLoading}>
      <Title level={5}>ID</Title>
      <TextField value={record?.id} />

      <Title level={5}>用户名</Title>
      <TextField value={record?.username} />

      <Title level={5}>邮箱</Title>
      <EmailField value={record?.email} />

      <Title level={5}>角色</Title>
      <TextField value={record?.role} />

      <Title level={5}>创建时间</Title>
      <DateField value={record?.created_at} />
    </Show>
  );
};

