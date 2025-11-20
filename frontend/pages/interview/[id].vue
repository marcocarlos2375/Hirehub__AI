<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-6xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="text-center">
          <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600">Preparing interview guide...</p>
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
          <h1 class="text-4xl font-bold text-gray-900 mb-2">🎤 Interview Preparation</h1>
          <p class="text-gray-600">
            Comprehensive guide with questions, answers, and tips for each interview stage
          </p>
        </div>

        <!-- Interview Stages -->
        <div v-if="data.stages?.length" class="space-y-6 mb-6">
          <div
            v-for="(stage, sidx) in data.stages"
            :key="sidx"
            class="bg-white rounded-3xl shadow-lg p-8"
          >
            <div class="mb-6">
              <h2 class="text-2xl font-bold text-gray-900 mb-2">{{ stage.stage_name }}</h2>
              <div class="flex items-center gap-4 text-sm text-gray-600">
                <span>⏱️ {{ stage.duration }}</span>
                <span>👤 {{ stage.interviewer }}</span>
                <span>🎯 {{ stage.focus }}</span>
              </div>
            </div>

            <!-- Questions for this stage -->
            <div class="space-y-6">
              <div
                v-for="(q, qidx) in stage.questions"
                :key="qidx"
                class="border-l-4 border-blue-500 pl-6 py-4"
              >
                <!-- Question Header -->
                <div class="flex items-start justify-between mb-3">
                  <h3 class="text-lg font-semibold text-gray-900 flex-1">
                    {{ qidx + 1 }}. {{ q.question }}
                  </h3>
                  <span :class="getPriorityBadgeClass(q.priority)" class="text-xs px-3 py-1 rounded-full ml-4">
                    {{ q.priority.toUpperCase() }}
                  </span>
                </div>

                <!-- Why They Ask -->
                <div class="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-3">
                  <p class="text-sm text-blue-800">
                    <span class="font-semibold">💡 Why they ask:</span> {{ q.why_they_ask }}
                  </p>
                </div>

                <!-- Suggested Answer -->
                <div class="bg-gray-50 border border-gray-200 rounded-lg p-4 mb-3">
                  <p class="text-sm font-semibold text-gray-700 mb-2">✨ Suggested Answer:</p>
                  <p class="text-sm text-gray-800 whitespace-pre-wrap">{{ q.suggested_answer }}</p>
                </div>

                <!-- Tips -->
                <div v-if="q.tips?.length">
                  <p class="text-sm font-semibold text-gray-700 mb-2">💡 Tips:</p>
                  <ul class="space-y-1">
                    <li v-for="(tip, tidx) in q.tips" :key="tidx" class="text-sm text-gray-700">
                      • {{ tip }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Technical Deep Dives -->
        <div v-if="data.technical_deep_dives?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">🔧 Technical Deep Dives</h2>
          <div class="space-y-6">
            <div
              v-for="(topic, idx) in data.technical_deep_dives"
              :key="idx"
              class="border border-gray-200 rounded-xl p-6"
            >
              <h3 class="text-lg font-semibold text-gray-900 mb-3">{{ topic.topic }}</h3>

              <div class="mb-4">
                <p class="text-sm font-semibold text-gray-700 mb-2">Likely Questions:</p>
                <ul class="space-y-1">
                  <li v-for="(q, qidx) in topic.likely_questions" :key="qidx" class="text-sm text-gray-700">
                    • {{ q }}
                  </li>
                </ul>
              </div>

              <div class="mb-4">
                <p class="text-sm font-semibold text-gray-700 mb-2">How to Prepare:</p>
                <ul class="space-y-1">
                  <li v-for="(tip, tidx) in topic.preparation_tips" :key="tidx" class="text-sm text-gray-700">
                    ✓ {{ tip }}
                  </li>
                </ul>
              </div>

              <div v-if="topic.example_projects_to_mention?.length">
                <p class="text-sm font-semibold text-gray-700 mb-2">Projects to Mention:</p>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(proj, pidx) in topic.example_projects_to_mention"
                    :key="pidx"
                    class="text-xs bg-blue-100 text-blue-700 px-3 py-1 rounded-full"
                  >
                    {{ proj }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- STAR Method Examples -->
        <div v-if="data.star_method_examples?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">⭐ STAR Method Examples</h2>
          <p class="text-sm text-gray-600 mb-6">
            Use these structured examples from your experience for behavioral questions
          </p>
          <div class="space-y-6">
            <div
              v-for="(example, idx) in data.star_method_examples"
              :key="idx"
              class="border border-gray-200 rounded-xl p-6"
            >
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                <div>
                  <p class="text-xs font-semibold text-gray-500 mb-1">SITUATION</p>
                  <p class="text-sm text-gray-800">{{ example.situation }}</p>
                </div>
                <div>
                  <p class="text-xs font-semibold text-gray-500 mb-1">TASK</p>
                  <p class="text-sm text-gray-800">{{ example.task }}</p>
                </div>
                <div>
                  <p class="text-xs font-semibold text-gray-500 mb-1">ACTION</p>
                  <p class="text-sm text-gray-800">{{ example.action }}</p>
                </div>
                <div>
                  <p class="text-xs font-semibold text-gray-500 mb-1">RESULT</p>
                  <p class="text-sm text-green-700 font-medium">{{ example.result }}</p>
                </div>
              </div>

              <div v-if="example.applicable_to?.length">
                <p class="text-xs font-semibold text-gray-500 mb-2">Can be used for:</p>
                <div class="flex flex-wrap gap-2">
                  <span
                    v-for="(topic, tidx) in example.applicable_to"
                    :key="tidx"
                    class="text-xs bg-green-100 text-green-700 px-3 py-1 rounded-full"
                  >
                    {{ topic }}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Red Flags to Address -->
        <div v-if="data.red_flags_to_address?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">⚠️ Potential Concerns & How to Address</h2>
          <div class="space-y-4">
            <div
              v-for="(flag, idx) in data.red_flags_to_address"
              :key="idx"
              class="border-l-4 border-yellow-500 pl-6 py-4"
            >
              <h3 class="font-semibold text-gray-900 mb-2">{{ flag.concern }}</h3>
              <p class="text-sm text-gray-700 mb-3">
                <span class="font-semibold">Strategy:</span> {{ flag.how_to_address }}
              </p>
              <div class="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <p class="text-sm text-gray-800">
                  <span class="font-semibold">Example response:</span> "{{ flag.example_response }}"
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Questions to Ask Them -->
        <div v-if="data.questions_to_ask_them?.length" class="bg-white rounded-3xl shadow-lg p-8 mb-6">
          <h2 class="text-2xl font-bold mb-6">❓ Questions to Ask Them</h2>
          <p class="text-sm text-gray-600 mb-6">
            Asking smart questions shows you're engaged and thinking strategically
          </p>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div
              v-for="(q, idx) in data.questions_to_ask_them"
              :key="idx"
              class="border border-gray-200 rounded-xl p-4"
            >
              <p class="text-sm font-semibold text-gray-900 mb-2">{{ q.question }}</p>
              <div class="flex items-center gap-2 mb-2">
                <span class="text-xs bg-gray-100 text-gray-700 px-2 py-1 rounded">{{ q.category }}</span>
              </div>
              <p class="text-xs text-gray-600">💡 {{ q.why_ask }}</p>
            </div>
          </div>
        </div>

        <!-- General Tips -->
        <div v-if="data.general_tips?.length" class="bg-gradient-to-r from-blue-500 to-indigo-600 rounded-3xl shadow-lg p-8 text-white">
          <h2 class="text-2xl font-bold mb-6">🎯 General Interview Tips</h2>
          <ul class="space-y-3">
            <li v-for="(tip, idx) in data.general_tips" :key="idx" class="flex items-start">
              <span class="mr-3 text-xl">✓</span>
              <span class="opacity-90">{{ tip }}</span>
            </li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const route = useRoute()
const { getInterviewPrep } = useApi()

const loading = ref(true)
const data = ref<any>(null)

onMounted(async () => {
  try {
    const result = await getInterviewPrep(route.params.id as string)
    data.value = result.interview_prep
  } catch (err) {
    console.error(err)
  } finally {
    loading.value = false
  }
})

const getPriorityBadgeClass = (priority: string) => {
  if (priority === 'critical') return 'bg-red-100 text-red-700'
  if (priority === 'high') return 'bg-orange-100 text-orange-700'
  return 'bg-yellow-100 text-yellow-700'
}
</script>
