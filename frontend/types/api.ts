// Type definitions for HireHub AI API

export type Priority = 'critical' | 'high' | 'medium' | 'low'

export interface Gap {
  gap: string
  priority: Priority
  impact: string
}

export interface Question {
  question: string
  category: string
  priority: Priority
  potential_impact: string
  why_asking: string
  suggested_answers?: string[]
}

export interface BreakdownItem {
  score: number
  weight: number
  matched?: string[]
  missing?: string[]
  assessment?: string
  candidate_years?: number
  required_years?: number
}

export interface AnalysisData {
  id: string
  score: number
  breakdown?: Record<string, BreakdownItem>
  strengths?: string[]
  gaps?: Gap[]
  questions?: Question[]
  answers?: Record<number, string>
  optimized_cv?: any
  cv_parsed?: any
  jd_parsed?: any
  cover_letter?: CoverLetterData
  learning_recommendations?: LearningRecommendationsData
  interview_prep?: InterviewPrepData
}

export interface InterviewQuestion {
  question: string
  category: string
  priority: Priority
  suggested_answer: string
  tips?: string[]
  why_they_ask: string
}

export interface InterviewStage {
  stage_name: string
  duration: string
  interviewer: string
  focus: string
  questions: InterviewQuestion[]
}

export interface TechnicalDeepDive {
  topic: string
  likely_questions: string[]
  preparation_tips: string[]
  example_projects_to_mention?: string[]
}

export interface StarMethodExample {
  situation: string
  task: string
  action: string
  result: string
  applicable_to?: string[]
}

export interface RedFlag {
  concern: string
  how_to_address: string
  example_response: string
}

export interface QuestionToAsk {
  question: string
  category: string
  why_ask: string
}

export interface InterviewPrepData {
  stages?: InterviewStage[]
  technical_deep_dives?: TechnicalDeepDive[]
  star_method_examples?: StarMethodExample[]
  red_flags_to_address?: RedFlag[]
  questions_to_ask_them?: QuestionToAsk[]
  general_tips?: string[]
}

export interface QuickWin {
  action: string
  impact: string
  description: string
  time: string
}

export interface PriorityCourse {
  title: string
  priority: Priority
  platform: string
  duration: string
  cost: string
  impact: string
  why_recommended: string
  skills_covered: string[]
  url?: string
}

export interface RoadmapWeek {
  week: number
  focus: string
  hours_per_week: string | number
  tasks: string[]
  milestone: string
}

export interface TotalInvestment {
  time_hours: number
  cost_usd: number
  expected_score_improvement: string
}

export interface LearningRecommendationsData {
  current_score: number
  target_score: number
  estimated_weeks: number
  quick_wins?: QuickWin[]
  priority_courses?: PriorityCourse[]
  roadmap?: RoadmapWeek[]
  total_investment?: TotalInvestment
  recommendations?: string[]
}

export interface CoverLetterSignature {
  name: string
  email: string
  phone: string
  location: string
}

export interface CoverLetterData {
  opening_paragraph: string
  body_paragraph_1: string
  body_paragraph_2: string
  body_paragraph_3?: string
  closing_paragraph: string
  signature: CoverLetterSignature
}

// API Response types
export interface UploadCVResponse {
  id: string
  score: number
  breakdown?: Record<string, BreakdownItem>
  gaps?: Gap[]
  strengths?: string[]
  questions?: Question[]
}

export interface AnalysisResponse extends AnalysisData {}

export interface SubmitAnswersResponse {
  id: string
  message: string
  optimized_cv: any
}

export interface CoverLetterResponse {
  id: string
  message: string
  cover_letter: CoverLetterData
}

export interface LearningRecommendationsResponse {
  id: string
  learning_recommendations: LearningRecommendationsData
}

export interface InterviewPrepResponse {
  id: string
  interview_prep: InterviewPrepData
}
