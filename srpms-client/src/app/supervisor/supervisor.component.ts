import {Component, Injectable, OnInit} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {ContractService} from '../contract.service';
import {SupervisorService} from '../supervisor.service';
import {AccountsService, SrpmsUser} from '../accounts.service';

export interface ContractList<T> {
  studentName: string;
  studentId: string;
  title: string;
}

export interface SuperviseList<T> {
  id: number;
}

@Component({
  selector: 'app-supervisor',
  templateUrl: './supervisor.component.html',
  styleUrls: ['./supervisor.component.scss']
})


export class SupervisorComponent implements OnInit {
  private errorMessage: string;
  public awaitingContractList: ContractList<any>[] = [];
  public approvedContractList: ContractList<any>[] = [];
  private readonly superviseList: SuperviseList<any>[] = [];
  private readonly approvedList: SuperviseList<any>[] = [];
  // private supervisorID: string;

  constructor(
      public contractService: ContractService,
      public supervisorService: SupervisorService,
      public accountService: AccountsService,
  ) {
    this.superviseList = this.showSupervise();
    this.approvedList = this.showApprove();
    this.awaitingContractList = this.showContracts(this.superviseList);
    this.approvedContractList = this.showContracts(this.approvedList);
    // this.supervisorID = JSON.parse(localStorage.getItem('srpmsUser')).id;
  }

  ngOnInit() {
  }

  showSupervise(): SuperviseList<any>[] {
    let superviseList: SuperviseList<any>[];
    superviseList = [];
    this.supervisorService.getSupervise()
        .subscribe(
            (data: any) => {
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
    return superviseList;
  }

  showApprove(): SuperviseList<any>[] {
    let approvedList: SuperviseList<any>[];
    approvedList = [];
    this.supervisorService.getSupervise()
        .subscribe(
            (data: any) => {
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
                          contractList.push({
                            studentId: student.uni_id,
                            studentName: student.first_name + ' ' + student.last_name,
                            title: contracts[contract.id - 1].special_topics ? contracts[contract.id - 1].special_topics.title :
                                contracts[contract.id - 1].individual_project.title,
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
