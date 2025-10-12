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
      <Spin size="large" tip="加载中..." />
    </div>
  );
};

