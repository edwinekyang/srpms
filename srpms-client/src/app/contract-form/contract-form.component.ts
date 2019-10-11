import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';
import { FormGroup } from '@angular/forms';
import { ElementBase } from '../element-base';
import { ContractFormControlService } from '../contract-form-control.service';
import {HttpErrorResponse} from '@angular/common/http';
import { ContractService } from '../contract.service';
import {ContractMgtService} from '../contract-mgt.service';
import {Router} from '@angular/router';
import {MatDialog} from '@angular/material';
import {ContractDialogComponent} from '../contract-dialog/contract-dialog.component';
import {map} from 'rxjs/operators';

@Component({
    selector: 'app-contract-form',
    templateUrl: './contract-form.component.html',
    styleUrls: ['./contract-form.component.scss'],
    providers: [ ContractFormControlService, ContractService ]
})
export class ContractFormComponent implements OnInit, OnChanges {
    errorMessage: string;
    @Input() elements: ElementBase<any>[] = [];
    form: FormGroup;
    payLoad = {};
    assessment = [];
    assessment1 = {};
    assessment2 = {};
    assessment3 = {};
    supervise = {};
    contractId: number;
    sectionList = [];
    formFlag: string;
    elementFlag: string;
    individualProject = {
    };
    specialTopics = {
    };
    message = {};
    courseValue: string;
    @Input() contractFlag: string;
    @Input() courseSelected: string;
    @Output() formFlagEvent = new EventEmitter<any>();

    constructor(
        private cfcs: ContractFormControlService,
        public contractService: ContractService,
        public contractMgtService: ContractMgtService,
        public dialog: MatDialog,
        private router: Router,
    ) {}

    ngOnInit() {
        // Attach the form control to the form elements
        if (this.elements.length === 1) {
            this.form = this.cfcs.toFormGroup(this.elements, 'course');
        } else {
            this.form = this.cfcs.toFormGroup(this.elements, '');
        }
        this.sectionList = [
            '',
            'Course and Supervisor',
            'Project',
            'Assessment',
            'Assessment',
            'Assessment',
        ];
        // Sets the value of course dropdown
        if (this.courseSelected) {
            this.form.controls.course.setValue(this.courseSelected);
        }
    }

    ngOnChanges(changes: SimpleChanges) {
        this.form = this.cfcs.toFormGroup(changes.elements.currentValue, '');
        if (this.courseSelected) {
            this.form.controls.course.setValue(changes.courseSelected.currentValue);
        }
    }

    /**
     * Receives the flag from ContractFormElementComponent and sends the flag to ContractComponent
     *
     * @param $event - Object that contains the flag and course value
     */
    receiveFormFlag($event) {
        this.formFlag = $event.formFlag;
        this.elementFlag = $event.formFlag;
        this.courseValue = $event.courseValue;
        this.message = {
            formFlag: this.formFlag,
            courseValue: this.courseValue,
        };
        this.sendFormFlag();
    }

