import { Component, Inject, Input, OnInit } from '@angular/core';
import { MAT_DIALOG_DATA, MatDialogRef } from '@angular/material';

import { AccountsService } from '../accounts.service';

@Component({
  selector: 'app-login-dialog',
  templateUrl: './login-dialog.component.html',
  styleUrls: ['./login-dialog.component.scss']
})
export class LoginDialogComponent implements OnInit {

  @Input() username: string;
  @Input() password: string;

  constructor(
    public dialogRef: MatDialogRef<LoginDialogComponent>,
    private accountService: AccountsService) {
  }

  ngOnInit() {
  }

  login() {
    this.accountService.login(this.username, this.password);
    this.dialogRef.close();
  }

  close() {
    this.dialogRef.close();
  }
}
