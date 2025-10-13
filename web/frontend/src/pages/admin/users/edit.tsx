import { Edit } from '@refinedev/antd';
import { Form, Input, Switch, Select, Card, Space, Button } from 'antd';
import { useForm } from '@refinedev/antd';
import { useNavigation } from '@refinedev/core';
import { ArrowLeftOutlined } from '@ant-design/icons';

export const AdminUserEdit = () => {
  const { formProps, saveButtonProps } = useForm({ 
    resource: 'admin/users',
    redirect: 'show'
  });
  const { list } = useNavigation();

  return (
    <Edit
      saveButtonProps={saveButtonProps}
      title="编辑用户"
      headerButtons={({ defaultButtons }) => (
        <Space>
          <Button 
            icon={<ArrowLeftOutlined />}
            onClick={() => list('admin/users')}
          >
            返回列表
          </Button>
          {defaultButtons}
        </Space>
      )}
    >
      <Form {...formProps} layout="vertical">
        <Card title="基本信息" style={{ marginBottom: 16 }}>
          <Form.Item
            label="用户名"
            name="username"
            rules={[
              { required: true, message: '请输入用户名' },
              { min: 3, max: 80, message: '用户名长度为3-80个字符' }
            ]}
          >
            <Input placeholder="用户名" disabled />
          </Form.Item>

          <Form.Item
            label="邮箱"
            name="email"
            rules={[
              { type: 'email', message: '请输入有效的邮箱地址' }
            ]}
          >
            <Input placeholder="user@example.com" />
          </Form.Item>

          <Form.Item
            label="新密码"
            name="password"
            extra="留空则不修改密码"
            rules={[
              { min: 6, max: 128, message: '密码长度为6-128个字符' }
            ]}
          >
            <Input.Password placeholder="留空则不修改" />
          </Form.Item>
        </Card>

        <Card title="账号状态">
          <Form.Item
            label="账号状态"
            name="is_active"
            valuePropName="checked"
            extra="禁用后用户将无法登录"
          >
            <Switch checkedChildren="激活" unCheckedChildren="禁用" />
          </Form.Item>

          <Form.Item
            label="角色"
            name="role"
            extra="警告：修改角色权限需谨慎"
          >
            <Select>
              <Select.Option value="user">普通用户</Select.Option>
              <Select.Option value="admin">管理员</Select.Option>
            </Select>
          </Form.Item>
        </Card>
      </Form>
    </Edit>
  );
};

