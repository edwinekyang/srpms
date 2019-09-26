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
}

@Component({
    selector: 'app-supervisor',
    templateUrl: './contract-mgt.component.html',
    styleUrls: ['./contract-mgt.component.scss'],
})


export class ContractMgtComponent implements OnInit {
    private errorMessage: string;
    public awaitingContractList: ContractList<any>[] = [];
    public approvedContractList: ContractList<any>[] = [];
    private readonly preList: IdList<any>[] = [];
    private readonly postList: IdList<any>[] = [];
    public route: string;
    public courses: Course[] = [];
    // private supervisorID: string;

    constructor(
        public contractService: ContractService,
        public contractMgtService: ContractMgtService,
        public accountService: AccountsService,
        private router: Router,
    ) {
        this.route = this.router.url;
        this.preList = this.showIds();
        this.postList = this.showApprove();
        this.contractService.getCourses()
            .subscribe((courses: Course[]) => {
                this.courses = courses;
                this.awaitingContractList = this.showContracts(this.preList);
                this.approvedContractList = this.showContracts(this.postList);
            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });
        // this.supervisorID = JSON.parse(localStorage.getItem('srpmsUser')).id;
    }

    ngOnInit() {
    }

    sendContractObj(contractObj: any) {
        this.contractMgtService.changeMessage(contractObj);
    }

    showIds(): IdList<any>[] {
        let idList: IdList<any>[];
        idList = [];
        if (this.route === '/supervisor') {
            this.contractMgtService.getSupervise()
                .subscribe((data: any) => {
                    data.forEach(supervise => {
                        if (supervise.supervisor === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                            !supervise.supervisor_approval_date) {
                            idList.push({
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
        } else if (this.route === '/examnior') {
            this.contractMgtService.getAssessmentMethods()
                .subscribe((data: any) => {
                    data.forEach(assessmentMethods => {
                        if (assessmentMethods.examiner === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                            !assessmentMethods.is_examiner_approved) {
                            idList.push({
                                id: assessmentMethods.contract,
                            });
                        }
                    });
                }, error => {
                    if (error instanceof HttpErrorResponse) {
                        this.errorMessage = error.error.detail;
                    }
                });
        }
        return idList;
    }

    showExamine(): IdList<any>[] {
        let examineList: IdList<any>[];
        examineList = [];
        this.contractMgtService.getExamine()
            .subscribe((data: any) => {
                data.forEach(assessmentMethods => {
                    if (assessmentMethods.examiner === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                        !assessmentMethods.is_examiner_approved) {
                        examineList.push({
                            id: assessmentMethods.contract,
                        });
                    }
                });
            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            });
        return examineList;
    }

    showApprove(): IdList<any>[] {
        let approvedList: IdList<any>[];
        approvedList = [];
        this.contractMgtService.getSupervise()
            .subscribe((data: any) => {
                data.forEach(supervise => {
                    if (supervise.supervisor === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                        supervise.supervisor_approval_date) {
                        approvedList.push({
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
        return approvedList;
    }

    showContracts(contractIdList: IdList<any>[]): ContractList<any>[] {
        let contractList: ContractList<any>[];
        contractList = [];
        let assessmentList: any;
        assessmentList = [];
        this.contractService.getContracts()
            .subscribe(
                (contracts: any) => {
                    contractIdList.forEach(contractId => {
                        this.accountService.getUser(contracts[contractId.id - 1].owner)
                            .subscribe(
                                (student: SrpmsUser) => {
                                    Object.assign(contracts[contractId.id - 1], {
                                        studentId: student.uni_id,
                                        studentName: student.first_name + ' ' + student.last_name,
                                    });
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
                                            });
                                        }
                                    });

                                }
                            );
                    });
                },
                error => {
                    if (error instanceof HttpErrorResponse) {
                        this.errorMessage = error.error.detail;
                    }
                });
        return contractList;
    }
}
