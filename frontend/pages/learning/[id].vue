<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-6xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="flex flex-col items-center gap-4">
          <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
          <p class="text-gray-600">{{ generating ? 'Creating personalized learning roadmap...' : 'Loading...' }}</p>
        </div>
      </div>

      <!-- Content -->
      <div v-else>
        <!-- Header -->
        <div class="mb-8">
          <button
            @click="navigateTo(`/cover-letter/${route.params.id}`)"
            class="text-blue-600 hover:text-blue-700 mb-4 font-medium"
          >
            ← Back
          </button>
          <h1 class="text-4xl font-bold text-gray-900 mb-2">📚 Learning Roadmap</h1>
          <p class="text-gray-600">
            Personalized plan to close skill gaps and boost your profile
          </p>
        </div>

        <!-- Score Progress -->
        <div class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl shadow-xl p-8 mb-8 text-white">
          <div class="flex items-center justify-between mb-4">
            <div>
              <div class="text-sm opacity-90 mb-1">Current Score</div>
              <div class="text-4xl font-bold">{{ learningPath?.current_score }}%</div>
            </div>
            <div class="text-3xl">→</div>
            <div>
              <div class="text-sm opacity-90 mb-1">Target Score</div>
              <div class="text-4xl font-bold">{{ learningPath?.target_score }}%</div>
            </div>
          </div>
          <div class="w-full bg-white/20 rounded-full h-3">
            <div
              class="bg-white h-3 rounded-full transition-all duration-1000"
              :style="{ width: `${(learningPath?.current_score / learningPath?.target_score) * 100}%` }"
            ></div>
          </div>
        </div>

        <!-- Quick Wins -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4 flex items-center gap-2">
            ⚡ Quick Wins (1-2 weeks)
          </h2>
          <div class="grid md:grid-cols-2 gap-4">
            <div
              v-for="(win, idx) in learningPath?.quick_wins"
              :key="idx"
              class="bg-green-50 rounded-2xl p-6 border-2 border-green-200"
            >
              <div class="flex justify-between items-start mb-3">
                <h3 class="font-semibold text-gray-900">{{ win.action }}</h3>
                <span class="text-green-600 font-bold text-sm">{{ win.impact }}</span>
              </div>
              <p class="text-sm text-gray-600 mb-3">⏱️ {{ win.time }}</p>
              <ul class="space-y-1">
                <li v-for="(detail, didx) in win.details" :key="didx" class="text-sm text-gray-700">
                  • {{ detail }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Priority Areas -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">🎯 Priority Learning Areas</h2>
          <div class="space-y-6">
            <div
              v-for="(area, idx) in learningPath?.priority_areas"
              :key="idx"
              class="bg-white rounded-3xl shadow-lg p-8"
            >
              <!-- Area Header -->
              <div class="flex justify-between items-start mb-4">
                <div>
                  <span class="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full font-semibold mr-2">
                    PRIORITY {{ area.priority }}
                  </span>
                  <h3 class="text-2xl font-bold text-gray-900 mt-2">{{ area.skill }}</h3>
                  <p class="text-gray-600 mt-1">{{ area.current_level }} → {{ area.target_level }}</p>
                </div>
                <div class="text-right">
                  <div class="text-2xl font-bold text-blue-600">{{ area.impact }}</div>
                  <div class="text-sm text-gray-600">{{ area.time }}</div>
                </div>
              </div>

              <!-- Why Important -->
              <p class="text-gray-700 mb-6 bg-blue-50 p-4 rounded-xl">
                💡 {{ area.why_important }}
              </p>

              <!-- Courses -->
              <div v-if="area.courses?.length" class="mb-6">
                <h4 class="font-semibold text-gray-900 mb-3">📖 Recommended Courses</h4>
                <div class="space-y-3">
                  <div
                    v-for="(course, cidx) in area.courses"
                    :key="cidx"
                    class="border border-gray-200 rounded-xl p-4 hover:shadow-md transition-all"
                  >
                    <div class="flex justify-between items-start mb-2">
                      <div>
                        <h5 class="font-semibold text-gray-900">{{ course.name }}</h5>
                        <p class="text-sm text-gray-600">{{ course.platform }} • {{ course.duration }}</p>
                      </div>
                      <div class="text-right">
                        <span :class="course.cost === 'FREE' ? 'text-green-600 font-bold' : 'text-gray-600'">
                          {{ course.cost }}
                        </span>
                        <div class="text-sm text-blue-600">{{ course.impact }}</div>
                      </div>
                    </div>
                    <div class="flex flex-wrap gap-2 mt-2">
                      <span
                        v-for="(topic, tidx) in course.topics"
                        :key="tidx"
                        class="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded"
                      >
                        {{ topic }}
                      </span>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Projects -->
              <div v-if="area.projects?.length">
                <h4 class="font-semibold text-gray-900 mb-3">🛠️ Hands-On Projects</h4>
                <div class="space-y-3">
                  <div
                    v-for="(project, pidx) in area.projects"
                    :key="pidx"
                    class="bg-purple-50 border border-purple-200 rounded-xl p-4"
                  >
                    <div class="flex justify-between items-start mb-2">
                      <h5 class="font-semibold text-gray-900">{{ project.name }}</h5>
                      <div class="text-right">
                        <div class="text-sm text-gray-600">{{ project.time }}</div>
                        <div class="text-sm text-purple-600">{{ project.impact }}</div>
                      </div>
                    </div>
                    <p class="text-sm text-gray-700 mb-2">{{ project.description }}</p>
                    <div class="text-xs text-gray-600 mb-2">
                      Tech: {{ project.technologies?.join(', ') }}
                    </div>
                    <ul class="space-y-1">
                      <li v-for="(feature, fidx) in project.features" :key="fidx" class="text-sm text-gray-700">
                        ✓ {{ feature }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Weekly Roadmap -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">🗓️ 10-Week Roadmap</h2>
          <div class="bg-white rounded-3xl shadow-lg p-8">
            <div class="space-y-4">
              <div
                v-for="(week, idx) in learningPath?.weekly_roadmap"
                :key="idx"
                class="border-l-4 border-blue-500 pl-6 py-3 hover:bg-blue-50 transition-all rounded-r-xl"
              >
                <div class="flex justify-between items-start mb-2">
                  <div>
                    <div class="font-semibold text-gray-900">Week {{ week.week }}</div>
                    <div class="text-lg font-bold text-blue-600">{{ week.focus }}</div>
                  </div>
                  <div class="text-right">
                    <div class="text-sm text-gray-600">{{ week.hours }}</div>
                    <div class="text-lg font-bold text-green-600">{{ week.score_after }}%</div>
                  </div>
                </div>
                <ul class="space-y-1 mb-2">
                  <li v-for="(task, tidx) in week.tasks" :key="tidx" class="text-sm text-gray-700">
                    • {{ task }}
                  </li>
                </ul>
                <div class="text-xs text-gray-600">
                  Deliverables: {{ week.deliverables?.join(', ') }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Total Investment -->
        <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-3xl shadow-lg p-8 mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">💰 Investment Summary</h2>
          <div class="grid md:grid-cols-4 gap-6">
            <div>
              <div class="text-sm text-gray-600 mb-1">Total Time</div>
              <div class="text-2xl font-bold text-gray-900">{{ learningPath?.total_investment?.time }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-600 mb-1">Total Cost</div>
              <div class="text-2xl font-bold text-gray-900">{{ learningPath?.total_investment?.cost }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-600 mb-1">Score Gain</div>
              <div class="text-2xl font-bold text-green-600">{{ learningPath?.total_investment?.score_improvement }}</div>
            </div>
            <div>
              <div class="text-sm text-gray-600 mb-1">Timeline</div>
              <div class="text-2xl font-bold text-gray-900">{{ learningPath?.total_investment?.timeline }}</div>
            </div>
          </div>
          <div class="mt-6 p-4 bg-white rounded-xl">
            <div class="font-semibold text-gray-900 mb-2">ROI Analysis</div>
            <p class="text-gray-700">{{ learningPath?.total_investment?.roi_analysis }}</p>
          </div>
        </div>

        <!-- Resources -->
        <div class="bg-white rounded-3xl shadow-lg p-8 mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-6">📌 Additional Resources</h2>
          <div class="grid md:grid-cols-3 gap-6">
            <div>
              <h3 class="font-semibold text-gray-900 mb-3">Free Platforms</h3>
              <ul class="space-y-2">
                <li v-for="(platform, idx) in learningPath?.resources?.free_platforms" :key="idx" class="text-sm text-gray-700">
                  • {{ platform }}
                </li>
              </ul>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-3">Communities</h3>
              <ul class="space-y-2">
                <li v-for="(community, idx) in learningPath?.resources?.communities" :key="idx" class="text-sm text-gray-700">
                  • {{ community }}
                </li>
              </ul>
            </div>
            <div>
              <h3 class="font-semibold text-gray-900 mb-3">Certifications</h3>
              <ul class="space-y-2">
                <li v-for="(cert, idx) in learningPath?.resources?.certifications" :key="idx" class="text-sm text-gray-700">
                  • {{ cert }}
                </li>
              </ul>
            </div>
          </div>
        </div>

        <!-- Next Step -->
        <div class="bg-gradient-to-r from-purple-50 to-pink-50 rounded-3xl shadow-lg p-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-4">🎯 Ready for Interviews?</h3>
          <p class="text-gray-600 mb-6">
            Get tailored interview questions and practice your responses
          </p>
          <button
            @click="navigateTo(`/interview/${route.params.id}`)"
            class="px-8 py-4 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl
              font-semibold text-lg shadow-lg hover:from-purple-700 hover:to-pink-700
              transition-all transform hover:scale-105"
          >
            💼 Prepare for Interviews
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const api = useApi()

const loading = ref(true)
const generating = ref(false)
const learningPath = ref<any>(null)

onMounted(async () => {
  try {
    // Try to get existing learning path
    try {
      const data = await api.getLearningPath(route.params.id as string)
      learningPath.value = data.learning_path
      loading.value = false
    } catch (err: any) {
      // Learning path doesn't exist, generate it
      if (err?.statusCode === 404 || err?.response?.status === 404) {
        generating.value = true
        const data = await api.generateLearningPath(route.params.id as string)
        learningPath.value = data.learning_path
      } else {
        throw err
      }
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
    generating.value = false
  }
})
</script>