    /**
     * Sends the flag to ContractComponent
     */
    sendFormFlag() {
        this.formFlagEvent.emit(this.message);
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
     * Saves the contract and this function includes:
     * 1. Deciding whether the contract is the type of project or special topic,
     * 2. Creates the saved contract
     * 3. Creates the assessment relation of the contract
     * 4. Creates the supervise relation of the contract
     */
    async onSubmit() {
        this.payLoad = {
            year: this.form.value.year,
            semester: this.form.value.semester,
            duration: this.form.value.duration,
            resources: '',
            course: this.form.value.course,
            owner: JSON.parse(localStorage.getItem('srpmsUser')).id,
        };
        if (this.contractFlag === 'project') {
            this.individualProject = {
                individual_project: {
                    title: this.form.value.title,
                    objectives: this.form.value.objectives,
                    description: this.form.value.description
                },
            };
            Object.assign(this.payLoad, this.individualProject);
        } else if (this.contractFlag === 'special') {
            this.specialTopics = {
                special_topics: {
                    title: this.form.value.title,
                    objectives: this.form.value.objectives,
                    description: this.form.value.description
                },
            };
            Object.assign(this.payLoad, this.specialTopics, {duration: 1});
        }
        await this.contractService.addContract(JSON.stringify(this.payLoad))
            .toPromise().then(async (res) => {
                this.contractId = res.id;
                await this.addAssessmentMethod().then(async () => {
                    await this.addSupervise();
                });
            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });
    }

    /**
     * Creates the assessment relation of the contract
     * This function goes as following:
     * 1. Assign the corresponding assessment section values to the assessment object
     * 2. Retrieves the assessment relations of the contract
     *    (Assessment relations are created automatically by default when the contract is created in back-end)
     * 3. Updates the assessment information to the assessment relation that has the matching template id
     * 4. Inside above assessment relation, creates the examine relation with the corresponding examiner ID
     */
    async addAssessmentMethod() {

        this.assessment1 = {
            template: this.form.value.assessment1,
            contract: this.contractId,
            additional_description: this.form.value.assessment1Description,
            due: this.form.value.assessment1Due,
            weight: this.form.value.assessment1Mark,
            examiner: this.form.value.assessment1Examiner
        };

        this.assessment2 = {
            template: this.form.value.assessment2,
            contract: this.contractId,
            additional_description: this.form.value.assessment2Description,
            due: this.form.value.assessment2Due,
            weight: this.form.value.assessment2Mark,
            examiner: this.form.value.assessment2Examiner
        };

        this.assessment3 = {
            template: this.form.value.assessment3,
            contract: this.contractId,
            additional_description: this.form.value.assessment3Description,
            due: this.form.value.assessment3Due,
            weight: this.form.value.assessment3Mark,
            examiner: this.form.value.assessment3Examiner
        };

        this.assessment.push(this.assessment1, this.assessment2, this.assessment3);
        await this.contractMgtService.getAssessments(this.contractId)
            .pipe(
                map( assessments => {
                    assessments.map(assessment => {
                        if (assessment.template === 1) {
                            const promisePatch1 = this.contractService.patchAssessment(this.contractId, assessment.id,
                                JSON.stringify(this.assessment1)).toPromise();
                            Promise.race([promisePatch1]);
                            // @ts-ignore
                            if (this.assessment1.examiner) {
                                const promiseAdd1 = this.contractMgtService.addExamine(this.contractId, assessment.id, JSON.stringify({
                                    // @ts-ignore
                                    examiner: this.assessment1.examiner,
                                })).toPromise();
                                Promise.race([promiseAdd1]);
                            }
                        }
                        if (assessment.template === 2) {
                            const promiseAdd2 = this.contractMgtService.addExamine(this.contractId, assessment.id, JSON.stringify({
                                // @ts-ignore
                                examiner: this.assessment2.examiner,
                            })).toPromise();
                            Promise.race([promiseAdd2]);
                            const promisePatch2 = this.contractService.patchAssessment(this.contractId, assessment.id,
                                JSON.stringify(this.assessment2)).toPromise();
                            Promise.race([promisePatch2]);
                        }
                        if (assessment.template === 3) {
                            const promiseAdd3 = this.contractMgtService.addExamine(this.contractId, assessment.id, JSON.stringify({
                                // @ts-ignore
                                examiner: this.assessment3.examiner,
                            })).toPromise();
                            Promise.race([promiseAdd3]);
                            const promisePatch3 = this.contractService.patchAssessment(this.contractId, assessment.id,
                                JSON.stringify(this.assessment3)).toPromise();
                            Promise.race([promisePatch3]);
                        }
                    });
                })
            ).toPromise();
    }

    /**
     * Creates the supervise relation of the contract
     * This is the last step of saving the contract.
     * If this function successes, a dialog will pop-up and
     * the user will be redirected to the contract management page.
     */
    async addSupervise() {
        this.supervise = {
            supervisor: this.form.value.projectSupervisor,
            contract: this.contractId,
            is_formal: true
        };

        await this.contractService.addSupervise(this.contractId, JSON.stringify(this.supervise))
            .toPromise().then(() => {
                this.openSuccessDialog();
            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });
    }

    /**
     * Opens the dialog and redirects the user to the contract management page
     */
    private openSuccessDialog() {
        const dialogRef = this.dialog.open(ContractDialogComponent, {
            width: '400px',
        });

        dialogRef.afterClosed().subscribe(() => {
            this.router.navigate(['/submit']).then(() => {});
        });
    }
}
