<template>
  <div class="min-h-screen bg-gray-50 py-8 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Loading -->
      <div v-if="loading" class="flex items-center justify-center min-h-[60vh]">
        <div class="text-center">
          <div class="animate-spin rounded-full h-16 w-16 border-b-4 border-blue-600 mx-auto"></div>
          <p class="mt-4 text-gray-600">Loading your cover letter...</p>
        </div>
      </div>

      <!-- Error -->
      <div v-else-if="error" class="bg-red-50 border border-red-200 rounded-2xl p-6">
        <h2 class="text-xl font-bold text-red-800 mb-2">Error Loading Cover Letter</h2>
        <p class="text-red-700 mb-4">{{ error }}</p>
        <button
          @click="navigateTo(`/analysis/${route.params.id}`)"
          class="text-blue-600 hover:text-blue-700 font-medium"
        >
          ← Back to Analysis
        </button>
      </div>

      <!-- Content -->
      <div v-else-if="coverLetter">
        <!-- Header -->
        <div class="mb-8">
          <button
            @click="navigateTo(`/analysis/${route.params.id}`)"
            class="text-blue-600 hover:text-blue-700 mb-4 font-medium"
          >
            ← Back to Analysis
          </button>
          <div class="flex justify-between items-start">
            <div>
              <h1 class="text-4xl font-bold text-gray-900 mb-2">Cover Letter</h1>
              <p class="text-gray-600">
                Tailored specifically for this job opportunity
              </p>
            </div>
            <a
              :href="getCoverLetterDownloadURL(route.params.id as string)"
              target="_blank"
              class="bg-blue-600 text-white px-6 py-3 rounded-xl font-semibold
                hover:bg-blue-700 transition-colors shadow-lg"
            >
              📄 Download PDF
            </a>
          </div>
        </div>

        <!-- Cover Letter Document -->
        <div class="bg-white rounded-3xl shadow-xl p-12 mb-6" style="font-family: 'Georgia', serif;">
          <!-- Date -->
          <div class="text-right text-gray-600 mb-8">
            {{ currentDate }}
          </div>

          <!-- Recipient Address (placeholder) -->
          <div class="mb-8 text-gray-700">
            <p>Hiring Manager</p>
            <p>Company Name</p>
            <p>Address</p>
          </div>

          <!-- Salutation -->
          <div class="mb-6">
            <p class="text-gray-900">Dear Hiring Manager,</p>
          </div>

          <!-- Opening Paragraph -->
          <div class="mb-6 text-gray-800 leading-relaxed text-justify">
            <p>{{ coverLetter.opening_paragraph }}</p>
          </div>

          <!-- Body Paragraph 1 -->
          <div class="mb-6 text-gray-800 leading-relaxed text-justify">
            <p>{{ coverLetter.body_paragraph_1 }}</p>
          </div>

          <!-- Body Paragraph 2 -->
          <div class="mb-6 text-gray-800 leading-relaxed text-justify">
            <p>{{ coverLetter.body_paragraph_2 }}</p>
          </div>

          <!-- Body Paragraph 3 (optional) -->
          <div v-if="coverLetter.body_paragraph_3" class="mb-6 text-gray-800 leading-relaxed text-justify">
            <p>{{ coverLetter.body_paragraph_3 }}</p>
          </div>

          <!-- Closing Paragraph -->
          <div class="mb-6 text-gray-800 leading-relaxed text-justify">
            <p>{{ coverLetter.closing_paragraph }}</p>
          </div>

          <!-- Closing Salutation -->
          <div class="mb-8 text-gray-900">
            <p>Sincerely,</p>
          </div>

          <!-- Signature -->
          <div class="text-gray-900">
            <p class="font-semibold text-lg">{{ coverLetter.signature.name }}</p>
            <p class="text-gray-700">{{ coverLetter.signature.email }}</p>
            <p class="text-gray-700">{{ coverLetter.signature.phone }}</p>
            <p class="text-gray-700">{{ coverLetter.signature.location }}</p>
          </div>
        </div>

        <!-- Tips Card -->
        <div class="bg-blue-50 border border-blue-200 rounded-2xl p-6">
          <h3 class="text-lg font-semibold text-blue-900 mb-3">💡 Cover Letter Tips</h3>
          <ul class="space-y-2 text-blue-800 text-sm">
            <li>✓ Customize the recipient's name and company address before sending</li>
            <li>✓ Review and personalize any generic phrases to match your voice</li>
            <li>✓ Keep the letter to one page when printed</li>
            <li>✓ Proofread carefully for any errors or typos</li>
            <li>✓ Save as PDF before submitting to preserve formatting</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { CoverLetterData } from '~/types/api'

const route = useRoute()
const { getCoverLetter, getCoverLetterDownloadURL } = useApi()

const loading = ref(true)
const error = ref('')
const coverLetter = ref<CoverLetterData | null>(null)

const currentDate = computed(() => {
  const date = new Date()
  return date.toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  })
})

onMounted(async () => {
  try {
    const response = await getCoverLetter(route.params.id as string)

    if (!response.cover_letter) {
      error.value = 'Cover letter not generated yet. Please generate it from the analysis page first.'
      return
    }

    coverLetter.value = response.cover_letter
  } catch (err) {
    console.error('Error loading cover letter:', err)
    error.value = 'Failed to load cover letter. Please try again.'
  } finally {
    loading.value = false
  }
})
</script>
