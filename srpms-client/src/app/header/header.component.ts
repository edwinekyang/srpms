import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material';

import { LoginDialogComponent } from '../login-dialog/login-dialog.component';
import { AccountsService } from '../accounts.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {

  constructor(public dialog: MatDialog, public accountService: AccountsService) {
  }

  ngOnInit() {
  }

  openLoginDialog(): void {
    this.dialog.open(LoginDialogComponent);
  }

  getDisplayName(): string {
    const localUser = this.accountService.getLocalUser();
    if (localUser.first_name) {
      return localUser.first_name;
    }
    return localUser.username;
  }
}
