export const useApi = () => {
  const config = useRuntimeConfig()
  const apiBase = config.public.apiBase

  const uploadCV = async (file: File, jdText: string) => {
    const formData = new FormData()
    formData.append('file', file)
    formData.append('jd_text', jdText)

    const response = await $fetch(`${apiBase}/api/upload-cv`, {
      method: 'POST',
      body: formData
    })

    return response
  }

  const getAnalysis = async (id: string) => {
    return await $fetch(`${apiBase}/api/analysis/${id}`)
  }

  const submitAnswers = async (id: string, answers: Record<number, string>) => {
    return await $fetch(`${apiBase}/api/submit-answers/${id}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(answers)
    })
  }

  const getDownloadURL = (id: string) => {
    return `${apiBase}/api/download-cv/${id}`
  }

  // Phase 7: Cover Letter
  const generateCoverLetter = async (id: string) => {
    return await $fetch(`${apiBase}/api/generate-cover-letter/${id}`, {
      method: 'POST'
    })
  }

  const getCoverLetterDownloadURL = (id: string) => {
    return `${apiBase}/api/download-cover-letter/${id}`
  }

  // Phase 8: Learning Recommendations
  const getLearningRecommendations = async (id: string) => {
    return await $fetch(`${apiBase}/api/learning-recommendations/${id}`)
  }

  // Phase 9: Interview Prep
  const getInterviewPrep = async (id: string) => {
    return await $fetch(`${apiBase}/api/interview-prep/${id}`)
  }

  return {
    uploadCV,
    getAnalysis,
    submitAnswers,
    getDownloadURL,
    generateCoverLetter,
    getCoverLetterDownloadURL,
    getLearningRecommendations,
    getInterviewPrep
  }
}
