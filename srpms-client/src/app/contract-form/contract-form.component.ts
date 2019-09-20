import { Component, Input, OnInit } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { ElementBase } from '../element-base';
import { ContractFormControlService } from '../contract-form-control.service';
import { HttpErrorResponse } from '@angular/common/http';
import { ContractService } from '../contract.service';

@Component({
  selector: 'app-contract-form',
  templateUrl: './contract-form.component.html',
  providers: [ ContractFormControlService, ContractService ]
})
export class ContractFormComponent implements OnInit {
  errorMessage: string;
  @Input() elements: ElementBase<any>[] = [];
  form: FormGroup;
  payLoad = '';
  assessment1 = {};
  assessment2 = {};
  assessment3 = {};
  supervise = {};
  contractId: number;

  constructor(
    private cfcs: ContractFormControlService,
    public contractService: ContractService
  ) {  }

  ngOnInit() {
    this.form = this.cfcs.toFormGroup(this.elements);
  }

  onSubmit() {
    this.payLoad = JSON.stringify(this.form.value);

    this.contractService.addContract(this.payLoad)
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
      additional_description: '',
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
      additional_description: '',
      due: this.form.value.assessment2Due,
      max_mark: this.form.value.assessment2Mark,
      examiner: this.form.value.assessment2Examiner
    };

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
      additional_description: '',
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
      supervisor: this.form.value.proejctSupervisor,
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
