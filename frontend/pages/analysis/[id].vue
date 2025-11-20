<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-6xl mx-auto">
      <!-- Loading State -->
      <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="text-center">
          <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600">Loading analysis...</p>
        </div>
      </div>

      <!-- Content -->
      <div v-else-if="data">
        <!-- Header -->
        <div class="mb-8">
          <button
            @click="navigateTo('/')"
            class="text-blue-600 hover:text-blue-700 mb-4 font-medium"
          >
            ← Back to Home
          </button>
          <h1 class="text-4xl font-bold text-gray-900">Analysis Results</h1>
        </div>

        <!-- Score Card -->
        <div class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <div class="text-center">
            <div :class="getScoreColorClass(data.score)" class="text-7xl font-bold">
              {{ Math.round(data.score) }}%
            </div>
            <p class="text-2xl text-gray-600 mt-2 font-medium">
              {{ getScoreLabel(data.score) }}
            </p>
            <div class="w-full bg-gray-200 rounded-full h-4 mt-6">
              <div
                class="bg-gradient-to-r from-blue-600 to-indigo-600 h-4 rounded-full transition-all duration-500"
                :style="{ width: `${data.score}%` }"
              ></div>
            </div>
          </div>
        </div>

        <!-- Score Breakdown -->
        <div v-if="data.breakdown" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">Score Breakdown</h2>
          <div class="space-y-4">
            <div
              v-for="([key, value], index) in Object.entries(data.breakdown)"
              :key="index"
              class="flex items-center justify-between"
            >
              <div class="flex-1">
                <div class="flex justify-between mb-1">
                  <span class="font-semibold capitalize">
                    {{ key.replace('_', ' ') }}
                  </span>
                  <span class="text-gray-600">
                    {{ Math.round((value as any).score) }}% (weight: {{ (value as any).weight }}%)
                  </span>
                </div>
                <div class="w-full bg-gray-200 rounded-full h-2">
                  <div
                    class="bg-blue-600 h-2 rounded-full transition-all"
                    :style="{ width: `${(value as any).score}%` }"
                  ></div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Strengths -->
        <div v-if="data.strengths?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">💪 Your Strengths</h2>
          <ul class="space-y-3">
            <li v-for="(strength, idx) in data.strengths" :key="idx" class="flex items-start">
              <span class="text-green-500 mr-3 text-xl">✓</span>
              <span class="text-gray-700">{{ strength }}</span>
            </li>
          </ul>
        </div>

        <!-- Gaps -->
        <div v-if="data.gaps?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">🎯 Areas to Improve</h2>
          <div class="space-y-4">
            <div
              v-for="(gap, idx) in data.gaps"
              :key="idx"
              class="border-l-4 border-yellow-500 pl-4 py-2"
            >
              <div class="flex items-center justify-between mb-1">
                <span class="font-semibold text-gray-900">{{ gap.gap }}</span>
                <span :class="getPriorityClass(gap.priority)" class="text-sm px-3 py-1 rounded-full">
                  {{ gap.priority.toUpperCase() }}
                </span>
              </div>
              <p class="text-sm text-gray-600">Impact: {{ gap.impact }}</p>
            </div>
          </div>
        </div>

        <!-- Questions CTA -->
        <div class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">
            💬 Smart Questions ({{ data.questions?.length || 0 }})
          </h2>
          <p class="text-gray-600 mb-6">
            Answer these questions to improve your CV optimization. Your answers will help us
            uncover hidden experience and boost your score.
          </p>
          <button
            @click="navigateTo(`/questions/${route.params.id}`)"
            class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-xl
              font-semibold text-lg shadow-lg hover:from-blue-700 hover:to-indigo-700
              transition-all transform hover:scale-[1.02]"
          >
            Answer Questions & Optimize CV →
          </button>
        </div>

        <!-- Next Steps (Phases 7-9) - Only show if CV is optimized -->
        <div v-if="data.optimized_cv" class="bg-gradient-to-br from-indigo-50 to-blue-50 rounded-3xl shadow-lg p-8">
          <h2 class="text-3xl font-bold mb-2 text-gray-900">🚀 Next Steps</h2>
          <p class="text-gray-600 mb-6">
            Your CV is optimized! Now take these additional steps to maximize your application success.
          </p>

          <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
            <!-- Cover Letter -->
            <div class="bg-white rounded-2xl shadow-md p-6 hover:shadow-xl transition-shadow">
              <div class="text-4xl mb-4">📝</div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">Cover Letter</h3>
              <p class="text-sm text-gray-600 mb-4">
                Generate a personalized, compelling cover letter tailored to this job posting.
              </p>
              <button
                v-if="!coverLetterGenerated"
                @click="handleGenerateCoverLetter"
                :disabled="generatingCoverLetter"
                class="w-full bg-blue-600 text-white py-3 px-4 rounded-xl font-semibold
                  hover:bg-blue-700 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {{ generatingCoverLetter ? 'Generating...' : 'Generate Cover Letter' }}
              </button>
              <a
                v-else
                :href="getCoverLetterDownloadURL(route.params.id as string)"
                download
                class="block w-full bg-green-600 text-white py-3 px-4 rounded-xl font-semibold text-center
                  hover:bg-green-700 transition-all"
              >
                Download Cover Letter
              </a>
            </div>

            <!-- Learning Path -->
            <div class="bg-white rounded-2xl shadow-md p-6 hover:shadow-xl transition-shadow">
              <div class="text-4xl mb-4">🎓</div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">Learning Path</h3>
              <p class="text-sm text-gray-600 mb-4">
                Get personalized course recommendations and a 10-week roadmap to improve your skills.
              </p>
              <button
                @click="navigateTo(`/learning/${route.params.id}`)"
                class="w-full bg-indigo-600 text-white py-3 px-4 rounded-xl font-semibold
                  hover:bg-indigo-700 transition-all"
              >
                View Learning Path →
              </button>
            </div>

            <!-- Interview Prep -->
            <div class="bg-white rounded-2xl shadow-md p-6 hover:shadow-xl transition-shadow">
              <div class="text-4xl mb-4">🎤</div>
              <h3 class="text-xl font-bold text-gray-900 mb-2">Interview Prep</h3>
              <p class="text-sm text-gray-600 mb-4">
                Practice with likely questions, suggested answers, and STAR method examples.
              </p>
              <button
                @click="navigateTo(`/interview/${route.params.id}`)"
                class="w-full bg-purple-600 text-white py-3 px-4 rounded-xl font-semibold
                  hover:bg-purple-700 transition-all"
              >
                Start Interview Prep →
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { getAnalysis, generateCoverLetter, getCoverLetterDownloadURL } = useApi()

