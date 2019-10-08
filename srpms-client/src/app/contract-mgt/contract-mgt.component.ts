import {Component, OnInit} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {ContractService, Course} from '../contract.service';
import {ContractMgtService} from '../contract-mgt.service';
import {AccountsService, SrpmsUser} from '../accounts.service';
import {Router} from '@angular/router';
import {ContractDialogComponent} from '../contract-dialog/contract-dialog.component';
import {MatDialog} from '@angular/material';

export interface ContractList<T> {
    contractId: string;
    studentName: string;
    studentId: string;
    title: string;
    contractObj: any;
    courseNumber: string;
    courseName: string;
    assessment: [];
}

export interface AssessmentList<T> {
    id: any;
    examineId: any;
    template: number;
    assessmentName: string;
    contract: number;
    due: string;
    weight: number;
    examiner: number;
    isAllExaminersApproved: boolean;
    examinerApprovalDate: string;
    additionalDescription: string;
}


@Component({
    selector: 'app-contract-mgt',
    templateUrl: './contract-mgt.component.html',
    styleUrls: ['./contract-mgt.component.scss'],
})


export class ContractMgtComponent implements OnInit {
    private errorMessage: string;
    public preContractList: ContractList<any>[] = [];
    public postContractList: ContractList<any>[] = [];
    private preList: number[] = [];
    private postList: number[] = [];
    public preAssessmentList: AssessmentList<any>[] = [];
    public postAssessmentList: AssessmentList<any>[] = [];
    public route: string;
    public courses: Course[] = [];

    constructor(
        public contractService: ContractService,
        private contractMgtService: ContractMgtService,
        public accountService: AccountsService,
        private router: Router,
        public dialog: MatDialog,
    ) {
        this.route = this.router.url;
    }

    ngOnInit() {
        this.initView().then();
    }

    async initView() {
        // Pre-contract list
        this.getPreContractIds().then(
            async () => {
                await this.showAssessments(this.preList, 'pre');
                await this.contractService.getCourses().toPromise()
                    .then(async (courses: Course[]) => {
                        this.courses = courses;
                        await this.showContracts(this.preList, 'pre');
                    }, error => {
                        if (error instanceof HttpErrorResponse) {
                            this.errorMessage = error.error.detail;
                        }
                    });
            });

        // Post-contract list
        this.getPostContractIds().then(
            async () => {
                await this.showAssessments(this.postList, 'post');
                await this.contractService.getCourses().toPromise()
                    .then(async (courses: Course[]) => {
                        this.courses = courses;
                        await this.showContracts(this.postList, 'post');
                    }, error => {
                        if (error instanceof HttpErrorResponse) {
                            this.errorMessage = error.error.detail;
                        }
                    });
            });
    }

