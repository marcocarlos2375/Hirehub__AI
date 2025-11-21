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

    const response = await $fetch<UploadCVResponse>(`${apiBase}/api/upload-cv`, {
      method: 'POST',
      body: formData
    })

    return response
  }

  const getAnalysis = async (id: string): Promise<AnalysisResponse> => {
    return await $fetch<AnalysisResponse>(`${apiBase}/api/analysis/${id}`)
  }

  const submitAnswers = async (id: string, answers: Record<number, string>): Promise<SubmitAnswersResponse> => {
    return await $fetch<SubmitAnswersResponse>(`${apiBase}/api/submit-answers/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(answers)
    })
  }

  const getDownloadURL = (id: string): string => {
    return `${apiBase}/api/download-cv/${id}`
  }

  // Phase 7: Cover Letter
  const generateCoverLetter = async (id: string): Promise<CoverLetterResponse> => {
    return await $fetch<CoverLetterResponse>(`${apiBase}/api/generate-cover-letter/${id}`, {
      method: 'POST'
    })
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
