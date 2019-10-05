import {Component, EventEmitter, Input, OnChanges, OnInit, Output, SimpleChanges} from '@angular/core';
import { FormGroup } from '@angular/forms';
import { ElementBase } from '../element-base';
import { ContractFormControlService } from '../contract-form-control.service';
import { HttpErrorResponse } from '@angular/common/http';
import { ContractService } from '../contract.service';

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
        public contractService: ContractService
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

    onSubmit() {
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
        this.contractService.addContract(JSON.stringify(this.payLoad))
            .subscribe((res) => {
                this.contractId = res.id;
                this.addAssessmentMethod();
                this.addSupervise();
            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });
    }

    addAssessmentMethod() {

        this.assessment1 = {
            template: this.form.value.assessment1,
            contract: this.contractId,
            additional_description: this.form.value.assessment1Description,
            due: this.form.value.assessment1Due,
            max_mark: this.form.value.assessment1Mark,
            examiner: this.form.value.assessment1Examiner
        };

        this.contractService.addAssessmentMethod(JSON.stringify(this.assessment1))
            .subscribe(() => {

            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });

        this.assessment2 = {
            template: this.form.value.assessment2,
            contract: this.contractId,
            additional_description: this.form.value.assessment2Description,
            due: this.form.value.assessment2Due,
            max_mark: this.form.value.assessment2Mark,
            examiner: this.form.value.assessment2Examiner
        };

        console.log(this.form.value.assessment2);

        this.contractService.addAssessmentMethod(JSON.stringify(this.assessment2))
            .subscribe(() => {

            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });

        this.assessment3 = {
            template: this.form.value.assessment3,
            contract: this.contractId,
            additional_description: this.form.value.assessment3Description,
            due: this.form.value.assessment3Due,
            max_mark: this.form.value.assessment3Mark,
            examiner: this.form.value.assessment3Examiner
        };

        this.contractService.addAssessmentMethod(JSON.stringify(this.assessment3))
            .subscribe(() => {

            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });
    }

    addSupervise() {
        this.supervise = {
            supervisor: this.form.value.projectSupervisor,
            contract: this.contractId,
            is_formal: true
        };

        this.contractService.addSupervise(JSON.stringify(this.supervise))
            .subscribe(() => {

            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });
    }
}
