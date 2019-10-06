import {Component, OnInit} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {ContractService, Course} from '../contract.service';
import {ContractMgtService} from '../contract-mgt.service';
import {AccountsService, SrpmsUser} from '../accounts.service';
import {Router} from '@angular/router';

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
            await this.contractMgtService.getContracts().toPromise()
                .then(async contracts => {
                    const promiseContracts = contracts.map(async contract => {
                        if (contract.supervise[0].supervisor === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                            contract.is_submitted && !contract.supervise[0].is_supervisor_approved) {
                            this.preList.push(contract.id);
                        }
                    });
                    await Promise.all(promiseContracts);
                });
        } else if (this.route === '/examine') {
            /*await this.contractMgtService.getAssessments()
                .subscribe((data: any) => {
                    data.forEach(assessmentMethods => {
                        if (assessmentMethods.examiner === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                            !assessmentMethods.is_examiner_approved) {
                            this.preList.push({
                                id: assessmentMethods.contract,
                            });
                        }
                    });
                }, error => {
                    if (error instanceof HttpErrorResponse) {
                        this.errorMessage = error.error.detail;
                    }
                });*/
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
            await this.contractMgtService.getContracts().toPromise()
                .then(async contracts => {
                    const promiseContracts = contracts.map(async contract => {
                        if (contract.supervise[0].supervisor === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                            contract.is_submitted && contract.supervise[0].is_supervisor_approved) {
                            this.postList.push(contract.id);
                        }
                    });
                    await Promise.all(promiseContracts);
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

    submit(id: any) {
        this.contractMgtService.updateSubmitted(id).subscribe(() => {
        });
    }

    onApprove(value: any, contract: any) {
        this.contractMgtService.approveContract(contract.contractId, contract.contractObj.supervise[0].id,
            JSON.stringify({
                approve: true,
            }))
            .subscribe();
        contract.contractObj.assessment.forEach(assessment => {
            if (assessment.template === 1) {
                this.contractMgtService.addExamine(contract.contractId, assessment.id, JSON.stringify({
                    examiner: value,
                }))
                    .subscribe();
            } else if (assessment.template === 2) {
                this.contractMgtService.approveExamine(contract.contractId, assessment.id,
                    assessment.assessment_examine[0].id, JSON.stringify({
                        approve: true,
                    }))
                    .subscribe();
            }
        });
    }
}
