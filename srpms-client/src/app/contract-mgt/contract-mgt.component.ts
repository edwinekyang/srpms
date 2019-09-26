import {Component, OnInit} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {ContractService} from '../contract.service';
import {ContractMgtService} from '../contract-mgt.service';
import {AccountsService, SrpmsUser} from '../accounts.service';
import {Router} from '@angular/router';

export interface ContractList<T> {
    contractId: string;
    studentName: string;
    studentId: string;
    title: string;
    contractObj: any;
}

export interface SuperviseList<T> {
    id: number;
}

export interface AssessmentMethodList<T> {
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
    styleUrls: ['./contract-mgt.component.scss']
})


export class ContractMgtComponent implements OnInit {
    private errorMessage: string;
    public awaitingContractList: ContractList<any>[] = [];
    public approvedContractList: ContractList<any>[] = [];
    private readonly superviseList: SuperviseList<any>[] = [];
    private readonly approvedList: SuperviseList<any>[] = [];
    public route: string;
    // private supervisorID: string;

    constructor(
        public contractService: ContractService,
        public contractMgtService: ContractMgtService,
        public accountService: AccountsService,
        private router: Router,
    ) {
        this.route = this.router.url;
        this.superviseList = this.showSupervise();
        this.approvedList = this.showApprove();
        this.awaitingContractList = this.showContracts(this.superviseList);
        this.approvedContractList = this.showContracts(this.approvedList);
        // this.supervisorID = JSON.parse(localStorage.getItem('srpmsUser')).id;
    }

    ngOnInit() {
    }

    sendContractObj(contractObj: any) {
        this.contractMgtService.changeMessage(contractObj);
    }

    showSupervise(): SuperviseList<any>[] {
        let superviseList: SuperviseList<any>[];
        superviseList = [];
        if (this.route === '/supervisor') {
            this.contractMgtService.getSupervise()
                .subscribe((data: any) => {
                    data.forEach(supervise => {
                        if (supervise.supervisor === JSON.parse(localStorage.getItem('srpmsUser')).id &&
                            !supervise.supervisor_approval_date) {
                            superviseList.push({
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
                            superviseList.push({
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
        return superviseList;
    }

    showExamine(): SuperviseList<any> {
        let examineList: SuperviseList<any>[];
        examineList = [];
        this.contractMgtService.getExamine()
            .subscribe((data: any) => {

            }, error => {
                if (error instanceof HttpErrorResponse) {
                    this.errorMessage = error.error.detail;
                }
            })
        return;
    }

    showApprove(): SuperviseList<any>[] {
        let approvedList: SuperviseList<any>[];
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

    showContracts(contractIdList: SuperviseList<any>[]): ContractList<any>[] {
        let contractList: ContractList<any>[];
        contractList = [];
        this.contractService.getContracts()
            .subscribe(
                (contracts: any) => {
                    contractIdList.forEach(contract => {
                        this.accountService.getUser(contracts[contract.id - 1].owner)
                            .subscribe(
                                (student: SrpmsUser) => {
                                    Object.assign(contracts[contract.id - 1], {
                                        studentId: student.uni_id,
                                        studentName: student.first_name + ' ' + student.last_name,
                                    });
                                    contractList.push({
                                        contractId: contracts[contract.id - 1].id,
                                        studentId: student.uni_id,
                                        studentName: student.first_name + ' ' + student.last_name,
                                        title: contracts[contract.id - 1].special_topics ? contracts[contract.id - 1].special_topics.title :
                                            contracts[contract.id - 1].individual_project.title,
                                        contractObj: contracts[contract.id - 1],
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
