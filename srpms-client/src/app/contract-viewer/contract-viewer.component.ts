import {Component, OnInit} from '@angular/core';
import {ContractMgtService} from '../contract-mgt.service';
import {ElementService} from '../element.service';
import {ElementBase} from '../element-base';
import {FormGroup} from '@angular/forms';
import {ContractFormControlService} from '../contract-form-control.service';
import {Observable} from 'rxjs';
import {ActivatedRoute} from '@angular/router';
import {map} from 'rxjs/operators';

export interface ContractViewer {
  projectSupervisor: string;
  semester: string;
  duration: string;
  year: string;
  title: string;
  objectives: string;
  description: string;
  assessment: any;
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
  styleUrls: ['./contract-viewer.component.scss'],
  providers: [
    ElementService,
    ContractMgtService,
    ContractFormControlService,
  ]
})
export class ContractViewerComponent implements OnInit {
  private state$: Observable<object>;
  private message: any;
  public contractViewer: any = {};
  elements: ElementBase<any>[] = [];
  form: FormGroup;
  sectionList = [];
  filteredElements: ElementBase<any>[] = [];
  private errorMessage: string;
  private readonly formFlag: any;
  public isContractChanged: boolean;

  constructor(
      private supervisorService: ContractMgtService,
      public elementService: ElementService,
      private cfcs: ContractFormControlService,
      public activatedRoute: ActivatedRoute,
  ) {
    this.isContractChanged = false;
    this.elements = this.elementService.getElements();
    this.sectionList = [
      '',
      'Course and Supervisor',
      'Project',
      'Assessment',
      'Assessment',
      'Assessment',
    ];

    this.formFlag = 'project';


    this.elements.forEach((element: any) => {
      if ((element.flag === 'common' || element.flag === this.formFlag || element.flag === '') && element.key !== 'course') {
        this.filteredElements.push(element);
      }
    });

    this.form = this.cfcs.toFormGroup(this.filteredElements, '');


  }

  ngOnInit() {
    // this.contractViewer = this.showContract();
    this.state$ = this.activatedRoute.paramMap
        .pipe(
            map(() => window.history.state
                , this.message = window.history.state
            ));

    console.log(this.message);

    this.supervisorService.getSupervise()
        .subscribe((data: any) => {
          data.forEach(supervise => {
            if (supervise.contract === this.message.contractId) {
              Object.assign(this.contractViewer, {projectSupervisor: supervise.id});
              this.form.controls.projectSupervisor.setValue(this.contractViewer.projectSupervisor);
              this.onFormChanges();
            }
          });
        });
    Object.assign(this.contractViewer, {
      semester: this.message.contractObj.semester,
      duration: this.message.contractObj.duration,
      year: this.message.contractObj.year,
      title: this.message.contractObj.special_topics ? this.message.contractObj.special_topics.title :
          this.message.contractObj.individual_project.title,
      objectives: this.message.contractObj.special_topics ? this.message.contractObj.special_topics.objectives :
          this.message.contractObj.individual_project.objectives,
      description: this.message.contractObj.special_topics ? this.message.contractObj.special_topics.description :
          this.message.contractObj.individual_project.description,
      assessment: this.message.assessment,
      assessment1: this.message.assessment[0].assessmentName,
      assessment1Description: this.message.assessment[0].additionalDescription,
      assessment1Mark: this.message.assessment[0].maxMark,
      assessment1Due: this.message.assessment[0].due,
      assessment1Examiner: this.message.assessment[0].examiner,
      assessment2: this.message.assessment[1].assessmentName,
      assessment2Description: this.message.assessment[1].additionalDescription,
      assessment2Mark: this.message.assessment[1].maxMark,
      assessment2Due: this.message.assessment[1].due,
      assessment2Examiner: this.message.assessment[1].examiner,
      assessment3: this.message.assessment[2].assessmentName,
      assessment3Description: this.message.assessment[2].additionalDescription,
      assessment3Mark: this.message.assessment[2].maxMark,
      assessment3Due: this.message.assessment[2].due,
      assessment3Examiner: this.message.assessment[2].examiner,
    });
    console.log(this.contractViewer);


    this.form.controls.semester.setValue(this.contractViewer.semester);
    this.form.controls.year.setValue(this.contractViewer.year);
    this.form.controls.duration.setValue(this.contractViewer.duration);

    this.form.controls.title.setValue(this.contractViewer.title);
    this.form.controls.objectives.setValue(this.contractViewer.objectives);
    this.form.controls.description.setValue(this.contractViewer.description);

    this.form.controls.assessment1.setValue(this.contractViewer.assessment[0].template);
    this.form.controls.assessment1Description.setValue(this.contractViewer.assessment1Description);
    this.form.controls.assessment1Mark.setValue(this.contractViewer.assessment1Mark);
    this.form.controls.assessment1Due.setValue(this.contractViewer.assessment1Due);
    this.form.controls.assessment1Examiner.setValue(this.contractViewer.assessment1Examiner);

    this.form.controls.assessment2.setValue(this.contractViewer.assessment[1].template);
    this.form.controls.assessment2Description.setValue(this.contractViewer.assessment2Description);
    this.form.controls.assessment2Mark.setValue(this.contractViewer.assessment2Mark);
    this.form.controls.assessment2Due.setValue(this.contractViewer.assessment2Due);
    this.form.controls.assessment2Examiner.setValue(this.contractViewer.assessment2Examiner);

    this.form.controls.assessment3.setValue(this.contractViewer.assessment[2].template);
    this.form.controls.assessment3Description.setValue(this.contractViewer.assessment3Description);
    this.form.controls.assessment3Mark.setValue(this.contractViewer.assessment3Mark);
    this.form.controls.assessment3Due.setValue(this.contractViewer.assessment3Due);
    this.form.controls.assessment3Examiner.setValue(this.contractViewer.assessment3Examiner);


  }

  onFormChanges() {
    this.form.valueChanges.subscribe(() => {
      this.isContractChanged = true;
    });
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

  onSubmit() {
    // implement patch to the contract
  }


  isAnotherSection(order): boolean {
    if (order > 1) {
      return (order % 10 === 0);
    } else {
      return true;
    }
  }

  isTextArea(type): boolean {
    return (type === 'textarea');
  }

  isLastElement(val, elements): boolean {
    if (elements.indexOf(val) + 1 < elements.length) {
      if (val.order > 10) {
        return elements[elements.indexOf(val) + 1].order.toString().charAt(0) !== val.order.toString().charAt(0);
      } else {
        return elements[elements.indexOf(val) + 1].order - val.order > 2;
      }
    }
  }

  sectionDivider(order): number {
    if (order === 1) {
      return order;
    } else {
      return (order / 10) + 1;
    }
  }

  getErrorMessage(formControl) {
    return formControl.hasError('required') ? 'You must enter a value' : '';
  }

}

