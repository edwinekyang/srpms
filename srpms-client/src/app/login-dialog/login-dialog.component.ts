import { Component, Inject, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material';

import { AccountsService } from '../accounts.service';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { APIErrorResponse } from '../auth-interceptor.service';
import { HttpErrorResponse } from '@angular/common/http';

@Component({
  selector: 'app-login-dialog',
  templateUrl: './login-dialog.component.html',
  styleUrls: ['./login-dialog.component.scss']
})
export class LoginDialogComponent implements OnInit {
  errorMessage: string;

  loginForm = new FormGroup({
    username: new FormControl(''),
    password: new FormControl(''),
  }, [Validators.required, Validators.required]);

  constructor(
    public dialogRef: MatDialogRef<LoginDialogComponent>,
    @Inject(MAT_DIALOG_DATA) public data: string,
    private accountService: AccountsService) {

    this.errorMessage = data;
  }

  ngOnInit() {
  }

  login() {
    this.accountService.login(this.loginForm.value)
      .subscribe(() => {
        this.close();
      }, (error1: APIErrorResponse) => {
        if (error1 instanceof HttpErrorResponse) {
          if (Math.floor(error1.status / 100) === 4) {
            this.errorMessage = error1.error.detail;
          } else {
            this.errorMessage = error1.statusText;
          }
        }
        throw error1;
      });
  }

  close() {
    this.errorMessage = '';
    this.dialogRef.close();
  }
}
