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

  // Cover Letter methods
  const generateCoverLetter = async (id: string) => {
    return await $fetch(`${apiBase}/api/generate-cover-letter/${id}`, {
      method: 'POST'
    })
  }

  const getCoverLetter = async (id: string) => {
    return await $fetch(`${apiBase}/api/cover-letter/${id}`)
  }

  const getCoverLetterDownloadURL = (id: string) => {
    return `${apiBase}/api/download-cover-letter/${id}`
  }

  // Learning Path methods
  const generateLearningPath = async (id: string) => {
    return await $fetch(`${apiBase}/api/generate-learning-path/${id}`, {
      method: 'POST'
    })
  }

  const getLearningPath = async (id: string) => {
    return await $fetch(`${apiBase}/api/learning-path/${id}`)
  }

  // Interview Prep methods
  const generateInterviewPrep = async (id: string) => {
    return await $fetch(`${apiBase}/api/generate-interview-prep/${id}`, {
      method: 'POST'
    })
  }

  const getInterviewPrep = async (id: string) => {
    return await $fetch(`${apiBase}/api/interview-prep/${id}`)
  }

  return {
    uploadCV,
    getAnalysis,
    submitAnswers,
    getDownloadURL,
    generateCoverLetter,
    getCoverLetter,
    getCoverLetterDownloadURL,
    generateLearningPath,
    getLearningPath,
    generateInterviewPrep,
    getInterviewPrep
  }
}
