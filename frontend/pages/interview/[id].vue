<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-6xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="flex flex-col items-center gap-4">
          <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
          <p class="text-gray-600">{{ generating ? 'Preparing interview materials...' : 'Loading...' }}</p>
        </div>
      </div>

      <!-- Content -->
      <div v-else>
        <!-- Header -->
        <div class="mb-8">
          <button
            @click="navigateTo(`/learning/${route.params.id}`)"
            class="text-blue-600 hover:text-blue-700 mb-4 font-medium"
          >
            ← Back
          </button>
          <h1 class="text-4xl font-bold text-gray-900 mb-2">💼 Interview Preparation</h1>
          <p class="text-gray-600">
            Tailored questions, answers, and strategies to ace your interviews
          </p>
        </div>

        <!-- Company Research -->
        <div class="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-3xl shadow-xl p-8 mb-8 text-white">
          <h2 class="text-2xl font-bold mb-4">🏢 Company Research</h2>
          <div class="grid md:grid-cols-2 gap-6">
            <div>
              <h3 class="font-semibold mb-2 opacity-90">Key Facts</h3>
              <ul class="space-y-2">
                <li v-for="(fact, idx) in interviewPrep?.company_research?.key_facts" :key="idx" class="text-sm">
                  • {{ fact }}
                </li>
              </ul>
            </div>
            <div>
              <h3 class="font-semibold mb-2 opacity-90">Company Values</h3>
              <div class="flex flex-wrap gap-2">
                <span
                  v-for="(value, idx) in interviewPrep?.company_research?.values"
                  :key="idx"
                  class="px-3 py-1 bg-white/20 rounded-full text-sm"
                >
                  {{ value }}
                </span>
              </div>
            </div>
          </div>
          <div class="mt-4">
            <h3 class="font-semibold mb-2">Technical Stack</h3>
            <div class="flex flex-wrap gap-2">
              <span
                v-for="(tech, idx) in interviewPrep?.company_research?.technical_stack"
                :key="idx"
                class="px-3 py-1 bg-white/20 rounded-full text-sm font-mono"
              >
                {{ tech }}
              </span>
            </div>
          </div>
        </div>

        <!-- Interview Stages -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">📋 Interview Stages</h2>
          <div class="space-y-6">
            <div
              v-for="(stage, sidx) in interviewPrep?.interview_stages"
              :key="sidx"
              class="bg-white rounded-3xl shadow-lg p-8"
            >
              <!-- Stage Header -->
              <div class="flex justify-between items-start mb-6 pb-4 border-b-2 border-gray-100">
                <div>
                  <div class="text-sm text-blue-600 font-semibold mb-1">STAGE {{ stage.stage }}</div>
                  <h3 class="text-2xl font-bold text-gray-900">{{ stage.name }}</h3>
                  <p class="text-gray-600 mt-1">{{ stage.duration }} • {{ stage.interviewer }}</p>
                </div>
              </div>

              <!-- Focus -->
              <div class="bg-blue-50 rounded-xl p-4 mb-6">
                <div class="font-semibold text-gray-900 mb-1">Focus Areas:</div>
                <p class="text-gray-700">{{ stage.focus }}</p>
              </div>

              <!-- Questions -->
              <div class="space-y-6">
                <div
                  v-for="(q, qidx) in stage.questions"
                  :key="qidx"
                  class="border-l-4 pl-6 py-2"
                  :class="{
                    'border-red-500 bg-red-50': q.priority === 'critical',
                    'border-orange-500 bg-orange-50': q.priority === 'high',
                    'border-yellow-500 bg-yellow-50': q.priority === 'medium'
                  }"
                >
                  <!-- Question Header -->
                  <div class="flex justify-between items-start mb-3">
                    <h4 class="text-lg font-semibold text-gray-900 flex-1">
                      {{ q.question }}
                    </h4>
                    <span
                      class="ml-4 px-3 py-1 rounded-full text-xs font-semibold"
                      :class="{
                        'bg-red-100 text-red-700': q.priority === 'critical',
                        'bg-orange-100 text-orange-700': q.priority === 'high',
                        'bg-yellow-100 text-yellow-700': q.priority === 'medium'
                      }"
                    >
                      {{ q.priority.toUpperCase() }}
                    </span>
                  </div>

                  <!-- Category and Why -->
                  <div class="text-sm text-gray-600 mb-3">
                    <span class="font-medium">Category:</span> {{ q.category }} •
                    <span class="font-medium">Why:</span> {{ q.why_important }}
                  </div>

                  <!-- Answer Framework -->
                  <div class="mb-3">
                    <div class="font-semibold text-gray-900 mb-2 text-sm">📝 Answer Framework:</div>
                    <ul class="space-y-1">
                      <li v-for="(point, pidx) in q.answer_framework" :key="pidx" class="text-sm text-gray-700">
                        • {{ point }}
                      </li>
                    </ul>
                  </div>

                  <!-- Sample Answer -->
                  <div class="bg-white rounded-xl p-4 mb-3">
                    <div class="font-semibold text-gray-900 mb-2 text-sm">💡 Sample Answer:</div>
                    <p class="text-gray-700 text-sm leading-relaxed whitespace-pre-line">{{ q.sample_answer }}</p>
                  </div>

                  <!-- Follow-up Questions -->
                  <div v-if="q.follow_up_questions?.length" class="mt-3">
                    <div class="font-semibold text-gray-900 mb-2 text-sm">🔄 Possible Follow-ups:</div>
                    <ul class="space-y-1">
                      <li v-for="(followup, fidx) in q.follow_up_questions" :key="fidx" class="text-sm text-gray-600 italic">
                        → {{ followup }}
                      </li>
                    </ul>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Project Talking Points -->
        <div v-if="interviewPrep?.project_talking_points?.length" class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">🚀 Project Talking Points</h2>
          <div class="grid md:grid-cols-2 gap-6">
            <div
              v-for="(project, pidx) in interviewPrep.project_talking_points"
              :key="pidx"
              class="bg-purple-50 border border-purple-200 rounded-2xl p-6"
            >
              <h3 class="font-bold text-gray-900 mb-3">{{ project.project }}</h3>
              <div class="space-y-3">
                <div>
                  <div class="text-sm font-semibold text-gray-700 mb-1">Key Points:</div>
                  <ul class="space-y-1">
                    <li v-for="(point, idx) in project.key_points" :key="idx" class="text-sm text-gray-700">
                      • {{ point }}
                    </li>
                  </ul>
                </div>
                <div>
                  <div class="text-sm font-semibold text-gray-700 mb-1">Business Impact:</div>
                  <p class="text-sm text-gray-700">{{ project.business_impact }}</p>
                </div>
                <div>
                  <div class="text-sm font-semibold text-gray-700 mb-1">Challenges Overcome:</div>
                  <ul class="space-y-1">
                    <li v-for="(challenge, cidx) in project.challenges_overcome" :key="cidx" class="text-sm text-gray-700">
                      • {{ challenge }}
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Gap Mitigation -->
        <div v-if="interviewPrep?.gap_mitigation_strategies?.length" class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">🎯 Addressing Gaps</h2>
          <div class="bg-yellow-50 border border-yellow-200 rounded-2xl p-6">
            <div class="space-y-4">
              <div
                v-for="(gap, gidx) in interviewPrep.gap_mitigation_strategies"
                :key="gidx"
                class="border-b border-yellow-200 last:border-0 pb-4 last:pb-0"
              >
                <div class="font-semibold text-gray-900 mb-2">{{ gap.gap }}</div>
                <div class="text-sm text-gray-700 mb-2">
                  <span class="font-medium">Strategy:</span> {{ gap.how_to_address }}
                </div>
                <div class="text-sm text-green-700 bg-green-50 p-3 rounded-lg">
                  <span class="font-medium">Positive Framing:</span> "{{ gap.positive_framing }}"
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Questions to Ask -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">❓ Smart Questions to Ask</h2>
          <div class="bg-white rounded-3xl shadow-lg p-8">
            <div class="space-y-4">
              <div
                v-for="(q, qidx) in interviewPrep?.questions_to_ask"
                :key="qidx"
                class="border-l-4 border-blue-500 pl-6 py-3 hover:bg-blue-50 transition-all rounded-r-xl"
              >
                <div class="font-semibold text-gray-900 mb-2">{{ q.question }}</div>
                <div class="text-sm text-gray-600 mb-1">
                  <span class="font-medium">When:</span> {{ q.when_to_ask }}
                </div>
                <div class="text-sm text-gray-600">
                  <span class="font-medium">Why:</span> {{ q.why_ask }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Common Mistakes -->
        <div class="mb-8">
          <h2 class="text-2xl font-bold text-gray-900 mb-4">⚠️ Common Mistakes to Avoid</h2>
          <div class="bg-red-50 border border-red-200 rounded-2xl p-6">
            <div class="space-y-4">
              <div
                v-for="(mistake, midx) in interviewPrep?.common_mistakes"
                :key="midx"
                class="border-b border-red-200 last:border-0 pb-4 last:pb-0"
              >
                <div class="font-semibold text-red-700 mb-2">❌ {{ mistake.mistake }}</div>
                <div class="text-sm text-gray-700 mb-2">
                  <span class="font-medium">Why it's bad:</span> {{ mistake.why_bad }}
                </div>
                <div class="text-sm text-green-700 bg-white p-3 rounded-lg">
                  <span class="font-medium">✓ Do this instead:</span> {{ mistake.instead_do }}
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Final CTA -->
        <div class="bg-gradient-to-r from-green-50 to-emerald-50 rounded-3xl shadow-lg p-8 text-center">
          <h3 class="text-2xl font-bold text-gray-900 mb-4">🎉 You're Ready!</h3>
          <p class="text-gray-600 mb-6">
            You now have everything you need: optimized CV, personalized cover letter, learning roadmap, and interview prep.
          </p>
          <div class="flex gap-4 justify-center">
            <button
              @click="window.print()"
              class="px-6 py-3 bg-gray-600 text-white rounded-xl font-semibold
                hover:bg-gray-700 transition-all"
            >
              🖨️ Print This Page
            </button>
            <button
              @click="navigateTo(`/analysis/${route.params.id}`)"
              class="px-6 py-3 bg-gradient-to-r from-blue-600 to-indigo-600 text-white rounded-xl
                font-semibold hover:from-blue-700 hover:to-indigo-700 transition-all"
            >
              📊 Back to Analysis
            </button>
          </div>
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
const interviewPrep = ref<any>(null)

onMounted(async () => {
  try {
    // Try to get existing interview prep
    try {
      const data = await api.getInterviewPrep(route.params.id as string)
      interviewPrep.value = data.interview_prep
      loading.value = false
    } catch (err: any) {
      // Interview prep doesn't exist, generate it
      if (err?.statusCode === 404 || err?.response?.status === 404) {
        generating.value = true
        const data = await api.generateInterviewPrep(route.params.id as string)
        interviewPrep.value = data.interview_prep
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
