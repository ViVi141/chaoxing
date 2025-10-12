<template>
  <div>
    <el-row :gutter="20" style="margin-bottom: 20px">
      <el-col :span="6">
        <el-card><el-statistic title="总用户数" :value="stats.total_users"><template #prefix><el-icon><User /></el-icon></template></el-statistic></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="活跃用户" :value="stats.active_users"><template #prefix><el-icon color="#67C23A"><UserFilled /></el-icon></template></el-statistic></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="运行任务" :value="stats.running_tasks"><template #prefix><el-icon color="#E6A23C"><VideoPlay /></el-icon></template></el-statistic></el-card>
      </el-col>
      <el-col :span="6">
        <el-card><el-statistic title="完成任务" :value="stats.completed_tasks"><template #prefix><el-icon color="#409EFF"><CircleCheck /></el-icon></template></el-statistic></el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20">
      <el-col :span="12">
        <el-card>
          <template #header><span>任务状态分布</span></template>
          <div ref="taskChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card>
          <template #header><span>用户活跃度</span></template>
          <div ref="userChartRef" style="height: 300px"></div>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { adminAPI } from '@/api'
import * as echarts from 'echarts'

const stats = ref({})
const taskChartRef = ref(null)
const userChartRef = ref(null)

const loadStats = async () => {
  const res = await adminAPI.getStatistics()
  stats.value = res.data
  
  // 绘制图表
  if (taskChartRef.value) {
    const chart = echarts.init(taskChartRef.value)
    chart.setOption({
      tooltip: { trigger: 'item' },
      series: [{
        type: 'pie',
        radius: '50%',
        data: [
          { value: stats.value.running_tasks, name: '运行中' },
          { value: stats.value.completed_tasks, name: '已完成' },
          { value: stats.value.failed_tasks, name: '失败' }
        ]
      }]
    })
  }
}

onMounted(() => loadStats())
</script>

