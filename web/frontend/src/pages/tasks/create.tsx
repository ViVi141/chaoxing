import { Create, useForm } from '@refinedev/antd';
import { Form, Input, InputNumber } from 'antd';

export const TaskCreate = () => {
  const { formProps, saveButtonProps } = useForm();

  return (
    <Create saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical">
        <Form.Item
          label="课程ID"
          name="course_id"
          rules={[{ required: true }]}
          extra="请输入超星学习通的课程ID"
        >
          <Input placeholder="例如: 123456789" />
        </Form.Item>
        <Form.Item
          label="课程名称"
          name="course_name"
          rules={[{ required: true }]}
        >
          <Input placeholder="例如: 大学英语" />
        </Form.Item>
        <Form.Item
          label="播放倍速"
          name="speed"
          initialValue={1.5}
          rules={[{ required: true }]}
        >
          <InputNumber min={1} max={2} step={0.1} style={{ width: '100%' }} />
        </Form.Item>
      </Form>
    </Create>
  );
};

