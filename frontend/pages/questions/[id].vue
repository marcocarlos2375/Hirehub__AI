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

            <!-- Suggested Answers (Multiple Choice) -->
            <div v-if="q.suggested_answers && q.suggested_answers.length > 0" class="space-y-3 mb-4">
              <p class="text-sm font-semibold text-gray-700 mb-2">Choose an answer or write your own:</p>

              <!-- Suggested Answer Options -->
              <div
                v-for="(option, optIdx) in q.suggested_answers"
                :key="`option-${optIdx}`"
                @click="selectSuggestedAnswer(idx, option)"
                :class="[
                  'p-4 border-2 rounded-xl cursor-pointer transition-all',
                  answers[idx] === option
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                ]"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-shrink-0 mt-0.5">
                    <div :class="[
                      'w-5 h-5 rounded-full border-2 flex items-center justify-center',
                      answers[idx] === option
                        ? 'border-blue-500 bg-blue-500'
                        : 'border-gray-300'
                    ]">
                      <div v-if="answers[idx] === option" class="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                  </div>
                  <p class="text-sm text-gray-700 leading-relaxed">{{ option }}</p>
                </div>
              </div>

              <!-- Custom Answer Option -->
              <div
                @click="selectCustomAnswer(idx)"
                :class="[
                  'p-4 border-2 rounded-xl cursor-pointer transition-all',
                  selectedCustom[idx]
                    ? 'border-blue-500 bg-blue-50 shadow-md'
                    : 'border-gray-200 hover:border-blue-300 hover:bg-gray-50'
                ]"
              >
                <div class="flex items-start gap-3">
                  <div class="flex-shrink-0 mt-0.5">
                    <div :class="[
                      'w-5 h-5 rounded-full border-2 flex items-center justify-center',
                      selectedCustom[idx]
                        ? 'border-blue-500 bg-blue-500'
                        : 'border-gray-300'
                    ]">
                      <div v-if="selectedCustom[idx]" class="w-2 h-2 bg-white rounded-full"></div>
                    </div>
                  </div>
                  <p class="text-sm font-medium text-gray-700">✍️ Write your own custom answer</p>
                </div>
              </div>

              <!-- Custom Answer Textarea (shown when custom is selected) -->
              <div v-if="selectedCustom[idx]" class="mt-3">
                <textarea
                  v-model="answers[idx]"
                  rows="4"
                  class="w-full px-4 py-3 border-2 border-blue-300 rounded-xl
                    focus:ring-2 focus:ring-blue-500 focus:border-blue-500 resize-none"
                  placeholder="Type your custom answer here..."
                  @input="onCustomAnswerInput(idx)"
                />
              </div>

              <!-- Answer Tips -->
              <div v-if="q.answer_tips && q.answer_tips.length > 0" class="mt-4 p-3 bg-amber-50 border border-amber-200 rounded-xl">
                <p class="text-xs font-semibold text-amber-800 mb-2">💡 Tips for answering:</p>
                <ul class="text-xs text-gray-700 space-y-1">
                  <li v-for="(tip, tipIdx) in q.answer_tips" :key="tipIdx" class="flex items-start gap-2">
                    <span class="text-amber-600">•</span>
                    <span>{{ tip }}</span>
                  </li>
                </ul>
              </div>
            </div>

            <!-- Fallback: Plain textarea if no suggestions (backward compatibility) -->
            <textarea
              v-else
              v-model="answers[idx]"
              rows="4"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl
                focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none"
              placeholder="Type your answer here..."
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
const route = useRoute()
const router = useRouter()
const { getAnalysis, submitAnswers, getDownloadURL } = useApi()

const loading = ref(true)
const submitting = ref(false)
const questions = ref<any[]>([])
const answers = ref<Record<number, string>>({})
const selectedCustom = ref<Record<number, boolean>>({})

onMounted(async () => {
  try {
    const data = await getAnalysis(route.params.id as string)
    questions.value = data.questions
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

const handleSubmit = async () => {
  submitting.value = true

  try {
    await submitAnswers(route.params.id as string, answers.value)

    // Download PDF
    window.open(getDownloadURL(route.params.id as string), '_blank')

    // Redirect to cover letter page
    await navigateTo(`/cover-letter/${route.params.id}`)
  } catch (err) {
    console.error(err)
  } finally {
    submitting.value = false
  }
}

const selectSuggestedAnswer = (idx: number, answer: string) => {
  answers.value[idx] = answer
  selectedCustom.value[idx] = false
}

const selectCustomAnswer = (idx: number) => {
  selectedCustom.value[idx] = true
  // Clear answer if switching to custom (user will type their own)
  if (!answers.value[idx] || questions.value[idx]?.suggested_answers?.includes(answers.value[idx])) {
    answers.value[idx] = ''
  }
}

const onCustomAnswerInput = (idx: number) => {
  // Ensure custom remains selected while typing
  selectedCustom.value[idx] = true
}

const getPriorityBadgeClass = (priority: string) => {
  if (priority === 'critical') return 'bg-red-100 text-red-700'
  if (priority === 'high') return 'bg-orange-100 text-orange-700'
  if (priority === 'medium') return 'bg-yellow-100 text-yellow-700'
  return 'bg-gray-100 text-gray-700'
}
</script>
