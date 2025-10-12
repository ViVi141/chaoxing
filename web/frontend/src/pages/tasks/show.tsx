import { Show, TextField, TagField } from '@refinedev/antd';
import { useShow } from '@refinedev/core';
import { Typography, Progress } from 'antd';

const { Title } = Typography;

export const TaskShow = () => {
  const { query } = useShow();
  const { data, isLoading } = query;

  const record = data?.data;

  return (
    <Show isLoading={isLoading}>
      <Title level={5}>任务ID</Title>
      <TextField value={record?.id} />

      <Title level={5}>课程名称</Title>
      <TextField value={record?.course_name} />

      <Title level={5}>状态</Title>
      <TagField value={record?.status} />

      <Title level={5}>进度</Title>
      <Progress percent={record?.progress || 0} />

      <Title level={5}>创建时间</Title>
      <TextField value={new Date(record?.created_at).toLocaleString('zh-CN')} />

      <Title level={5}>任务日志</Title>
      <div style={{ 
        background: '#f5f5f5', 
        padding: 16, 
        borderRadius: 4,
        maxHeight: 400,
        overflow: 'auto',
        fontFamily: 'monospace'
      }}>
        {record?.log || '暂无日志'}
      </div>
    </Show>
  );
};

