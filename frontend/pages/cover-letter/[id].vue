<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-5xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="flex flex-col items-center gap-4">
          <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600"></div>
          <p class="text-gray-600">{{ generating ? 'Generating personalized cover letter...' : 'Loading...' }}</p>
        </div>
      </div>

      <!-- Content -->
      <div v-else>
        <!-- Header -->
        <div class="mb-8">
          <button
            @click="navigateTo(`/questions/${route.params.id}`)"
            class="text-blue-600 hover:text-blue-700 mb-4 font-medium"
          >
            ← Back
          </button>
          <h1 class="text-4xl font-bold text-gray-900 mb-2">📝 Your Cover Letter</h1>
          <p class="text-gray-600">
            Personalized cover letter tailored to the job requirements
          </p>
        </div>

        <!-- Actions -->
        <div class="flex gap-4 mb-6">
          <button
            @click="copyToClipboard"
            class="px-6 py-3 bg-blue-600 text-white rounded-xl font-semibold
              hover:bg-blue-700 transition-all transform hover:scale-105 shadow-lg flex items-center gap-2"
          >
            <span v-if="copied">✓ Copied!</span>
            <span v-else>📋 Copy to Clipboard</span>
          </button>
          <a
            :href="api.getCoverLetterDownloadURL(route.params.id as string)"
            target="_blank"
            class="px-6 py-3 bg-gradient-to-r from-purple-600 to-pink-600 text-white rounded-xl
              font-semibold hover:from-purple-700 hover:to-pink-700
              transition-all transform hover:scale-105 shadow-lg flex items-center gap-2"
          >
            📥 Download PDF
          </a>
        </div>

        <!-- Cover Letter Display -->
        <div class="bg-white rounded-3xl shadow-xl p-12 mb-8">
          <!-- Header Info -->
          <div class="mb-8">
            <h2 class="text-2xl font-bold text-gray-900 mb-2">
              {{ coverLetter?.personal_info?.name }}
            </h2>
            <p class="text-gray-600">{{ coverLetter?.personal_info?.email }}</p>
            <p class="text-gray-600">{{ coverLetter?.personal_info?.phone }}</p>
            <p class="text-gray-600">{{ coverLetter?.personal_info?.location }}</p>
          </div>

          <!-- Date -->
          <p class="text-gray-700 mb-6">{{ coverLetter?.date }}</p>

          <!-- Company Info -->
          <div class="mb-6">
            <p class="text-gray-700">{{ coverLetter?.company_info?.hiring_team }}</p>
            <p class="text-gray-700">{{ coverLetter?.company_info?.company_name }}</p>
            <p class="text-gray-700">{{ coverLetter?.company_info?.company_location }}</p>
          </div>

          <!-- RE: Position -->
          <p class="font-semibold text-gray-900 mb-6">
            RE: {{ coverLetter?.position_title }}
          </p>

          <!-- Full Text -->
          <div class="prose max-w-none">
            <div v-html="formatCoverLetterText(coverLetter?.full_text || '')"></div>
          </div>
        </div>

        <!-- Next Steps -->
        <div class="bg-gradient-to-r from-blue-50 to-indigo-50 rounded-3xl shadow-lg p-8">
          <h3 class="text-2xl font-bold text-gray-900 mb-4">🚀 Next Steps</h3>
          <div class="grid md:grid-cols-2 gap-4">
            <button
              @click="navigateTo(`/learning/${route.params.id}`)"
              class="p-6 bg-white rounded-2xl shadow-md hover:shadow-xl transition-all
                transform hover:scale-105 text-left"
            >
              <div class="text-3xl mb-2">📚</div>
              <h4 class="font-semibold text-gray-900 mb-2">Learning Roadmap</h4>
              <p class="text-sm text-gray-600">Get personalized learning recommendations to close skill gaps</p>
            </button>

            <button
              @click="navigateTo(`/interview/${route.params.id}`)"
              class="p-6 bg-white rounded-2xl shadow-md hover:shadow-xl transition-all
                transform hover:scale-105 text-left"
            >
              <div class="text-3xl mb-2">💼</div>
              <h4 class="font-semibold text-gray-900 mb-2">Interview Preparation</h4>
              <p class="text-sm text-gray-600">Prepare for interviews with tailored questions and answers</p>
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
const copied = ref(false)
const coverLetter = ref<any>(null)

onMounted(async () => {
  try {
    // Try to get existing cover letter
    try {
      const data = await api.getCoverLetter(route.params.id as string)
      coverLetter.value = data.cover_letter
      loading.value = false
    } catch (err: any) {
      // Cover letter doesn't exist, generate it
      if (err?.statusCode === 404 || err?.response?.status === 404) {
        generating.value = true
        const data = await api.generateCoverLetter(route.params.id as string)
        coverLetter.value = data.cover_letter
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

const formatCoverLetterText = (text: string) => {
  if (!text) return ''

  // Split by paragraphs and wrap in p tags
  return text
    .split('\n\n')
    .filter(p => p.trim())
    .map(p => `<p class="mb-4 text-gray-700 leading-relaxed">${p.trim()}</p>`)
    .join('')
}

const copyToClipboard = async () => {
  const text = coverLetter.value?.full_text || ''

  try {
    await navigator.clipboard.writeText(text)
    copied.value = true
    setTimeout(() => {
      copied.value = false
    }, 2000)
  } catch (err) {
    console.error('Failed to copy:', err)
  }
}
</script>
