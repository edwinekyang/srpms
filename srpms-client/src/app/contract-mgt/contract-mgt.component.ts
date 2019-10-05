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

export interface IdList<T> {
    id: number;
}

export interface AssessmentList<T> {
    template: number;
    contract: number;
    due: string;
    maxMark: number;
    examiner: number;
    isExaminerApproved: boolean;
    examinerApprovalDate: string;
    additionalDescription: string;
}

export interface AssessmentTemplate<T> {
    id: number;
    name: string;
    description: string;
    minMark: number;
    maxMark: number;
    defaultMark: number;
}

@Component({
    selector: 'app-supervisor',
    templateUrl: './contract-mgt.component.html',
    styleUrls: ['./contract-mgt.component.scss'],
})


export class ContractMgtComponent implements OnInit {
    private errorMessage: string;
    public preContractList: ContractList<any>[] = [];
    public postContractList: ContractList<any>[] = [];
    private preList: IdList<any>[] = [];
    private postList: IdList<any>[] = [];
    public preAssessmentList: AssessmentList<any>[] = [];
    public route: string;
    public courses: Course[] = [];
    private message: any;
    public assessmentTemplates: AssessmentTemplate<any>[] = [];
    // private supervisorID: string;

    constructor(
        public contractService: ContractService,
        private contractMgtService: ContractMgtService,
        public accountService: AccountsService,
        private router: Router,
    ) {
        this.route = this.router.url;
        // Pre-list
        /*this.showIds().then(
            res1 => {
                console.log(this.preList);
                this.preAssessmentList = this.showAssessments(this.preList);
                this.getAssessmentTemplates();
            });*/
        this.initView().then(res => {
            this.contractService.getCourses()
                .subscribe((courses: Course[]) => {
                    this.courses = courses;
                    this.preContractList = this.showContracts(this.preList, 'pre');
                    this.postContractList = this.showContracts(this.postList, 'post');
                }, error => {
                    if (error instanceof HttpErrorResponse) {
                        this.errorMessage = error.error.detail;
                    }
                });
        });

        /* // Post-list
         this.postList = this.showApprove();
         */
        /*this.contractService.getCourses()
            .subscribe((courses: Course[]) => {
                this.courses = courses;
                this.awaitingContractList = this.showContracts(this.preList);
                this.approvedContractList = this.showContracts(this.postList);
            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });*/
        // this.supervisorID = JSON.parse(localStorage.getItem('srpmsUser')).id;
    }

    ngOnInit() {
    }

    async initView() {
        // Pre-contract ID list
        await this.getPreContractIds().then(
            res1 => {
                this.preAssessmentList = this.showAssessments(this.preList);
                this.getAssessmentTemplates();
            });

        // Post-contract ID list
        this.postList = this.getPostContractIds();
    }

