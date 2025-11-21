<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
      </div>

      <!-- Content -->
      <div v-else>
        <!-- Header -->
        <div class="mb-8">
          <button
            @click="navigateTo(`/analysis/${route.params.id}`)"
            class="text-blue-600 hover:text-blue-700 mb-4 font-medium"
          >
            ← Back to Analysis
          </button>
          <h1 class="text-4xl font-bold text-gray-900 mb-2">Smart Questions</h1>
          <p class="text-gray-600">
            Answer these questions to help us optimize your CV. Be honest and detailed.
          </p>
        </div>

        <!-- Questions -->
        <div class="space-y-6">
          <div
            v-for="(q, idx) in questions"
            :key="idx"
            class="bg-white rounded-2xl shadow-lg p-6"
          >
            <!-- Priority Badge -->
            <div class="flex items-start justify-between mb-3">
              <span :class="getPriorityBadgeClass(q.priority)" class="text-xs px-3 py-1 rounded-full font-semibold">
                {{ q.priority.toUpperCase() }} PRIORITY
              </span>
              <span class="text-sm text-blue-600 font-medium">
                {{ q.potential_impact }}
              </span>
            </div>

            <!-- Question -->
            <h3 class="text-lg font-semibold text-gray-900 mb-2">
              {{ idx + 1 }}. {{ q.question }}
            </h3>

            <!-- Why Asking -->
            <p class="text-sm text-gray-600 mb-4 italic">
              💡 {{ q.why_asking }}
            </p>

            <!-- Suggested Answers -->
            <div v-if="q.suggested_answers && q.suggested_answers.length > 0" class="mb-4">
              <p class="text-xs font-semibold text-gray-700 mb-2 uppercase tracking-wide">
                💬 Suggested Answers (click to use):
              </p>
              <div class="flex flex-wrap gap-2">
                <button
                  v-for="(suggestion, sIdx) in q.suggested_answers"
                  :key="sIdx"
                  @click="selectSuggestion(idx, suggestion)"
                  class="text-sm px-4 py-2 border-2 border-blue-200 bg-blue-50 text-blue-700 rounded-lg
                    hover:bg-blue-100 hover:border-blue-300 transition-all
                    focus:ring-2 focus:ring-blue-500 focus:outline-none"
                >
                  {{ suggestion }}
                </button>
              </div>
            </div>

            <!-- Answer Textarea -->
            <textarea
              v-model="answers[idx]"
              rows="4"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl
                focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Type your answer here, or click a suggested answer above..."
            />
          </div>
        </div>

        <!-- Submit Button -->
        <div class="mt-8 bg-white rounded-2xl shadow-lg p-6">
          <button
            @click="handleSubmit"
            :disabled="submitting || Object.keys(answers).length === 0"
            class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-xl
              font-semibold text-lg shadow-lg
              hover:from-blue-700 hover:to-indigo-700
              disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed
              transition-all transform hover:scale-[1.02]"
          >
            <span v-if="submitting">⏳ Generating Optimized CV...</span>
            <span v-else>✨ Generate Optimized CV</span>
          </button>
          <p class="text-sm text-gray-600 text-center mt-3">
            You can skip questions, but answering them improves optimization quality
          </p>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { Question, Priority } from '~/types/api'

const route = useRoute()
const { getAnalysis, submitAnswers, getDownloadURL } = useApi()

const loading = ref(true)
const submitting = ref(false)
const questions = ref<Question[]>([])
const answers = ref<Record<number, string>>({})

onMounted(async () => {
  try {
    const data = await getAnalysis(route.params.id as string)
    questions.value = data.questions || []
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

const selectSuggestion = (questionIndex: number, suggestion: string): void => {
  answers.value[questionIndex] = suggestion
}

const handleSubmit = async (): Promise<void> => {
  submitting.value = true

  try {
    await submitAnswers(route.params.id as string, answers.value)

    // Download PDF
    window.open(getDownloadURL(route.params.id as string), '_blank')

    // Redirect back to analysis
    await navigateTo(`/analysis/${route.params.id}`)
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}

const getPriorityBadgeClass = (priority: Priority): string => {
  if (priority === 'critical') return 'bg-red-100 text-red-700'
  if (priority === 'high') return 'bg-orange-100 text-orange-700'
  if (priority === 'medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-700'
}
</script>
