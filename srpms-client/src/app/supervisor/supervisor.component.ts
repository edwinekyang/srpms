import {Component, Injectable, OnInit} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {ContractService} from '../contract.service';


export interface ContractList {
  studentName: string;
  studentId: string;
  title: string;
}

@Component({
  selector: 'app-supervisor',
  templateUrl: './supervisor.component.html',
  styleUrls: ['./supervisor.component.scss']
})


export class SupervisorComponent implements OnInit {
  private errorMessage: string;
  private contractList: ContractList[];

  constructor(public contractService: ContractService) {
    this.showContracts();
  }

  ngOnInit() {

  }

  showContracts() {
    this.contractService.getContracts()
        .subscribe(
            (data: any) => {
              console.log(data);
              data.forEach(contract => {
                // get student's uni_id, first_name and last_name with owner's ID
                // from Srpmsuser, url: user/id/
                this.contractList.push({
                  studentId: '',
                  studentName: '',
                  title: '',
                });

              });
            },
            error => {
              if (error instanceof HttpErrorResponse) {
                this.errorMessage = error.error.detail;
              }
            });
  }
}