    async getPreContractIds() {
        if (this.route === '/supervise') {
            await this.contractMgtService.getSupervise()
                .subscribe((data: any) => {
                    data.forEach(supervise => {
                        if (supervise.supervisor === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                            !supervise.supervisor_approval_date) {
                            this.contractService.getContracts()
                                .subscribe((contracts: any) => {
                                    contracts.forEach(contract => {
                                        if (supervise.contract === contract.id && contract.is_submitted) {
                                            this.preList.push({
                                                id: supervise.contract,
                                                // supervisor: supervise.supervisor,
                                            });
                                        }
                                    });
                                });
                        }
                    });
                }, error => {
                    if (error instanceof HttpErrorResponse) {
                        this.errorMessage = error.error.detail;
                    }
                });
        } else if (this.route === '/examine') {
            await this.contractMgtService.getAssessmentMethods()
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
                });
        } else if (this.route === '/submit') {
            await this.contractService.getContracts()
                .subscribe((contracts: any) => {
                    contracts.forEach(contract => {
                        if (contract.owner === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                            !contract.is_submitted) {
                            this.preList.push({
                                id: contract.id,
                            });
                        }
                    });
                });
        }
        return new Promise((resolve, reject) => {
            resolve();
        });
    }

    getPostContractIds(): IdList<any>[] {
        let postList: IdList<any>[];
        postList = [];
        if (this.route === '/supervise') {
            this.contractMgtService.getSupervise()
                .subscribe((data: any) => {
                    data.forEach(supervise => {
                        if (supervise.supervisor === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                            supervise.supervisor_approval_date) {
                            postList.push({
                                id: supervise.contract,
                                // supervisor: supervise.supervisor,
                            });
                        }
                    });
                }, error => {
                    if (error instanceof HttpErrorResponse) {
                        this.errorMessage = error.error.detail;
                    }
                });
        } else if (this.route === '/submit') {
            this.contractService.getContracts()
                .subscribe((contracts: any) => {
                    contracts.forEach(contract => {
                        if (contract.owner === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                            contract.is_submitted) {
                            postList.push({
                                id: contract.id,
                            });
                        }
                    });
                });
        }

        return postList;
    }

    showContracts(contractIdList: IdList<any>[], type: string): ContractList<any>[] {
        let contractList: ContractList<any>[];
        contractList = [];
        let assessmentList: any;
        this.contractService.getContracts()
            .subscribe((contracts: any) => {
                contractIdList.forEach(contractId => {
                    this.accountService.getUser(contracts[contractId.id - 1].owner)
                        .subscribe((student: SrpmsUser) => {
                            assessmentList = [];
                            if (type === 'pre') {
                                this.preAssessmentList.forEach(assessment => {
                                    if (assessment.contract === contractId.id) {
                                        assessmentList.push(assessment);
                                    }
                                });
                            } else if (type === 'post') {
                                /*this.postAssessmentList.forEach(assessment => {
                                    if (assessment.contract === contractId.id) {
                                        assessmentList.push(assessment);
                                    }
                                });*/
                            }
                            this.courses.forEach(course => {
                                if (course.id === contracts[contractId.id - 1].course) {
                                    contractList.push({
                                        courseNumber: course.course_number,
                                        courseName: course.name,
                                        contractId: contracts[contractId.id - 1].id,
                                        studentId: student.uni_id,
                                        studentName: student.first_name + ' ' + student.last_name,
                                        title: contracts[contractId.id - 1].special_topics ?
                                            contracts[contractId.id - 1].special_topics.title :
                                            contracts[contractId.id - 1].individual_project.title,
                                        contractObj: contracts[contractId.id - 1],
                                        assessment: assessmentList,
                                    });
                                }
                            });
                        });
                });
            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });
        return contractList;
    }

    private showAssessments(contractIdList: IdList<any>[]) {
        let assessmentList: AssessmentList<any>[];
        assessmentList = [];
        this.contractMgtService.getAssessmentMethods()
            .subscribe((assessments: any) => {
                assessments.forEach(assessment => {
                    contractIdList.forEach(contractId => {
                        if (assessment.contract === contractId.id) {
                            assessmentList.push({
                                template: assessment.template,
                                contract: assessment.contract,
                                due: assessment.due,
                                maxMark: assessment.max_mark,
                                examiner: assessment.examiner,
                                isExaminerApproved: assessment.is_examiner_approved,
                                examinerApprovalDate: assessment.examiner_approval_date,
                                additionalDescription: assessment.additional_description,
                            });
                        }
                    });
                });
            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });
        return assessmentList;
    }

    private getAssessmentTemplates() {
        this.contractMgtService.getAssessmentTemplates()
            .subscribe((templates: any) => {
                templates.forEach(template => {
                    this.assessmentTemplates.push({
                        id: template.id,
                        name: template.name,
                        description: template.description,
                        minMark: template.min_mark,
                        maxMark: template.max_mark,
                        defaultMark: template.default_mark,
                    });
                });

                // Push assessment names in the list
                this.preAssessmentList = this.pushAssessmentName(this.preAssessmentList, this.assessmentTemplates);

            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });
    }

    private pushAssessmentName(assessmentList: AssessmentList<any>[], templateList: AssessmentTemplate<any>[]) {
        assessmentList.forEach(assessment => {
            templateList.forEach(template => {
                if (assessment.template === template.id) {
                    Object.assign(assessment, {assessmentName: template.name});
                }
            });
        });
        return assessmentList;
    }

    submit(id: any) {
        this.contractService.updateSubmitted(id);
    }
}
