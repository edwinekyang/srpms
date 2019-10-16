import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material';

import { AccountsService } from '../accounts.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { APIErrorResponse } from '../auth-interceptor.service';
import { HttpErrorResponse } from '@angular/common/http';

/**
 * Login dialog logic, control login progress bar, send login request to API, show
 * error messages (if any).
 *
 * TODO: Solve circular dependency problem between this dialog and account service
 *
 * @author Dajie Yang (u6513788)
 */
@Component({
  selector: 'app-login-dialog',
  templateUrl: './login-dialog.component.html',
  styleUrls: [ './login-dialog.component.scss' ]
})
export class LoginDialogComponent implements OnInit {
  errorMessage: string;  // For displaying login error
  loginInProgress: boolean;  // Control whether to display login progress bar

  loginForm = new FormGroup({
    username: new FormControl(''),
    password: new FormControl(''),
  }, [ Validators.required, Validators.required ]);

  constructor(
    public dialogRef: MatDialogRef<LoginDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: string,
    private accountService: AccountsService) {

    this.errorMessage = data;
  }

  ngOnInit() {
    this.loginInProgress = false;
  }

  login() {
    this.loginInProgress = true;
    this.accountService.login(this.loginForm.value)
      .subscribe(() => {
        this.close();  // Close dialog on success
      }, (error1: APIErrorResponse) => {
        if (error1 instanceof HttpErrorResponse) {
          if (Math.floor(error1.status / 100) === 4) {
            // Display error message to dialog
            if (error1.error.detail) {
              this.errorMessage = error1.error.detail;
            } else {
              this.errorMessage = error1.statusText;
            }
          } else {
            this.errorMessage = error1.statusText;
          }
        }
        this.loginInProgress = false;
        throw error1;
      });
  }

  close() {
    this.dialogRef.close();
  }

  handleKeyEvent(event: KeyboardEvent) {
    if (event.key === 'Enter') {
      this.login();
    }
  }
}
