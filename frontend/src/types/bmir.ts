export type VerificationStatus =
  | 'Verified'
  | 'Pending verification'
  | 'Draft'
  | 'Unpublished'
  | 'Archived';

export type DevelopmentStage =
  | 'Concept'
  | 'Research'
  | 'Feasibility'
  | 'Design'
  | 'Prototype'
  | 'Testing'
  | 'Validation'
  | 'Commercialization';

export type PatentType =
  | 'Idea'
  | 'Provisional'
  | 'Complete'
  | 'Published'
  | 'Granted'
  | 'Abandoned';

export type UserRole =
  | 'super_admin'
  | 'founder'
  | 'research_admin'
  | 'research_scientist'
  | 'research_engineer'
  | 'external_collaborator'
  | 'viewer';

export interface Innovation {
  id: string;
  project_code: string;
  title: string;
  title_hi?: string;
  domain: string;
  summary: string;
  summary_hi?: string;
  problem_statement: string;
  problem_statement_hi?: string;
  proposed_solution: string;
  proposed_solution_hi?: string;
  technical_description?: string;
  technical_description_hi?: string;
  development_stage: DevelopmentStage;
  prototype_status: string;
  validation_required?: string;
  validation_required_hi?: string;
  collaboration_sought?: string;
  collaboration_sought_hi?: string;
  patent_application_no?: string;
  patent_status: string;
  co_inventors?: string;
  is_published: boolean;
  is_confidential?: boolean;
  verification_status?: VerificationStatus;
  created_at?: string;
}

export interface PatentRecord {
  id: string;
  title: string;
  application_number: string;
  provisional_application_number?: string;
  filing_date?: string;
  provisional_filing_date?: string;
  publication_date?: string;
  journal_issue?: string;
  journal_page?: string;
  jurisdiction: string;
  lead_inventor: string;
  co_inventors?: string;
  applicants: string;
  patent_type: PatentType;
  legal_status: string;
  verification_notes?: string;
  verification_status?: VerificationStatus;
  claims_summary?: string;
  is_confidential: boolean;
  innovation_code?: string;
  innovation_id?: string;
}

export interface ResearchProject {
  id: string;
  project_code: string;
  title: string;
  domain: string;
  objective: string;
  research_questions?: string;
  methodology: string;
  technical_requirements?: string;
  progress_pct: number;
  status: string;
  verification_status?: VerificationStatus;
  lead_researcher: string;
  team_members?: string;
  expected_outcome?: string;
  created_at?: string;
  experiments?: Experiment[];
}

export interface Experiment {
  id: string;
  project_id?: string;
  project_title?: string;
  project_code?: string;
  creator_name?: string;
  title: string;
  domain: string;
  objective: string;
  hypothesis: string;
  methodology?: string;
  materials_used?: string;
  measurements?: string;
  observations?: string;
  results_summary?: string;
  status: 'Draft' | 'Ongoing' | 'Concluded' | 'Replicated';
  version: number;
  data_metrics?: Record<string, any>;
  created_at?: string;
  updated_at?: string;
}

export interface FeasibilityEvaluation {
  id: string;
  innovation_id?: string;
  title: string;
  overall_score: number;
  scientific_feasibility: number;
  engineering_feasibility: number;
  material_availability: number;
  manufacturing_readiness: number;
  development_complexity: number;
  energy_efficiency: number;
  economic_viability: number;
  environmental_impact: number;
  safety_compliance: number;
  limitations_and_risks?: string;
  prerequisites?: string;
  confidence_level: 'Low' | 'Medium' | 'High';
  created_at?: string;
}

export interface InnovationRoadmap {
  id: string;
  innovation_id?: string;
  title: string;
  phases: Array<{
    phase: string;
    duration: string;
    milestones: string[];
    deliverables: string;
    risks: string;
  }>;
  estimated_timeline_months: number;
  status: string;
  created_at?: string;
}

export interface KnowledgeDocument {
  id: string;
  title: string;
  doc_type: string;
  domain: string;
  abstract?: string;
  content?: string;
  keywords?: string;
  authors?: string;
  source_url?: string;
  doi?: string;
  is_confidential: boolean;
  verification_status?: VerificationStatus;
  similarity_score?: number;
  created_at?: string;
}

export interface CollaborationEnquiry {
  id?: string;
  enquiry_number?: string;
  full_name: string;
  email: string;
  phone?: string;
  organization: string;
  organization_type: string;
  pathway: string;
  project_interest?: string;
  message: string;
  proposal_summary?: string;
  status?: string;
  internal_notes?: string;
  created_at?: string;
}

export interface User {
  id: string;
  email: string;
  full_name: string;
  role: UserRole;
  designation?: string;
  organization?: string;
  bio?: string;
  avatar_url?: string;
  research_interests?: string;
  phone?: string;
  preferences?: {
    theme?: 'dark' | 'light';
    email_notifications?: boolean;
    digest_frequency?: string;
  };
  email_verified: boolean;
  mfa_enabled?: boolean;
  created_at?: string;
}

export interface DashboardMetrics {
  total_innovations: number;
  verified_innovations?: number;
  pending_innovations?: number;
  draft_innovations?: number;
  total_patents: number;
  published_patents: number;
  provisional_patents: number;
  verified_patents?: number;
  total_projects: number;
  active_projects: number;
  verified_projects?: number;
  total_experiments: number;
  concluded_experiments: number;
  total_enquiries: number;
  pending_enquiries: number;
  approved_enquiries: number;
  total_documents: number;
}

