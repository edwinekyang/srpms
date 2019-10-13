import {Component, OnInit} from '@angular/core';
import {ContractMgtService} from '../contract-mgt.service';
import {ElementService} from '../element.service';
import {ElementBase} from '../element-base';
import {FormGroup} from '@angular/forms';
import {ContractFormControlService} from '../contract-form-control.service';
import {Observable} from 'rxjs';
import {ActivatedRoute, Router} from '@angular/router';
import {map} from 'rxjs/operators';
import {ContractDialogComponent} from '../contract-dialog/contract-dialog.component';
import {MatDialog} from '@angular/material';
import {HttpErrorResponse} from '@angular/common/http';
import {ErrorDialogComponent} from '../error-dialog/error-dialog.component';
import {ContractService} from '../contract.service';


@Component({
  selector: 'app-contract-viewer',
  templateUrl: './contract-viewer.component.html',
  styleUrls: ['./contract-viewer.component.scss'],
  providers: [
    ElementService,
    ContractService,
    ContractMgtService,
    ContractFormControlService,
  ]
})
export class ContractViewerComponent implements OnInit {
  public errorMessage = {};
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
      private contractService: ContractService,
      private contractMgtService: ContractMgtService,
      public elementService: ElementService,
      private cfcs: ContractFormControlService,
      public activatedRoute: ActivatedRoute,
      public dialog: MatDialog,
      private router: Router,
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
    // Needs to be changed in the future if the contract type is other than 'project'
    this.formFlag = 'project';

