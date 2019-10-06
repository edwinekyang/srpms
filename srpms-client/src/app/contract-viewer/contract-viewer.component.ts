import {Component, OnInit} from '@angular/core';
import {ContractMgtService} from '../contract-mgt.service';
import {ElementService} from '../element.service';
import {ElementBase} from '../element-base';
import {FormGroup} from '@angular/forms';
import {ContractFormControlService} from '../contract-form-control.service';
import {Observable} from 'rxjs';
import {ActivatedRoute} from '@angular/router';
import {map} from 'rxjs/operators';


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
  private readonly formFlag: any;
  public isContractChanged: boolean;

  constructor(
      private contractMgtService: ContractMgtService,
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
    this.state$ = this.activatedRoute.paramMap
        .pipe(
            map(() => window.history.state
                , this.message = window.history.state
            ));

    this.contractMgtService.getSupervise(this.message.contractId).toPromise()
        .then(supervise => {
          Object.assign(this.contractViewer, {projectSupervisor: supervise[0].supervisor});
          this.form.controls.projectSupervisor.setValue(this.contractViewer.projectSupervisor);
          this.onFormChanges();
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
    });

    this.message.assessment.forEach(assessment => {
      if (this.form.controls.assessment1.value === assessment.template) {
        Object.assign(this.contractViewer, {
          assessment1: assessment.assessmentName,
          assessment1Description: assessment.additionalDescription,
          assessment1Mark: assessment.weight,
          assessment1Due: assessment.due,
          assessment1Examiner: assessment.examiner,
        });
        this.form.controls.assessment1.setValue(assessment.template);
        this.form.controls.assessment1Description.setValue(this.contractViewer.assessment1Description);
        this.form.controls.assessment1Mark.setValue(this.contractViewer.assessment1Mark);
        this.form.controls.assessment1Due.setValue(this.contractViewer.assessment1Due);
        this.form.controls.assessment1Examiner.setValue(this.contractViewer.assessment1Examiner);
      } else if (this.form.controls.assessment2.value === assessment.template) {
        Object.assign(this.contractViewer, {
          assessment2: assessment.assessmentName,
          assessment2Description: assessment.additionalDescription,
          assessment2Mark: assessment.weight,
          assessment2Due: assessment.due,
          assessment2Examiner: assessment.examiner,
        });
        this.form.controls.assessment2.setValue(assessment.template);
        this.form.controls.assessment2Description.setValue(this.contractViewer.assessment2Description);
        this.form.controls.assessment2Mark.setValue(this.contractViewer.assessment2Mark);
        this.form.controls.assessment2Due.setValue(this.contractViewer.assessment2Due);
        this.form.controls.assessment2Examiner.setValue(this.contractViewer.assessment2Examiner);
      } else if (this.form.controls.assessment3.value === assessment.template) {
        Object.assign(this.contractViewer, {
          assessment3: assessment.assessmentName,
          assessment3Description: assessment.additionalDescription,
          assessment3Mark: assessment.weight,
          assessment3Due: assessment.due,
          assessment3Examiner: assessment.examiner,
        });
        this.form.controls.assessment3.setValue(assessment.template);
        this.form.controls.assessment3Description.setValue(this.contractViewer.assessment3Description);
        this.form.controls.assessment3Mark.setValue(this.contractViewer.assessment3Mark);
        this.form.controls.assessment3Due.setValue(this.contractViewer.assessment3Due);
        this.form.controls.assessment3Examiner.setValue(this.contractViewer.assessment3Examiner);
      }
    });

    this.form.controls.semester.setValue(this.contractViewer.semester);
    this.form.controls.year.setValue(this.contractViewer.year);
    this.form.controls.duration.setValue(this.contractViewer.duration);

    this.form.controls.title.setValue(this.contractViewer.title);
    this.form.controls.objectives.setValue(this.contractViewer.objectives);
    this.form.controls.description.setValue(this.contractViewer.description);

  }

  onFormChanges() {
    this.form.valueChanges.subscribe(() => {
      this.isContractChanged = true;
    });
  }

  async onSubmit() {
    let payLoad: any;
    payLoad = {
      year: this.form.value.year,
      semester: this.form.value.semester,
      duration: this.form.value.duration,
    };
    if (this.message.contractObj.special_topics) {
      let specialTopics: any;
      specialTopics = {
        special_topics: {
          title: this.form.value.title,
          objectives: this.form.value.objectives,
          description: this.form.value.description
        },
      };
      Object.assign(payLoad, specialTopics);
    } else {
      let individualProject: any;
      individualProject = {
        individual_project: {
          title: this.form.value.title,
          objectives: this.form.value.objectives,
          description: this.form.value.description
        },
      };
      Object.assign(payLoad, individualProject);
    }
    await this.contractMgtService.updateContract(this.message.contractId, payLoad).toPromise();

    await this.contractMgtService.updateSupervise(this.message.contractId, this.message.contractObj.supervise[0].id,
        JSON.stringify({
              supervisor: this.form.value.projectSupervisor,
            }
        )).toPromise();

    const promiseAssessments = this.message.contractObj.assessment.map(assessment => {
      if (assessment.template === this.form.controls.assessment1.value) {
        this.contractMgtService.updateAssessment(this.message.contractId, assessment.id, JSON.stringify({
          additional_description: this.form.value.assessment1Description,
          due: this.form.value.assessment1Due,
          weight: this.form.value.assessment1Mark,
        })).toPromise();
        if (assessment.assessment_examine[0]) {
          this.contractMgtService.updateExamine(this.message.contractId, assessment.id, assessment.assessment_examine[0].id,
              JSON.stringify({
                examiner: this.form.value.assessment1Examiner,
              })).toPromise();
        }
      } else if (assessment.template === this.form.controls.assessment2.value) {
        this.contractMgtService.updateAssessment(this.message.contractId, assessment.id, JSON.stringify({
          additional_description: this.form.value.assessment2Description,
          due: this.form.value.assessment2Due,
          weight: this.form.value.assessment2Mark,
        })).toPromise();
        if (assessment.assessment_examine[0]) {
          this.contractMgtService.updateExamine(this.message.contractId, assessment.id, assessment.assessment_examine[0].id,
              JSON.stringify({
                examiner: this.form.value.assessment2Examiner,
              })).toPromise();
        }
      } else if (assessment.template === this.form.controls.assessment3.value) {
        this.contractMgtService.updateAssessment(this.message.contractId, assessment.id, JSON.stringify({
          additional_description: this.form.value.assessment3Description,
          due: this.form.value.assessment3Due,
          weight: this.form.value.assessment3Mark,
        })).toPromise();
        if (assessment.assessment_examine[0]) {
          this.contractMgtService.updateExamine(this.message.contractId, assessment.id, assessment.assessment_examine[0].id,
              JSON.stringify({
                examiner: this.form.value.assessment3Examiner,
              })).toPromise();
        }
      }
    });
    await Promise.all(promiseAssessments);
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

