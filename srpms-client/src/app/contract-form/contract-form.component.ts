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

    sendFormFlag() {
        this.formFlagEvent.emit(this.message);
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
            .toPromise().then(async assessments => {
                const promiseAssessment = assessments.map(async assessment => {
                    // @ts-ignore
                    if (assessment.template === this.assessment1.template) {
                        await this.contractService.patchAssessment(this.contractId, assessment.id, JSON.stringify(this.assessment1))
                            .toPromise();
                        // @ts-ignore
                        if (this.assessment1.examiner) {
                            this.contractMgtService.addExamine(this.contractId, assessment.id, JSON.stringify({
                                // @ts-ignore
                                examiner: this.assessment1.examiner,
                            })).subscribe();
                        }
                        // @ts-ignore
                    } else if (assessment.template === this.assessment2.template) {
                        await this.contractService.patchAssessment(this.contractId, assessment.id, JSON.stringify(this.assessment2))
                            .toPromise().then(() => {
                            });
                        // @ts-ignore
                        if (this.assessment2.examiner) {
                            this.contractMgtService.addExamine(this.contractId, assessment.id, JSON.stringify({
                                // @ts-ignore
                                examiner: this.assessment2.examiner,
                            })).subscribe();
                        }
                        // @ts-ignore
                    } else if (assessment.template === this.assessment3.template) {
                        await this.contractService.patchAssessment(this.contractId, assessment.id, JSON.stringify(this.assessment3))
                            .toPromise().then(() => {
                            });
                        // @ts-ignore
                        if (this.assessment3.examiner) {
                            this.contractMgtService.addExamine(this.contractId, assessment.id, JSON.stringify({
                                // @ts-ignore
                                examiner: this.assessment3.examiner,
                            })).subscribe();
                        }
                    }
                });

                await Promise.all(promiseAssessment);

            });
    }

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

    private openSuccessDialog() {
        const dialogRef = this.dialog.open(ContractDialogComponent, {
            width: '400px',
        });

        dialogRef.afterClosed().subscribe(() => {
            this.router.navigate(['/submit']).then(() => {});
        });
    }
}
