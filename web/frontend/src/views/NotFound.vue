<template>
  <div class="not-found">
    <el-result icon="error" title="404" sub-title="页面不存在">
      <template #extra>
        <el-button type="primary" @click="$router.push('/')">返回首页</el-button>
      </template>
    </el-result>
    <div class="footer">
      <p>基于 <el-link href="https://github.com/Samueli924/chaoxing" target="_blank">Samueli924/chaoxing</el-link> 原项目</p>
      <p>增强版本: <el-link href="https://github.com/ViVi141/chaoxing" target="_blank">ViVi141/chaoxing</el-link></p>
    </div>
  </div>
</template>

<style scoped>
.not-found { height: 100vh; display: flex; flex-direction: column; justify-content: center; align-items: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); }
.footer { text-align: center; color: #ffffff; margin-top: 20px; font-size: 13px; }
.footer p { margin: 5px 0; }
</style>

