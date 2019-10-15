/**
 * @fileoverview This file does actions requested from contract-mgt component.
 * @author euiyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import {Component, Inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialog, MatDialogRef} from '@angular/material';
import {Router} from '@angular/router';
import {FormControl, FormGroup} from '@angular/forms';
import {HttpErrorResponse} from '@angular/common/http';
import {ContractMgtService} from '../contract-mgt.service';
import {ErrorDialogComponent} from '../error-dialog/error-dialog.component';
import {ContractDialogComponent} from '../contract-dialog/contract-dialog.component';

export interface Contract {
  action: string;
  assessment: Array<object>;
  contractId: number;
  contractObj: any;
  courseName: string;
  courseNumber: string;
  status: string;
  studentId: string;
  studentName: string;
  title: string;
}
@Component({
  selector: 'app-contract-mgt-dialog',
  templateUrl: './contract-mgt-dialog.component.html',
  styleUrls: ['./contract-mgt-dialog.component.scss']
})
export class ContractMgtDialogComponent implements OnInit {
  public route: string;
  public examinerForm: FormGroup;
  public examinerFormValid: boolean;
  private errorMessage = {};

  constructor(
      public dialogRef: MatDialogRef<ContractMgtDialogComponent>,
      @Inject(MAT_DIALOG_DATA) public data: Contract,
      private router: Router,
      private contractMgtService: ContractMgtService,
      public dialog: MatDialog,
  ) {
    this.route = this.router.url;
    this.examinerForm = new FormGroup({
      examiner1: new FormControl(''),
      examiner2: new FormControl(''),
      examiner3: new FormControl(''),
    });
    this.examinerForm.statusChanges.subscribe(() => {
      this.examinerFormValid = this.examinerForm.valid;
    });
  }

  ngOnInit() {
    console.log(this.data);
  }

  /**
   * Closes the dialog on click
   */
  onClick() {
    this.dialogRef.close();
  }

  /**
   * Nominates the examiner used by course convener
   *
   * @param contract - Contract object
   */
  async nominateExaminer(contract: any) {
    if (confirm('Are you sure?')) {
      // Nominate the examiner
      if (contract.status !== 'Nominated') {
        const promiseAssessment = contract.assessment.map(async assessment => {
          if (this.examinerForm.value['examiner' + assessment.template]) {
            const promiseAdd = this.contractMgtService.addExamine(contract.contractId, assessment.id, JSON.stringify({
              examiner: this.examinerForm.value['examiner' + assessment.template],
            })).toPromise();
            await Promise.all([promiseAdd]).catch((err: HttpErrorResponse) => {
              if (Math.floor(err.status / 100) === 4) {
                Object.assign(this.errorMessage, err.error);
              }
            });
          }
        });
        await Promise.all(promiseAssessment).catch((err: HttpErrorResponse) => {
          if (Math.floor(err.status / 100) === 4) {
            Object.assign(this.errorMessage, err.error);
          }
        });
        if (Object.keys(this.errorMessage).length) {
          this.openFailDialog();
        } else {
          this.openSuccessDialog('NominateExaminer');
        }
      }
    }
  }

  /**
   * Opens the dialog to notify the user's action has been failed
   * and reloads the page
   */
  private openFailDialog() {
    const dialogRef = this.dialog.open(ErrorDialogComponent, {
      width: '400px',
      data:  this.errorMessage,
    });

    dialogRef.afterClosed().subscribe(() => {
      this.dialogRef.close();
      this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
        this.router.navigate([this.route]).then(() => {});
      });
    });
  }

  /**
   * Opens the dialog that contains corresponding information for the user's action
   * and reloads the page
   *
   * @param optionalStatus - Contract status(optional)
   */
  private openSuccessDialog(optionalStatus?: any) {
    const dialogRef = this.dialog.open(ContractDialogComponent, {
      width: '400px',
      data: optionalStatus ? optionalStatus : '',
    });

    dialogRef.afterClosed().subscribe(() => {
      this.dialogRef.close();
      this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
        this.router.navigate([this.route]).then(() => {});
      });
    });
  }

  disapproveSupervise(contract: Contract, message: any) {
    if (confirm('Are you sure?')) {
      // Disapprove the contract
      Promise.race([this.contractMgtService.approveContract(contract.contractId, contract.contractObj.supervise[0].id,
          JSON.stringify({
            approve: false,
            message: String(message),
          }))
          .toPromise()]).catch((err: HttpErrorResponse) => {
        if (Math.floor(err.status / 100) === 4) {
          Object.assign(this.errorMessage, err.error);
        }
      }).then(() => {
          if (Object.keys(this.errorMessage).length) {
              this.openFailDialog();
          } else {
              this.openSuccessDialog('DisapproveSupervise');
          }
      });
    }
  }

    /**
     * Rejects the examiner request
     *
     * @param contract - Contract object
     * @param message - Reject message
     */
    async rejectExamine(contract: any, message: any) {
        if (confirm('Are you sure?')) {
            let assessmentId: number;
            let examineId: number;
            assessmentId = 0;
            examineId = 0;
            const promiseAssessments = contract.assessment.map(assessment => {
                if (this.route === '/examine') {
                    if (assessment.examiner === JSON.parse(localStorage.getItem('srpmsUser')).id) {
                        assessmentId = assessment.id;
                        examineId = assessment.examineId;
                    }
                } else if (this.route === '/convene' && contract.status === 'Approved') {
                    if (assessment.template === 1) {
                        assessmentId = assessment.id;
                        examineId = assessment.examineId;
                    }
                }
            });
            await Promise.all(promiseAssessments).then(async () => {
                await this.contractMgtService.confirmExamine(contract.contractId, assessmentId, examineId,
                    JSON.stringify({
                        approve: false,
                        message: String(message),
                    })).toPromise().catch((err: HttpErrorResponse) => {
                    if (Math.floor(err.status / 100) === 4) {
                        Object.assign(this.errorMessage, err.error);
                    }
                }).then(() => {
                    if (Object.keys(this.errorMessage).length) {
                        this.openFailDialog();
                    } else {
                        this.openSuccessDialog('RejectExamine');
                    }
                });
            });
        }
    }
}
