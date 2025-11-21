<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-6xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="text-center">
          <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600">Generating personalized learning path...</p>
        </div>
      </div>

      <!-- Content -->
      <div v-else-if="data">
        <!-- Header -->
        <div class="mb-8">
          <button
            @click="navigateTo(`/analysis/${route.params.id}`)"
            class="text-blue-600 hover:text-blue-700 mb-4 font-medium"
          >
            ← Back to Analysis
          </button>
          <h1 class="text-4xl font-bold text-gray-900 mb-2">🎓 Learning Recommendations</h1>
          <p class="text-gray-600">
            Personalized learning path to improve your score from {{ data.current_score }}% to {{ data.target_score }}%+
          </p>
        </div>

        <!-- Progress Overview -->
        <div class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">Your Learning Journey</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div class="text-center">
              <div class="text-4xl font-bold text-blue-600">{{ data.current_score }}%</div>
              <div class="text-sm text-gray-600">Current Score</div>
            </div>
            <div class="text-center">
              <div class="text-4xl font-bold text-green-600">{{ data.target_score }}%</div>
              <div class="text-sm text-gray-600">Target Score</div>
            </div>
            <div class="text-center">
              <div class="text-4xl font-bold text-indigo-600">{{ data.estimated_weeks }}</div>
              <div class="text-sm text-gray-600">Weeks to Complete</div>
            </div>
          </div>
        </div>

        <!-- Quick Wins -->
        <div v-if="data.quick_wins?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">⚡ Quick Wins (This Week)</h2>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="(win, idx) in data.quick_wins"
              :key="idx"
              class="border border-gray-200 rounded-xl p-4"
            >
              <div class="flex justify-between items-start mb-2">
                <h3 class="font-semibold text-gray-900">{{ win.action }}</h3>
                <span class="text-sm text-blue-600 font-medium">{{ win.impact }}</span>
              </div>
              <p class="text-sm text-gray-600 mb-2">{{ win.description }}</p>
              <p class="text-xs text-gray-500">⏱️ {{ win.time }}</p>
            </div>
          </div>
        </div>

        <!-- Priority Courses -->
        <div v-if="data.priority_courses?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">📚 Recommended Courses</h2>
          <div class="space-y-4">
            <div
              v-for="(course, idx) in data.priority_courses"
              :key="idx"
              class="border border-gray-200 rounded-xl p-6 hover:shadow-md transition-shadow"
            >
              <div class="flex justify-between items-start mb-3">
                <div class="flex-1">
                  <div class="flex items-center gap-3 mb-2">
                    <h3 class="text-lg font-semibold text-gray-900">{{ course.title }}</h3>
                    <span :class="getPriorityBadgeClass(course.priority)" class="text-xs px-3 py-1 rounded-full">
                      {{ course.priority.toUpperCase() }}
                    </span>
                  </div>
                  <div class="flex items-center gap-4 text-sm text-gray-600 mb-2">
                    <span>📱 {{ course.platform }}</span>
                    <span>⏱️ {{ course.duration }}</span>
                    <span>💰 {{ course.cost }}</span>
                    <span class="text-blue-600 font-medium">{{ course.impact }}</span>
                  </div>
                </div>
              </div>

              <p class="text-sm text-gray-700 mb-3">{{ course.why_recommended }}</p>

              <div class="flex flex-wrap gap-2 mb-3">
                <span
                  v-for="(skill, sidx) in course.skills_covered"
                  :key="sidx"
                  class="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                >
                  {{ skill }}
                </span>
              </div>

              <a
                v-if="course.url"
                :href="course.url"
                target="_blank"
                class="inline-block text-sm text-blue-600 hover:text-blue-700 font-medium"
              >
                View Course →
              </a>
            </div>
          </div>
        </div>

        <!-- 10-Week Roadmap -->
        <div v-if="data.roadmap?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">🗓️ 10-Week Roadmap</h2>
          <div class="space-y-4">
            <div
              v-for="(week, idx) in data.roadmap"
              :key="idx"
              class="border-l-4 border-blue-500 pl-6 py-4"
            >
              <div class="flex justify-between items-start mb-2">
                <h3 class="text-lg font-semibold text-gray-900">Week {{ week.week }}: {{ week.focus }}</h3>
                <span class="text-sm text-gray-600">{{ week.hours_per_week }} hrs/week</span>
              </div>

              <ul class="space-y-1 mb-3">
                <li v-for="(task, tidx) in week.tasks" :key="tidx" class="text-sm text-gray-700">
                  • {{ task }}
                </li>
              </ul>

              <p class="text-sm text-blue-600 font-medium">🎯 Milestone: {{ week.milestone }}</p>
            </div>
          </div>
        </div>

        <!-- Total Investment -->
        <div v-if="data.total_investment" class="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-3xl shadow-lg p-8 text-white mb-6">
          <h2 class="text-2xl font-bold mb-6">💎 Total Investment</h2>
          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div>
              <div class="text-3xl font-bold">{{ data.total_investment.time_hours }} hrs</div>
              <div class="text-sm opacity-90">Total Learning Time</div>
            </div>
            <div>
              <div class="text-3xl font-bold">${{ data.total_investment.cost_usd }}</div>
              <div class="text-sm opacity-90">Total Cost</div>
            </div>
            <div>
              <div class="text-3xl font-bold">{{ data.total_investment.expected_score_improvement }}</div>
              <div class="text-sm opacity-90">Expected Improvement</div>
            </div>
          </div>
          <p class="mt-6 text-sm opacity-90">
            🚀 ROI: Potential salary increase of $50K+ with improved profile
          </p>
        </div>

        <!-- General Recommendations -->
        <div v-if="data.recommendations?.length" class="bg-white rounded-3xl shadow-lg p-8">
          <h2 class="text-2xl font-bold mb-6">💡 Additional Tips</h2>
          <ul class="space-y-3">
            <li v-for="(rec, idx) in data.recommendations" :key="idx" class="flex items-start">
              <span class="text-green-500 mr-3 text-xl">✓</span>
              <span class="text-gray-700">{{ rec }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { LearningRecommendationsData, Priority } from '~/types/api'

const route = useRoute()
const { getLearningRecommendations } = useApi()

const loading = ref(true)
const data = ref<LearningRecommendationsData | null>(null)

onMounted(async () => {
  try {
    const result = await getLearningRecommendations(route.params.id as string)
    data.value = result.learning_recommendations
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

const getPriorityBadgeClass = (priority: Priority): string => {
  if (priority === 'critical') return 'bg-red-100 text-red-700'
  if (priority === 'high') return 'bg-orange-100 text-orange-700'
  if (priority === 'medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-700'
}
</script>