const loading = ref(true)
const data = ref<any>(null)
const generatingCoverLetter = ref(false)
const coverLetterGenerated = ref(false)

onMounted(async () => {
  try {
    data.value = await getAnalysis(route.params.id as string)
    // Check if cover letter already exists
    if (data.value.optimized_cv) {
      // Fetch fresh data to check cover_letter field
      const freshData = await getAnalysis(route.params.id as string)
      coverLetterGenerated.value = !!freshData.optimized_cv
    }
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

const handleGenerateCoverLetter = async () => {
  generatingCoverLetter.value = true
  try {
    await generateCoverLetter(route.params.id as string)
    coverLetterGenerated.value = true
  } catch (err) {
    console.error('Error generating cover letter:', err)
    alert('Failed to generate cover letter. Please try again.')
  } finally {
    generatingCoverLetter.value = false
  }
}

const getScoreColorClass = (score: number) => {
  if (score >= 80) return 'text-green-600'
  if (score >= 60) return 'text-yellow-600'
  return 'text-red-600'
}

const getScoreLabel = (score: number) => {
  if (score >= 80) return 'Excellent Match'
  if (score >= 60) return 'Good Match'
  return 'Needs Improvement'
}

const getPriorityClass = (priority: string) => {
  if (priority === 'critical') return 'bg-red-100 text-red-700'
  if (priority === 'high') return 'bg-orange-100 text-orange-700'
  return 'bg-yellow-100 text-yellow-700'
}
</script>
