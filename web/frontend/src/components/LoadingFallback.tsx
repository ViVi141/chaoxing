import { Spin } from 'antd';

export const LoadingFallback = () => {
  return (
    <div
      style={{
        display: 'flex',
        justifyContent: 'center',
        alignItems: 'center',
        minHeight: '100vh',
      }}
    >
      <Spin size="large" spinning={true} tip="加载中...">
        <div style={{ minHeight: '200px' }} />
      </Spin>
    </div>
  );
};

