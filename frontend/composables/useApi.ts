import type {
  UploadCVResponse,
  AnalysisResponse,
  SubmitAnswersResponse,
  CoverLetterResponse,
  LearningRecommendationsResponse,
  InterviewPrepResponse
} from '~/types/api'

export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const uploadCV = async (file: File, jdText: string): Promise<UploadCVResponse> => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('jd_text', jdText)

    // Extended timeout for AI processing (2 minutes)
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 120000) // 120 seconds

    console.log('🚀 Starting CV upload with 120s timeout...')
    const startTime = Date.now()

    try {
      const response = await $fetch<UploadCVResponse>(`${apiBase}/api/upload-cv`, {
        method: 'POST',
        body: formData,
        signal: controller.signal
      })
      clearTimeout(timeoutId)
      const duration = ((Date.now() - startTime) / 1000).toFixed(2)
      console.log(`✅ CV upload completed in ${duration}s`)
      return response
    } catch (error) {
      clearTimeout(timeoutId)
      const duration = ((Date.now() - startTime) / 1000).toFixed(2)
      console.error(`❌ CV upload failed after ${duration}s:`, error)
      throw error
    }
  }

  const getAnalysis = async (id: string): Promise<AnalysisResponse> => {
    return await $fetch<AnalysisResponse>(`${apiBase}/api/analysis/${id}`)
  }

  const submitAnswers = async (id: string, answers: Record<number, string>): Promise<SubmitAnswersResponse> => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 90000) // 90 seconds for CV optimization

    try {
      const response = await $fetch<SubmitAnswersResponse>(`${apiBase}/api/submit-answers/${id}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(answers),
        signal: controller.signal
      })
      clearTimeout(timeoutId)
      return response
    } catch (error) {
      clearTimeout(timeoutId)
      throw error
    }
  }

  const getDownloadURL = (id: string): string => {
    return `${apiBase}/api/download-cv/${id}`
  }

  // Phase 7: Cover Letter
  const generateCoverLetter = async (id: string): Promise<CoverLetterResponse> => {
    const controller = new AbortController()
    const timeoutId = setTimeout(() => controller.abort(), 60000) // 60 seconds for cover letter generation

    try {
      const response = await $fetch<CoverLetterResponse>(`${apiBase}/api/generate-cover-letter/${id}`, {
        method: 'POST',
        signal: controller.signal
      })
      clearTimeout(timeoutId)
      return response
    } catch (error) {
      clearTimeout(timeoutId)
      throw error
    }
  }

  const getCoverLetter = async (id: string): Promise<CoverLetterResponse> => {
    const analysis = await getAnalysis(id)
    return {
      id: analysis.id,
      message: 'Cover letter retrieved',
      cover_letter: analysis.cover_letter
    }
  }

  const getCoverLetterDownloadURL = (id: string): string => {
    return `${apiBase}/api/download-cover-letter/${id}`
  }

  // Phase 8: Learning Recommendations
  const getLearningRecommendations = async (id: string): Promise<LearningRecommendationsResponse> => {
    return await $fetch<LearningRecommendationsResponse>(`${apiBase}/api/learning-recommendations/${id}`)
  }

  // Phase 9: Interview Prep
  const getInterviewPrep = async (id: string): Promise<InterviewPrepResponse> => {
    return await $fetch<InterviewPrepResponse>(`${apiBase}/api/interview-prep/${id}`)
  }

  return {
    uploadCV,
    getAnalysis,
    submitAnswers,
    getDownloadURL,
    generateCoverLetter,
    getCoverLetter,
    getCoverLetterDownloadURL,
    getLearningRecommendations,
    getInterviewPrep
  }
}