    this.elements.forEach((element: any) => {
      if ((element.flag === 'common' || element.flag === this.formFlag || element.flag === '') && element.key !== 'course') {
        this.filteredElements.push(element);
      }
    });
    // Attaches the form control to form elements
    this.form = this.cfcs.toFormGroup(this.filteredElements, '');
  }

  ngOnInit() {
    // Retrieves the contract object passed from ContractMgtComponent
    this.state$ = this.activatedRoute.paramMap
        .pipe(
            map(() => window.history.state
                , this.message = window.history.state
            ));

    // Sets the value of the contract supervisor in the form control
    // (e.g. this.form.controls.element-key.setValue(...)
    // and value attribute in input html tag in 'contractViewer'
    // 'contractViewer' will be used to assign the value attribute inside input html tag
    // (e.g. [value]="contractViewer[element.key]")
    this.contractMgtService.getSupervise(this.message.contractId).toPromise()
        .then(supervise => {
          if (supervise[0]) {
            Object.assign(this.contractViewer, {projectSupervisor: supervise[0].supervisor});
            this.form.controls.projectSupervisor.setValue(this.contractViewer.projectSupervisor);
          }
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

  /**
   * Changes 'isContractChanged' to true if the value inside the form element is changed
   */
  onFormChanges() {
    this.form.valueChanges.subscribe(() => {
      this.isContractChanged = true;
    });
  }

  /**
   * Saves the contract
   * 1. Decides whether the contract is the type of project or special topics
   * 2. Adds the general contract information to payload
   * 3. Updates the general contract information using payload
   * 4. Updates the supervise relation of the contract
   * 5. Updates the assessment relations and the examine relations
   * 6. Opens the dialog
   */
  async onSubmit() {
    if (confirm('Are you sure?')) {
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
      if (this.message.contractObj.supervise[0]) {
        await this.contractMgtService.updateSupervise(this.message.contractId, this.message.contractObj.supervise[0].id,
            JSON.stringify({
                  supervisor: this.form.value.projectSupervisor,
                }
            )).toPromise().catch((err: HttpErrorResponse) => {
          if (Math.floor(err.status / 100) === 4) {
            Object.assign(this.errorMessage, err.error);
          }
        });
      } else {
        await this.contractService.addSupervise(this.message.contractId, JSON.stringify({
          supervisor: this.form.value.projectSupervisor,
        })).toPromise().catch((err: HttpErrorResponse) => {
          if (Math.floor(err.status / 100) === 4) {
            Object.assign(this.errorMessage, err.error);
          }
        });
      }

      const promiseAssessments = this.message.contractObj.assessment.map(async assessment => {
        if (assessment.template === this.form.controls.assessment1.value) {
          await this.contractMgtService.updateAssessment(this.message.contractId, assessment.id, JSON.stringify({
            additional_description: this.form.value.assessment1Description,
            due: this.form.value.assessment1Due,
            weight: this.form.value.assessment1Mark,
          })).toPromise().catch((err: HttpErrorResponse) => {
            if (Math.floor(err.status / 100) === 4) {
              Object.assign(this.errorMessage, err.error);
            }
          });
          if (assessment.assessment_examine[0]) {
            await this.contractMgtService.updateExamine(this.message.contractId, assessment.id, assessment.assessment_examine[0].id,
                JSON.stringify({
                  examiner: this.form.value.assessment1Examiner,
                })).toPromise().catch((err: HttpErrorResponse) => {
              if (Math.floor(err.status / 100) === 4) {
                Object.assign(this.errorMessage, err.error);
              }
            });
          } else if (this.form.value.assessment1Examiner) {
            await this.contractMgtService.addExamine(this.message.contractId, assessment.id, JSON.stringify({
              examiner: this.form.value.assessment1Examiner,
            })).toPromise().catch((err: HttpErrorResponse) => {
              if (Math.floor(err.status / 100) === 4) {
                Object.assign(this.errorMessage, err.error);
              }
            });
          }
        }
        if (assessment.template === this.form.controls.assessment2.value) {
          await this.contractMgtService.updateAssessment(this.message.contractId, assessment.id, JSON.stringify({
            additional_description: this.form.value.assessment2Description,
            due: this.form.value.assessment2Due,
            weight: this.form.value.assessment2Mark,
          })).toPromise().catch((err: HttpErrorResponse) => {
            if (Math.floor(err.status / 100) === 4) {
              Object.assign(this.errorMessage, err.error);
            }
          });
          if (assessment.assessment_examine[0]) {
            await this.contractMgtService.updateExamine(this.message.contractId, assessment.id, assessment.assessment_examine[0].id,
                JSON.stringify({
                  examiner: this.form.value.assessment2Examiner,
                })).toPromise().catch((err: HttpErrorResponse) => {
              if (Math.floor(err.status / 100) === 4) {
                Object.assign(this.errorMessage, err.error);
              }
            });
          } else if (this.form.value.assessment2Examiner) {
            await this.contractMgtService.addExamine(this.message.contractId, assessment.id, JSON.stringify({
              examiner: this.form.value.assessment2Examiner,
            })).toPromise().catch((err: HttpErrorResponse) => {
              if (Math.floor(err.status / 100) === 4) {
                Object.assign(this.errorMessage, err.error);
              }
            });
          }
        }
        if (assessment.template === this.form.controls.assessment3.value) {
          await this.contractMgtService.updateAssessment(this.message.contractId, assessment.id, JSON.stringify({
            additional_description: this.form.value.assessment3Description,
            due: this.form.value.assessment3Due,
            weight: this.form.value.assessment3Mark,
          })).toPromise().catch((err: HttpErrorResponse) => {
            if (Math.floor(err.status / 100) === 4) {
              Object.assign(this.errorMessage, err.error);
            }
          });
          if (assessment.assessment_examine[0]) {
            await this.contractMgtService.updateExamine(this.message.contractId, assessment.id, assessment.assessment_examine[0].id,
                JSON.stringify({
                  examiner: this.form.value.assessment3Examiner,
                })).toPromise().catch((err: HttpErrorResponse) => {
              if (Math.floor(err.status / 100) === 4) {
                Object.assign(this.errorMessage, err.error);
              }
            });
          } else if (this.form.value.assessment3Examiner) {
            await this.contractMgtService.addExamine(this.message.contractId, assessment.id, JSON.stringify({
              examiner: this.form.value.assessment3Examiner,
            })).toPromise().catch((err: HttpErrorResponse) => {
              if (Math.floor(err.status / 100) === 4) {
                Object.assign(this.errorMessage, err.error);
              }
            });
          }
        }
      });
      await Promise.all(promiseAssessments).then(() => {
        if (Object.keys(this.errorMessage).length) {
          this.openFailDialog();
        } else {
          this.openSuccessDialog();
        }
      });
    }
  }

  /**
   * Decides whether the form element has reached to the next section and returns boolean value
   *
   * @param order - Order value of the from element
   */
  isAnotherSection(order): boolean {
    if (order > 1) {
      return (order % 10 === 0);
    } else {
      return true;
    }
  }

  /**
   * Decides whether the input of the form is 'textarea' html tag and returns boolean value
   *
   * @param type - Type value from the form element
   */
  isTextArea(type): boolean {
    return (type === 'textarea');
  }

  /**
   * Decides whether the form element is the last element of the section and returns boolean value
   *
   * @param val - Element object
   * @param elements - List of elements
   */
  isLastElement(val, elements): boolean {
    if (elements.indexOf(val) + 1 < elements.length) {
      if (val.order > 10) {
        return elements[elements.indexOf(val) + 1].order.toString().charAt(0) !== val.order.toString().charAt(0);
      } else {
        return elements[elements.indexOf(val) + 1].order - val.order > 2;
      }
    }
  }

  /**
   * Decides the number of the section and returns number value
   *
   * @param order - Order value of the element
   */
  sectionDivider(order): number {
    if (order === 1) {
      return order;
    } else {
      return (order / 10) + 1;
    }
  }

  /**
   * Retrieves the error message for the form element
   * Currently only required validation exists.
   *
   * @param formControl - Form Control object
   */
  getErrorMessage(formControl) {
    return formControl.hasError('required') ? 'You must enter a value' : '';
  }

  /**
   * Opens the dialog that contains corresponding information for the user's action
   * and redirect the user to '/submit'
   */
  private openSuccessDialog() {
    const dialogRef = this.dialog.open(ContractDialogComponent, {
      width: '400px',
    });

    dialogRef.afterClosed().subscribe(() => {
      this.router.navigate(['/submit']).then(() => {});
    });
  }

  /**
   * Opens the dialog to notify the user's action has been failed
   * and reloads the page
   */
  private openFailDialog() {
    const dialogRef = this.dialog.open(ErrorDialogComponent, {
      width: '400px',
      data: this.errorMessage,
    });

    dialogRef.afterClosed().subscribe(() => {
      this.router.navigate(['/submit']).then(() => {});
    });
  }

}

