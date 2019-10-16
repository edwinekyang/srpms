/**
 * This file contains data structures return from the API server.
 *
 * @author Dajie Yang (u6513788) <dajie.yang@anu.edu.au>
 */

export interface Course {
  id: number;
  course_number: string;
  name: string;
  units: number;
}

export interface AssessmentTemplate {
  id: number;
  name: string;
  description: string;
  max_weight: number;
  min_weight: number;
  default_weight: number;
}

export interface Supervise {
  id: number;
  contract: number;
  supervisor: number;
  is_formal: boolean;
  nominator: number;
  is_supervisor_approved: boolean;
  supervisor_approval_date?: string;
}

export interface AssessmentExamine {
  id: number;
  examiner: number;
  nominator: number;
  examiner_approval_date: string;
}

export interface Assessment {
  id: number;
  template: number;
  template_info: AssessmentTemplate;
  contract: number;
  additional_description: string;
  due: string;
  weight: number;
  assessment_examine: AssessmentExamine[];
  is_all_examiners_approved: boolean;
}

export interface IndividualProject {
  title: string;
  objectives: string;
  description: string;
}

export interface SpecialTopic {
  title: string;
  objectives: string;
  description: string;
}

export interface Contract {
  id: number;
  year: number;
  semester: number;
  duration: number;
  resources: number;
  course: number;
  convener: number;
  is_convener_approved: boolean;
  convener_approval_date: string;
  owner: number;
  create_date: string;
  submit_date: string;
  is_submitted: boolean;
  was_submitted: boolean;
  individual_project?: IndividualProject;
  special_topic?: SpecialTopic;
  supervise: Supervise[];
  is_all_supervisors_approved: boolean;
  assessment: Assessment[];
  is_all_assessments_approved: boolean;
  is_examiner_nominated: boolean;
}
