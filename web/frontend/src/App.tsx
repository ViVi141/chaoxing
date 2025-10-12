import { Refine } from '@refinedev/core';
import {
  AuthPage,
  ErrorComponent,
  ThemedLayout,
  ThemedTitle,
  useNotificationProvider,
} from '@refinedev/antd';
import routerProviderDefault, {
  DocumentTitleHandler,
  UnsavedChangesNotifier,
} from '@refinedev/react-router';
import { App as AntdApp, ConfigProvider, message } from 'antd';
import { BrowserRouter, Outlet, Route, Routes } from 'react-router-dom';
import zhCN from 'antd/locale/zh_CN';
import { useEffect } from 'react';

import '@refinedev/antd/dist/reset.css';

import { authProvider } from './providers/authProvider';
import { dataProvider } from './providers/dataProvider';
// 用户页面（完整版）
import { DashboardPageFull } from './pages/dashboard/full';
import { TaskList } from './pages/tasks';
import { TaskShowFull } from './pages/tasks/show-full';
import { TaskCreateFull } from './pages/tasks/create-full';
import { ConfigPageFull } from './pages/config/full';
import { CustomLogin, VerifyEmail, ForgotPassword, ResetPassword } from './pages/auth';

// 管理员页面
import { AdminDashboard, AdminUsersList, AdminTasksList, SystemConfig, DatabaseMigration } from './pages/admin';

function App() {
  // 配置全局 message，防止重复弹窗
  useEffect(() => {
    message.config({
      maxCount: 3, // 最多同时显示3个消息
      duration: 2, // 默认显示2秒
    });
  }, []);

  return (
    <BrowserRouter>
      <ConfigProvider locale={zhCN}>
        <AntdApp>
          <Refine
            dataProvider={dataProvider}
            authProvider={authProvider}
            routerProvider={routerProviderDefault}
            notificationProvider={useNotificationProvider}
            options={{
              syncWithLocation: true,
              warnWhenUnsavedChanges: true,
              disableTelemetry: true,
            }}
            resources={[
              {
                name: 'dashboard',
                list: '/',
                meta: {
                  label: '仪表盘',
                  icon: <span>📊</span>,
                },
              },
              {
                name: 'tasks',
                list: '/tasks',
                show: '/tasks/show/:id',
                create: '/tasks/create',
                meta: {
                  label: '任务管理',
                  icon: <span>📝</span>,
                },
              },
              {
                name: 'config',
                list: '/config',
                meta: {
                  label: '配置管理',
                  icon: <span>⚙️</span>,
                },
              },
              {
                name: 'admin',
                meta: {
                  label: '管理员',
                  icon: <span>👑</span>,
                },
              },
              {
                name: 'admin/dashboard',
                list: '/admin/dashboard',
                meta: {
                  label: '控制台',
                  parent: 'admin',
                },
              },
              {
                name: 'admin/users',
                list: '/admin/users',
                meta: {
                  label: '用户管理',
                  parent: 'admin',
                },
              },
              {
                name: 'admin/tasks',
                list: '/admin/tasks',
                meta: {
                  label: '任务监控',
                  parent: 'admin',
                },
              },
              {
                name: 'admin/system-config',
                list: '/admin/system-config',
                meta: {
                  label: '系统配置',
                  parent: 'admin',
                },
              },
              {
                name: 'admin/database-migration',
                list: '/admin/database-migration',
                meta: {
                  label: '数据库迁移',
                  parent: 'admin',
                },
              },
            ]}
          >
            <Routes>
              <Route
                element={
                  <ThemedLayout
                    Title={({ collapsed }) => (
                      <ThemedTitle
                        collapsed={collapsed}
                        text="超星学习通"
                      />
                    )}
                  >
                    <Outlet />
                  </ThemedLayout>
                }
              >
                <Route index element={<DashboardPageFull />} />
                
                <Route path="/tasks">
                  <Route index element={<TaskList />} />
                  <Route path="show/:id" element={<TaskShowFull />} />
                  <Route path="create" element={<TaskCreateFull />} />
                </Route>

                <Route path="/config" element={<ConfigPageFull />} />

                {/* 管理员路由 */}
                <Route path="/admin">
                  <Route path="dashboard" element={<AdminDashboard />} />
                  <Route path="users" element={<AdminUsersList />} />
                  <Route path="tasks" element={<AdminTasksList />} />
                  <Route path="system-config" element={<SystemConfig />} />
                  <Route path="database-migration" element={<DatabaseMigration />} />
                </Route>

                <Route path="*" element={<ErrorComponent />} />
              </Route>

              <Route
                element={<CustomLogin />}
                path="/login"
              />
              
              <Route
                element={
                  <AuthPage
                    type="register"
                    title="超星学习通管理平台"
                    formProps={{
                      initialValues: {
                        username: '',
                        email: '',
                        password: '',
                      },
                    }}
                  />
                }
                path="/register"
              />
              
              <Route path="/verify-email" element={<VerifyEmail />} />
              <Route path="/forgot-password" element={<ForgotPassword />} />
              <Route path="/reset-password" element={<ResetPassword />} />
            </Routes>

            <UnsavedChangesNotifier />
            <DocumentTitleHandler />
          </Refine>
        </AntdApp>
      </ConfigProvider>
    </BrowserRouter>
  );
}

export default App;
