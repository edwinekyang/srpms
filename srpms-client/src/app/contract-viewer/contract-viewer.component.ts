import { Component, OnInit } from '@angular/core';
import {SupervisorService} from '../supervisor.service';

export interface ContractViewer {
  studentId: string;
  studentName: string;
  supervisor: string;
  courseNumber: string;
  courseName: string;
  courseUnit: string;
  semester: string;
  duration: string;
  year: string;
  title: string;
  objectives: string;
  description: string;
  assessment1: string;
  assessment1Style: string;
  assessment1Mark: string;
  assessment1Due: string;
  assessment1Examiner: string;
  assessment2: string;
  assessment2Style: string;
  assessment2Mark: string;
  assessment2Due: string;
  assessment2Examiner: string;
  assessment3: string;
  assessment3Style: string;
  assessment3Mark: string;
  assessment3Due: string;
  assessment3Examiner: string;
  submit_date: string;
}

export interface AssessmentMethods {
  template: string;
  contract: string;
  due: string;
  max_mark: string;
  examiner: string;
  is_examiner_approved: boolean;
}

@Component({
  selector: 'app-contract-viewer',
  templateUrl: './contract-viewer.component.html',
  styleUrls: ['./contract-viewer.component.scss']
})
export class ContractViewerComponent implements OnInit {

  private contractId: string;
  private contractViewer: ContractViewer;

  constructor(
      private supervisorService: SupervisorService,
  ) { }

  ngOnInit() {

    this.supervisorService.currentMessage
        .subscribe(
        (message: any) => {
          this.contractId = message.id;
          this.contractViewer = {
            studentId: message.studentId,
            studentName: message.studentName,
            supervisor: message.supervisor,
            courseNumber: message.course,
            courseName: message.course,
            courseUnit: message.course,
            semester: message.semester,
            duration: message.duration,
            year: message.year,
            title: message.special_topics ? message.special_topics.title :
                message.individual_project.title,
            objectives: message.special_topics ? message.special_topics.objectives :
                message.individual_project.objectives,
            description: message.special_topics ? message.special_topics.description :
                message.individual_project.description,
            assessment1: message,
            assessment1Style: message,
            assessment1Mark: message,
            assessment1Due: message,
            assessment1Examiner: message,
            assessment2: message,
            assessment2Style: message,
            assessment2Mark: message,
            assessment2Due: message,
            assessment2Examiner: message,
            assessment3: message,
            assessment3Style: message,
            assessment3Mark: message,
            assessment3Due: message,
            assessment3Examiner: message,
            submit_date: message.submit_date,
          };
        }
    );
    // this.contractViewer = this.showContract();
  }

  showAssessmentMethods() {

  }
  //
  // showContract() {
  //   let contractViewer: ContractViewer;
  //   this.contractService.getContract(this.contractId)
  //       .subscribe((contract: any) => {
  //         contractViewer = {
  //
  //         }
  //       }, error => {
  //         if (error instanceof HttpErrorResponse) {
  //           this.errorMessage = error.error.detail;
  //         }
  //       });
  //   return contractViewer;
  //   }

}

