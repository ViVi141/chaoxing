import { Show } from '@refinedev/antd';
import { useShow } from '@refinedev/core';
import { Typography, Card, Progress, Tag, Button, Space, Divider, Timeline, Alert, Popconfirm, message, Modal, Descriptions } from 'antd';
import { PlayCircleOutlined, PauseCircleOutlined, StopOutlined, ReloadOutlined, DeleteOutlined, CopyOutlined, DownloadOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useState, useEffect } from 'react';
import { websocketManager } from '../../providers/websocket';
import { axiosInstance } from '../../providers/authProvider';
import { useNavigate } from 'react-router-dom';

const { Text, Paragraph } = Typography;

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

export const TaskShowFull = () => {
  const { query } = useShow();
  const { data, isLoading, refetch } = query;
  const record = data?.data;
  const navigate = useNavigate();

  // 设置页面标题
  useEffect(() => {
    if (record) {
      document.title = `任务详情 - ${record.course_name || '任务'} - 超星学习通管理平台`;
    } else {
      document.title = '任务详情 - 超星学习通管理平台';
    }
  }, [record]);

  const [realTimeProgress, setRealTimeProgress] = useState(0);
  const [realTimeLogs, setRealTimeLogs] = useState<string[]>([]);
  const [actionLoading, setActionLoading] = useState(false);
  const [currentItem, setCurrentItem] = useState<string>('');
  const [itemProgress, setItemProgress] = useState<number>(0);
  const [itemCurrentTime, setItemCurrentTime] = useState<number>(0);
  const [itemTotalTime, setItemTotalTime] = useState<number>(0);
  const [itemDetail, setItemDetail] = useState<string>('');
  const [infoModalVisible, setInfoModalVisible] = useState(false);

  // 调试：打印record数据
  useEffect(() => {
    if (record) {
      console.log('[TaskShow] Record data:', record);
      console.log('[TaskShow] Logs count:', record.logs?.length || 0);
    }
  }, [record]);

  // ✅ WebSocket实时更新（完整实现）
  useEffect(() => {
    if (!record?.id) return;

    // 连接WebSocket
    const token = localStorage.getItem('token');
    if (token && !websocketManager.isConnected()) {
      websocketManager.connect(token);
    }

    // 订阅当前任务的更新
    websocketManager.send('subscribe_task', { task_id: record.id });

    // 处理任务更新消息
    const handleTaskUpdate = (message: any) => {
      console.log('[Task] Received update:', message);
      
      // 检查是否是当前任务的更新
      if (message.task_id === record.id) {
        const { data } = message;
        
        // 更新进度
        if (data.progress !== undefined) {
          setRealTimeProgress(data.progress);
        }
        
        // 更新当前项目和进度
        if (data.current_item) {
          setCurrentItem(data.current_item);
        }
        if (data.item_progress !== undefined) {
          setItemProgress(data.item_progress);
        }
        
        // 更新时间信息（视频/音频）
        if (data.item_current_time !== undefined) {
          console.log('[视频进度] 当前时间:', data.item_current_time);
          setItemCurrentTime(data.item_current_time);
        }
        if (data.item_total_time !== undefined) {
          console.log('[视频进度] 总时长:', data.item_total_time);
          setItemTotalTime(data.item_total_time);
        }
        
        // 更新详情信息
        if (data.item_detail) {
          setItemDetail(data.item_detail);
        }
        
        // 添加日志
        if (data.error_msg) {
          setRealTimeLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] ❌ ${data.error_msg}`]);
        }
        
        // 状态变化时刷新数据（包括logs）
        if (data.status && data.status !== record.status) {
          setRealTimeLogs(prev => [...prev, `[${new Date().toLocaleTimeString()}] 状态变更: ${data.status}`]);
          refetch(); // 刷新任务数据，包括数据库日志
        }
        
        // 显示课程进度
        if (data.completed_courses !== undefined && data.total_courses !== undefined) {
          setRealTimeLogs(prev => [
            ...prev, 
            `[${new Date().toLocaleTimeString()}] 课程进度: ${data.completed_courses}/${data.total_courses}`
          ]);
        }
        
        // ✅ 有进度更新时也刷新数据，获取最新日志
        if (data.progress !== undefined || data.current_item) {
          refetch();
        }
      }
    };

    // 监听task_update事件
    websocketManager.on('task_update', handleTaskUpdate);

    // 清理函数
    return () => {
      websocketManager.off('task_update', handleTaskUpdate);
      // 取消订阅
      websocketManager.send('unsubscribe_task', { task_id: record.id });
    };
  }, [record?.id, record?.status]);
  
  // ✅ 任务运行时定期刷新日志
  useEffect(() => {
    if (record?.status === 'running') {
      const interval = setInterval(() => {
        refetch(); // 每5秒刷新一次，获取最新日志
      }, 5000);
      
      return () => clearInterval(interval);
    }
  }, [record?.status]);

  const handleAction = async (action: string) => {
    try {
      setActionLoading(true);
      await axiosInstance.post(`/tasks/${record?.id}/${action}`);
      message.success(`操作成功: ${action}`);
      refetch();
    } catch (error: any) {
      message.error(error.response?.data?.detail || `操作失败: ${action}`);
      console.error(`Action ${action} failed:`, error);
    } finally {
      setActionLoading(false);
    }
  };

  // 删除任务
  const handleDelete = async () => {
    try {
      await axiosInstance.delete(`/tasks/${record?.id}`);
      message.success('任务已删除');
      navigate('/tasks');
    } catch (error: any) {
      message.error(error.response?.data?.detail || '删除失败');
    }
  };

  // 复制任务信息
  const handleCopy = async () => {
    const info = `任务ID: ${record?.id}\n任务名称: ${record?.name || '未命名'}\n状态: ${statusText[record?.status]}\n进度: ${record?.progress}%\n创建时间: ${new Date(record?.created_at).toLocaleString('zh-CN')}`;
    
    try {
      if (navigator.clipboard && navigator.clipboard.writeText) {
        await navigator.clipboard.writeText(info);
        message.success('任务信息已复制到剪贴板');
      } else {
        // Fallback: 使用传统的方法
        const textArea = document.createElement('textarea');
        textArea.value = info;
        textArea.style.position = 'fixed';
        textArea.style.opacity = '0';
        document.body.appendChild(textArea);
        textArea.select();
        document.execCommand('copy');
        document.body.removeChild(textArea);
        message.success('任务信息已复制到剪贴板');
      }
    } catch (error) {
      console.error('复制失败:', error);
      message.error('复制失败，请手动复制');
    }
  };

  // 导出日志
  const handleExportLogs = () => {
    const logs = realTimeLogs.join('\n');
    const blob = new Blob([logs], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `task_${record?.id}_logs.txt`;
    a.click();
    URL.revokeObjectURL(url);
    message.success('日志已导出');
  };

  // 键盘快捷键
  useEffect(() => {
    const handleKeyPress = (e: KeyboardEvent) => {
      // 检查是否在输入框中
      if (e.target instanceof HTMLInputElement || e.target instanceof HTMLTextAreaElement) {
        return;
      }

      switch (e.key.toLowerCase()) {
        case 's':
          if (record?.status === 'pending' && !actionLoading) {
            e.preventDefault();
            handleAction('start');
          }
          break;
        case 'p':
          if (record?.status === 'running' && !actionLoading) {
            e.preventDefault();
            handleAction('pause');
          }
          break;
        case 'c':
          if (record?.status === 'running' && !actionLoading) {
            e.preventDefault();
            handleAction('cancel');
          }
          break;
        case 'r':
          if ((record?.status === 'failed' || record?.status === 'cancelled') && !actionLoading) {
            e.preventDefault();
            handleAction('retry');
          }
          break;
        case 'delete':
          if (record?.status === 'completed' || record?.status === 'failed' || record?.status === 'cancelled') {
            e.preventDefault();
            Modal.confirm({
              title: '确认删除',
              content: '确定要删除此任务吗？此操作不可恢复。',
              okText: '确定',
              cancelText: '取消',
              onOk: handleDelete,
            });
          }
          break;
        case 'i':
          e.preventDefault();
          setInfoModalVisible(true);
          break;
        case 'escape':
          e.preventDefault();
          setInfoModalVisible(false);
          break;
      }
    };

    window.addEventListener('keydown', handleKeyPress);
    return () => window.removeEventListener('keydown', handleKeyPress);
  }, [record, actionLoading]);

  const currentProgress = realTimeProgress || record?.progress || 0;

  return (
    <Show
      isLoading={isLoading}
      headerButtons={({ defaultButtons }) => (
        <>
          {defaultButtons}
          <Button
            icon={<ReloadOutlined />}
            onClick={() => refetch()}
          >
            刷新
          </Button>
        </>
      )}
    >
      {/* 任务基本信息 */}
      <Card title="任务信息" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }} size="large">
          <div>
            <Text strong>任务ID: </Text>
            <Text>{record?.id}</Text>
          </div>
          
          <div>
            <Text strong>课程名称: </Text>
            <Text>{record?.course_name || '未设置'}</Text>
          </div>

          <div>
            <Text strong>课程ID: </Text>
            <Text>{record?.course_id || '未设置'}</Text>
          </div>

          <div>
            <Text strong>状态: </Text>
            <Tag color={statusColors[record?.status] || 'default'}>
              {statusText[record?.status] || record?.status}
            </Tag>
          </div>

          <div>
            <Text strong>创建时间: </Text>
            <Text>{record?.created_at ? new Date(record.created_at).toLocaleString('zh-CN') : '-'}</Text>
          </div>

          {record?.started_at && (
            <div>
              <Text strong>开始时间: </Text>
              <Text>{new Date(record.started_at).toLocaleString('zh-CN')}</Text>
            </div>
          )}

          {record?.completed_at && (
            <div>
              <Text strong>完成时间: </Text>
              <Text>{new Date(record.completed_at).toLocaleString('zh-CN')}</Text>
            </div>
          )}
        </Space>
      </Card>

      {/* 总体进度 */}
      <Card title="📊 总体进度" style={{ marginBottom: 16 }}>
        <Space direction="vertical" style={{ width: '100%' }}>
          <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
            <Text strong>任务完成度：</Text>
            <Text style={{ fontSize: '24px', fontWeight: 'bold', color: '#1890ff' }}>
              {currentProgress}%
            </Text>
          </div>
          <Progress 
            percent={currentProgress} 
            status={record?.status === 'running' ? 'active' : record?.status === 'completed' ? 'success' : record?.status === 'failed' ? 'exception' : undefined}
            size={['100%', 20]}
            strokeColor={{
              '0%': '#1890ff',
              '50%': '#52c41a',
              '100%': '#52c41a',
            }}
          />
          {record && record.total_courses > 0 && (
            <Text type="secondary">
              已完成 {record.completed_courses || 0} / {record.total_courses} 门课程
            </Text>
          )}
        </Space>
      </Card>

      {/* 当前项目进度（仅运行时显示） */}
      {currentItem && record?.status === 'running' && (
        <Card 
          title="🎯 当前进度" 
          style={{ marginBottom: 16 }}
          extra={
            itemTotalTime > 0 && (
              <Tag color="blue" style={{ fontSize: '14px', padding: '4px 12px' }}>
                ⏱ {Math.floor(itemCurrentTime / 60)}:{String(itemCurrentTime % 60).padStart(2, '0')}
                {' / '}
                {Math.floor(itemTotalTime / 60)}:{String(itemTotalTime % 60).padStart(2, '0')}
              </Tag>
            )
          }
        >
          <Space direction="vertical" style={{ width: '100%' }}>
            <div>
              <Text strong>当前任务：</Text>
              <Text style={{ marginLeft: 8, fontSize: '16px' }}>{currentItem}</Text>
            </div>
            
            {itemDetail && (
              <Text type="secondary">{itemDetail}</Text>
            )}
            
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginTop: 8 }}>
              <Text strong>播放进度：</Text>
              <Text style={{ fontSize: '20px', fontWeight: 'bold', color: '#52c41a' }}>
                {itemProgress}%
              </Text>
            </div>
            
            <Progress 
              percent={itemProgress} 
              status="active"
              size={['100%', 16]}
              strokeColor={{
                '0%': '#108ee9',
                '100%': '#87d068',
              }}
              format={(percent) => (
                <span style={{ fontSize: '14px', fontWeight: 'bold' }}>
                  {percent}%
                </span>
              )}
            />
            
            {/* 进度条下方的详细信息 */}
            {itemTotalTime > 0 && (
              <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 4 }}>
                <Text type="secondary">已播放 {Math.floor(itemCurrentTime / 60)}分{itemCurrentTime % 60}秒</Text>
                <Text type="secondary">剩余 {Math.floor((itemTotalTime - itemCurrentTime) / 60)}分{(itemTotalTime - itemCurrentTime) % 60}秒</Text>
              </div>
            )}
          </Space>
        </Card>
      )}

      {/* 任务控制 */}
      <Card 
        title="任务控制" 
        style={{ marginBottom: 16 }}
        extra={
          <Space>
            <Button
              size="small"
              icon={<InfoCircleOutlined />}
              onClick={() => setInfoModalVisible(true)}
            >
              快捷键 (I)
            </Button>
            <Button
              size="small"
              icon={<CopyOutlined />}
              onClick={handleCopy}
            >
              复制信息
            </Button>
            {realTimeLogs.length > 0 && (
              <Button
                size="small"
                icon={<DownloadOutlined />}
                onClick={handleExportLogs}
              >
                导出日志
              </Button>
            )}
          </Space>
        }
      >
        <Space wrap>
          {/* 开始任务 */}
          {record?.status === 'pending' && (
            <Button
              type="primary"
              size="large"
              icon={<PlayCircleOutlined />}
              onClick={() => handleAction('start')}
              loading={actionLoading}
            >
              开始任务 (S)
            </Button>
          )}
          
          {/* 运行中的操作 */}
          {record?.status === 'running' && (
            <>
              <Button
                size="large"
                icon={<PauseCircleOutlined />}
                onClick={() => handleAction('pause')}
                loading={actionLoading}
              >
                暂停 (P)
              </Button>
              <Button
                size="large"
                danger
                icon={<StopOutlined />}
                onClick={() => handleAction('cancel')}
                loading={actionLoading}
              >
                取消 (C)
              </Button>
            </>
          )}
          
          {/* 继续任务 */}
          {record?.status === 'paused' && (
            <Button
              type="primary"
              size="large"
              icon={<PlayCircleOutlined />}
              onClick={() => handleAction('resume')}
              loading={actionLoading}
            >
              继续 (S)
            </Button>
          )}

          {/* 重试任务 */}
          {(record?.status === 'failed' || record?.status === 'cancelled') && (
            <Button
              type="primary"
              size="large"
              icon={<ReloadOutlined />}
              onClick={() => handleAction('retry')}
              loading={actionLoading}
            >
              重试任务 (R)
            </Button>
          )}

          {/* 删除任务 */}
          {(record?.status === 'completed' || record?.status === 'failed' || record?.status === 'cancelled') && (
            <Popconfirm
              title="确定要删除此任务吗？"
              description="此操作不可恢复"
              onConfirm={handleDelete}
              okText="确定"
              cancelText="取消"
            >
              <Button
                size="large"
                danger
                icon={<DeleteOutlined />}
              >
                删除任务 (Del)
              </Button>
            </Popconfirm>
          )}

          {/* 刷新 */}
          <Button
            size="large"
            icon={<ReloadOutlined />}
            onClick={() => refetch()}
          >
            刷新
          </Button>
        </Space>
      </Card>

      {/* 快捷键说明弹窗 */}
      <Modal
        title="键盘快捷键"
        open={infoModalVisible}
        onCancel={() => setInfoModalVisible(false)}
        footer={[
          <Button key="close" type="primary" onClick={() => setInfoModalVisible(false)}>
            知道了
          </Button>
        ]}
      >
        <Descriptions column={1} bordered size="small">
          <Descriptions.Item label="S">开始/继续任务</Descriptions.Item>
          <Descriptions.Item label="P">暂停任务</Descriptions.Item>
          <Descriptions.Item label="C">取消任务</Descriptions.Item>
          <Descriptions.Item label="R">重试任务</Descriptions.Item>
          <Descriptions.Item label="Del">删除任务</Descriptions.Item>
          <Descriptions.Item label="I">显示快捷键</Descriptions.Item>
          <Descriptions.Item label="Esc">关闭弹窗</Descriptions.Item>
        </Descriptions>
        <Alert
          style={{ marginTop: 16 }}
          message="提示"
          description="快捷键仅在非输入状态下有效，且会根据任务当前状态自动适配"
          type="info"
          showIcon
        />
      </Modal>

      {/* 实时日志 */}
      <Card title="任务日志">
        {realTimeLogs.length > 0 && (
          <>
            <Alert
              message="实时日志"
              description="以下是WebSocket接收到的实时日志"
              type="info"
              showIcon
              style={{ marginBottom: 16 }}
            />
            <Timeline>
              {realTimeLogs.map((log, index) => (
                <Timeline.Item key={index}>
                  <Text style={{ fontFamily: 'monospace', fontSize: 12 }}>
                    {log}
                  </Text>
                </Timeline.Item>
              ))}
            </Timeline>
            <Divider />
          </>
        )}

        {/* 显示数据库中的详细日志 */}
        {record?.logs && record.logs.length > 0 ? (
          <Timeline
            style={{ 
              maxHeight: 500,
              overflow: 'auto',
              padding: 16,
              background: '#fafafa',
              borderRadius: 4
            }}
          >
            {record.logs.map((log: any) => (
              <Timeline.Item 
                key={log.id}
                color={
                  log.level === 'ERROR' ? 'red' : 
                  log.level === 'WARNING' ? 'orange' : 
                  log.level === 'INFO' ? 'blue' : 
                  'gray'
                }
              >
                <div style={{ fontFamily: 'Consolas, Monaco, monospace', fontSize: 13 }}>
                  <Text type="secondary" style={{ marginRight: 8 }}>
                    {new Date(log.created_at).toLocaleString('zh-CN')}
                  </Text>
                  <Tag color={
                    log.level === 'ERROR' ? 'red' : 
                    log.level === 'WARNING' ? 'orange' : 
                    'blue'
                  }>
                    {log.level}
                  </Tag>
                  <Text>{log.message}</Text>
                </div>
              </Timeline.Item>
            ))}
          </Timeline>
        ) : (
          <div style={{ 
            background: '#f5f5f5', 
            padding: 16, 
            borderRadius: 4,
            textAlign: 'center',
            color: '#999'
          }}>
            暂无日志（任务尚未启动或日志加载中）
          </div>
        )}
      </Card>

      {/* 任务结果 */}
      {record?.result && (
        <Card title="任务结果" style={{ marginTop: 16 }}>
          <Paragraph>
            <pre style={{ 
              background: '#f5f5f5', 
              padding: 16, 
              borderRadius: 4,
              overflow: 'auto'
            }}>
              {JSON.stringify(record.result, null, 2)}
            </pre>
          </Paragraph>
        </Card>
      )}

      {/* 错误信息 */}
      {record?.error && (
        <Card title="错误信息" style={{ marginTop: 16 }}>
          <Alert
            message="任务执行失败"
            description={record.error}
            type="error"
            showIcon
          />
        </Card>
      )}
    </Show>
  );
};

