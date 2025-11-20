<template>
  <div class="min-h-screen bg-gradient-to-br from-blue-50 via-white to-indigo-50 py-12 px-4">
    <div class="max-w-4xl mx-auto">
      <!-- Header -->
      <div class="text-center mb-12">
        <h1 class="text-6xl font-bold text-gray-900 mb-4 tracking-tight">
          HireHub<span class="text-blue-600">AI</span>
        </h1>
        <p class="text-xl text-gray-600 font-light">
          Optimize your CV for any job in minutes with AI
        </p>
      </div>

      <!-- Main Form Card -->
      <div class="bg-white rounded-3xl shadow-xl p-8 backdrop-blur-sm">
        <form @submit.prevent="handleSubmit" class="space-y-6">
          <!-- CV Upload -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              📄 Upload Your CV/Resume
            </label>
            <input
              type="file"
              accept=".pdf,.docx"
              @change="handleFileChange"
              class="block w-full text-sm text-gray-600
                file:mr-4 file:py-3 file:px-6
                file:rounded-xl file:border-0
                file:text-sm file:font-semibold
                file:bg-blue-50 file:text-blue-700
                hover:file:bg-blue-100
                file:transition-colors
                cursor-pointer"
            />
            <p class="mt-2 text-sm text-gray-500">
              PDF or DOCX format only
            </p>
          </div>

          <!-- JD Input -->
          <div>
            <label class="block text-sm font-semibold text-gray-700 mb-3">
              📋 Paste Job Description
            </label>
            <textarea
              v-model="jdText"
              rows="14"
              class="w-full px-4 py-3 border border-gray-200 rounded-xl
                focus:ring-2 focus:ring-blue-500 focus:border-transparent
                resize-none transition-all"
              placeholder="Paste the complete job description here..."
            />
          </div>

          <!-- Error Message -->
          <div v-if="error" class="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-xl">
            {{ error }}
          </div>

          <!-- Submit Button -->
          <button
            type="submit"
            :disabled="loading"
            class="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 px-6 rounded-xl
              font-semibold text-lg shadow-lg
              hover:from-blue-700 hover:to-indigo-700
              disabled:from-gray-400 disabled:to-gray-500 disabled:cursor-not-allowed
              transition-all duration-200 transform hover:scale-[1.02]"
          >
            <span v-if="loading" class="flex items-center justify-center">
              <svg class="animate-spin h-5 w-5 mr-3" viewBox="0 0 24 24">
                <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" fill="none"/>
                <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
              </svg>
              Analyzing with AI...
            </span>
            <span v-else>🚀 Analyze & Optimize</span>
          </button>
        </form>
      </div>

      <!-- Features -->
      <div class="mt-10 text-center">
        <div class="flex flex-wrap justify-center gap-6 text-sm text-gray-600">
          <div class="flex items-center gap-2">
            <span class="text-green-500">✓</span>
            <span>No signup required</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-green-500">✓</span>
            <span>Powered by Gemini 2.0</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-green-500">✓</span>
            <span>Vector DB intelligence</span>
          </div>
          <div class="flex items-center gap-2">
            <span class="text-green-500">✓</span>
            <span>Results in seconds</span>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
const router = useRouter()
const { uploadCV } = useApi()

const file = ref<File | null>(null)
const jdText = ref('')
const loading = ref(false)
const error = ref('')

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files[0]) {
    file.value = target.files[0]
  }
}

const handleSubmit = async () => {
  if (!file.value || !jdText.value) {
    error.value = 'Please upload a CV and paste a job description'
    return
  }

  loading.value = true
  error.value = ''

  try {
    const result = await uploadCV(file.value, jdText.value)
    await navigateTo(`/analysis/${result.id}`)
  } catch (err: any) {
    error.value = err.message || 'Something went wrong. Please try again.'
    console.error(err)
  } finally {
    loading.value = false
  }
}
</script>
