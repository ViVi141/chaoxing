import { Create, useForm } from '@refinedev/antd';
import { Form, Input, InputNumber, Select, Switch, Card, Button, Alert, Spin, message, Table, Tag } from 'antd';
import { ReloadOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { axiosInstance } from '../../providers/authProvider';

const { TextArea } = Input;

interface Course {
  courseId: string;
  courseName: string;
  teacherName: string;
  clazzId: string;
  cpi: string;
  progress: number;
  state: number;
}

export const TaskCreateFull = () => {
  const { formProps, saveButtonProps } = useForm();
  const [courses, setCourses] = useState<Course[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedCourseIds, setSelectedCourseIds] = useState<string[]>([]);

  // 获取课程列表
  const loadCourses = async () => {
    try {
      setLoading(true);
      const response = await axiosInstance.get('/courses/list');
      setCourses(response.data);
      message.success(`成功获取 ${response.data.length} 门课程`);
    } catch (error: any) {
      if (error.response?.status === 400) {
        message.error(error.response.data.detail || '请先配置超星账号');
      } else {
        message.error('获取课程列表失败');
      }
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadCourses();
  }, []);

  // 课程选择表格列
  const columns = [
    {
      title: '选择',
      dataIndex: 'courseId',
      key: 'select',
      width: 60,
      render: (courseId: string) => (
        <input
          type="checkbox"
          checked={selectedCourseIds.includes(courseId)}
          onChange={(e) => {
            if (e.target.checked) {
              setSelectedCourseIds([...selectedCourseIds, courseId]);
            } else {
              setSelectedCourseIds(selectedCourseIds.filter(id => id !== courseId));
            }
          }}
        />
      ),
    },
    {
      title: '课程名称',
      dataIndex: 'courseName',
      key: 'courseName',
    },
    {
      title: '教师',
      dataIndex: 'teacherName',
      key: 'teacherName',
      width: 150,
    },
    {
      title: '课程ID',
      dataIndex: 'courseId',
      key: 'courseId',
      width: 120,
    },
    {
      title: '进度',
      dataIndex: 'progress',
      key: 'progress',
      width: 100,
      render: (progress: number) => `${progress}%`,
    },
    {
      title: '状态',
      dataIndex: 'state',
      key: 'state',
      width: 100,
      render: (state: number) => (
        state === 0 ? (
          <Tag color="green">进行中</Tag>
        ) : (
          <Tag color="default">已结束</Tag>
        )
      ),
    },
  ];

  // 表单提交处理
  const handleSubmit = (values: any) => {
    // 验证是否选择了课程
    if (selectedCourseIds.length === 0) {
      message.error('请至少选择一门课程');
      return Promise.reject('请至少选择一门课程');
    }
    
    // 准备提交数据
    const submitData: any = {
      name: values.task_name || (selectedCourseIds.length > 0 
        ? courses.find(c => c.courseId === selectedCourseIds[0])?.courseName 
        : '学习任务') || '学习任务',
      course_ids: selectedCourseIds
    };
    
    // 添加描述（如果有）
    if (values.description) {
      submitData.description = values.description;
    }
    
    console.log('提交任务数据:', submitData);
    
    return formProps.onFinish?.(submitData);
  };

  return (
    <Create saveButtonProps={saveButtonProps}>
      <Form {...formProps} layout="vertical" onFinish={handleSubmit}>
        {/* 课程选择 */}
        <Card 
          title="📚 选择课程" 
          style={{ marginBottom: 16 }}
          extra={
            <Button 
              icon={<ReloadOutlined />} 
              onClick={loadCourses}
              loading={loading}
            >
              刷新课程列表
            </Button>
          }
        >
          <Alert
            message="智能课程选择"
            description={
              <>
                <p>✅ 自动从您的超星账号获取所有课程</p>
                <p>✅ 支持选择多门课程批量学习</p>
                <p>✅ 显示课程进度和状态</p>
                {selectedCourseIds.length > 0 && (
                  <p style={{ marginTop: 8, fontWeight: 'bold', color: '#52c41a' }}>
                    已选择 {selectedCourseIds.length} 门课程
                  </p>
                )}
              </>
            }
            type="info"
            icon={<InfoCircleOutlined />}
            style={{ marginBottom: 16 }}
          />

          {loading ? (
            <Spin spinning={loading} tip="正在获取课程列表...">
              <div style={{ minHeight: '200px' }} />
            </Spin>
          ) : courses.length === 0 ? (
            <Alert
              message="未获取到课程"
              description='请确保已在「配置管理」中正确配置超星账号和密码'
              type="warning"
              showIcon
            />
          ) : (
            <Table
              columns={columns}
              dataSource={courses}
              rowKey="courseId"
              pagination={{ pageSize: 10 }}
              size="small"
            />
          )}
        </Card>

        {/* 基础配置 */}
        <Card title="⚙️ 基础配置" style={{ marginBottom: 16 }}>
          <Form.Item
            label="任务名称"
            name="task_name"
            tooltip="自动使用第一个选中的课程名称，也可以自定义"
          >
            <Input placeholder="留空则自动使用课程名称" />
          </Form.Item>

          <Form.Item
            label="任务描述"
            name="description"
          >
            <TextArea 
              rows={3} 
              placeholder="可选：添加任务描述" 
            />
          </Form.Item>
        </Card>

        {/* 学习配置 */}
        <Card title="🎬 学习配置" style={{ marginBottom: 16 }}>
          <Form.Item
            label="播放倍速"
            name="speed"
            initialValue={1.5}
            rules={[{ required: true }]}
            tooltip="视频播放速度，范围1.0-2.0"
          >
            <InputNumber 
              min={1} 
              max={2} 
              step={0.1} 
              style={{ width: '100%' }} 
              formatter={value => `${value}x`}
            />
          </Form.Item>

          <Form.Item
            label="未开放章节处理"
            name="notopen_action"
            initialValue="retry"
            tooltip="遇到未开放章节时的处理方式"
          >
            <Select>
              <Select.Option value="retry">重试上一章节</Select.Option>
              <Select.Option value="continue">跳过继续</Select.Option>
              <Select.Option value="ask">询问用户</Select.Option>
            </Select>
          </Form.Item>

          <Form.Item
            label="自动提交"
            name="auto_submit"
            initialValue={true}
            valuePropName="checked"
            tooltip="是否自动提交作业和测验"
          >
            <Switch checkedChildren="是" unCheckedChildren="否" />
          </Form.Item>
        </Card>

        {/* 高级配置 */}
        <Card title="🔧 高级配置（可选）">
          <Form.Item
            label="指定章节ID列表"
            name="chapter_ids"
            tooltip="用逗号分隔，留空则学习所有章节"
          >
            <Input placeholder="例如: 12345,67890" />
          </Form.Item>

          <Form.Item
            label="题库配置"
            name="tiku_provider"
            tooltip="选择要使用的题库"
          >
            <Select placeholder="请选择题库" allowClear>
              <Select.Option value="cx">超星题库</Select.Option>
              <Select.Option value="wk">文库题库</Select.Option>
              <Select.Option value="tk">题库网</Select.Option>
            </Select>
          </Form.Item>
        </Card>
      </Form>
    </Create>
  );
};