    async getPreContractIds() {
        if (this.route === '/supervise') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPreList = data.supervise.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (contract.is_submitted && !contract.supervise[0].is_supervisor_approved) {
                                this.preList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPreList);
                });
        } else if (this.route === '/examine') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPreList = data.examine.map(async id => {
                        await this.contractMgtService.getAssessments(id).toPromise().then(async assessments => {
                            const promiseAssessments = assessments.map(assessment => {
                                if (assessment.assessment_examine[0].examiner ===
                                    JSON.parse(localStorage.getItem('srpmsUser')).id &&
                                    !assessment.assessment_examine[0].examiner_approval_date) {
                                    this.preList.push(id);
                                }
                            });
                            await Promise.all(promiseAssessments);
                        });
                    });
                    await Promise.all(promisesPreList);
                });
        } else if (this.route === '/submit') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPreList = data.own.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (!contract.is_submitted) {
                                this.preList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPreList);
                });
        }
    }

    async getPostContractIds() {
        if (this.route === '/supervise') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPostList = data.supervise.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (contract.is_submitted && contract.supervise[0].is_supervisor_approved) {
                                this.postList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPostList);
                });
        } else if (this.route === '/submit') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPostList = data.own.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (contract.is_submitted) {
                                this.postList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPostList);
                });
        } else if (this.route === '/examine') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPostList = data.examine.map(async id => {
                        await this.contractMgtService.getAssessments(id).toPromise().then(async assessments => {
                            const promiseAssessments = assessments.map(assessment => {
                                if (assessment.assessment_examine[0].examiner ===
                                    JSON.parse(localStorage.getItem('srpmsUser')).id &&
                                    assessment.assessment_examine[0].examiner_approval_date) {
                                    this.postList.push(id);
                                }
                            });
                            await Promise.all(promiseAssessments);
                        });
                    });
                    await Promise.all(promisesPostList);
                });
        }
    }

    async showContracts(contractIdList: number[], type: string) {
        let assessmentList: any;
        const promiseContractIdList = contractIdList.map(async (contractId: number) => {
            await this.contractMgtService.getContract(contractId).toPromise()
                .then(async contract => {
                    await this.accountService.getUser(contract.owner).toPromise()
                        .then(async (student: SrpmsUser) => {
                            assessmentList = [];
                            if (type === 'pre') {
                                this.preAssessmentList.forEach(assessment => {
                                    if (assessment.contract === contractId) {
                                        assessmentList.push(assessment);
                                    }
                                });
                            } else if (type === 'post') {
                                this.postAssessmentList.forEach(assessment => {
                                    if (assessment.contract === contractId) {
                                        assessmentList.push(assessment);
                                    }
                                });
                            }
                            const promisesCourses = this.courses.map(async course => {
                                if (course.id === contract.course) {
                                    if (type === 'pre') {
                                        this.preContractList.push({
                                            courseNumber: course.course_number,
                                            courseName: course.name,
                                            contractId: contract.id,
                                            studentId: student.uni_id,
                                            studentName: student.first_name + ' ' + student.last_name,
                                            title: contract.special_topics ?
                                                contract.special_topics.title :
                                                contract.individual_project.title,
                                            contractObj: contract,
                                            assessment: assessmentList,
                                        });
                                    } else if (type === 'post') {
                                        this.postContractList.push({
                                            courseNumber: course.course_number,
                                            courseName: course.name,
                                            contractId: contract.id,
                                            studentId: student.uni_id,
                                            studentName: student.first_name + ' ' + student.last_name,
                                            title: contract.special_topics ?
                                                contract.special_topics.title :
                                                contract.individual_project.title,
                                            contractObj: contract,
                                            assessment: assessmentList,
                                        });
                                    }
                                }
                            });

                            await Promise.all(promisesCourses);
                        });
                });
        });

        await Promise.all(promiseContractIdList);
    }

    async showAssessments(contractIdList: number[], type: string) {
        const promiseContractIdList = contractIdList.map(async id => {
            await this.contractMgtService.getAssessments(id).toPromise()
                .then(async assessments => {
                    const promiseAssessments = assessments.map(async assessment => {
                        if (type === 'pre') {
                            this.preAssessmentList.push({
                                id: assessment.id,
                                examineId: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].id : '',
                                template: assessment.template,
                                assessmentName: assessment.template_info.name,
                                contract: assessment.contract,
                                due: assessment.due,
                                weight: assessment.weight,
                                examiner: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].examiner : '',
                                isAllExaminersApproved: assessment.is_all_examiners_approved,
                                examinerApprovalDate: assessment.examiner_approval_date,
                                additionalDescription: assessment.additional_description,
                            });
                        } else if (type === 'post') {
                            this.postAssessmentList.push({
                                id: assessment.id,
                                examineId: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].id : '',
                                template: assessment.template,
                                assessmentName: assessment.template_info.name,
                                contract: assessment.contract,
                                due: assessment.due,
                                weight: assessment.weight,
                                examiner: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].examiner : '',
                                isAllExaminersApproved: assessment.is_all_examiners_approved,
                                examinerApprovalDate: assessment.examiner_approval_date,
                                additionalDescription: assessment.additional_description,
                            });
                        }
                    });
                    await Promise.all(promiseAssessments);
                }, error => {
                    if (error instanceof HttpErrorResponse) {
                        this.errorMessage = error.error.detail;
                    }
                });
        });

        await Promise.all(promiseContractIdList);
    }

    submit(contractId: any) {
        this.contractMgtService.updateSubmitted(contractId).subscribe(() => {
            this.openSuccessDialog();
        });
    }

    async approve(value: any, contract: any) {
        // Nominate the examiner
        const promiseNomination = contract.contractObj.assessment.map(async assessment => {
            if (assessment.template === 1) {
                await this.contractMgtService.addExamine(contract.contractId, assessment.id, JSON.stringify({
                    examiner: value,
                }))
                    .toPromise().then(() => {

                    });
            }
        });

        await Promise.all(promiseNomination);


        // Approve the contract
        await this.contractMgtService.approveContract(contract.contractId, contract.contractObj.supervise[0].id,
            JSON.stringify({
                approve: true,
            }))
            .toPromise().then(() => {

            });

        // Confirm supervisor's examiner role of the one of the assessments
        const promiseConfirmExamine = contract.contractObj.assessment.map(async assessment => {
            if (assessment.template === 2) {
                await this.contractMgtService.confirmExamine(contract.contractId, assessment.id,
                    assessment.assessment_examine[0].id, JSON.stringify({
                        approve: true,
                    }))
                    .toPromise().then(() => {

                    });
            }
        });

        await Promise.all(promiseConfirmExamine).then(() => {
            this.openSuccessDialog();
        });

    }

    private openSuccessDialog() {
        const dialogRef = this.dialog.open(ContractDialogComponent, {
            width: '400px',
        });

        dialogRef.afterClosed().subscribe(() => {
            this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
                this.router.navigate([this.route]).then(() => {});
            });
        });
    }

    async confirm(contractId: any, assessments: any) {
        let assessmentId: number;
        let examineId: number;
        assessmentId = 0;
        examineId = 0;
        const promiseAssessments = assessments.map(assessment => {
            if (assessment.examiner === JSON.parse(localStorage.getItem('srpmsUser')).id) {
                assessmentId = assessment.id;
                examineId = assessment.examineId;
            }
        });
        await Promise.all(promiseAssessments).then(() => {
            this.contractMgtService.confirmExamine(contractId, assessmentId, examineId,
                JSON.stringify({
                    approve: true,
                })).subscribe(() => {
                this.openSuccessDialog();
            });
        });
    }
}
