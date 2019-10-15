/**
 * @fileoverview This file draws the header of the system.
 * @author dajie.yang@anu.edu.au (Dajie (Cooper) Yang)
 * @author euiyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import { Component, OnInit } from '@angular/core';
import { MatDialog } from '@angular/material';

import { LoginDialogComponent } from '../login-dialog/login-dialog.component';
import { AccountsService, SrpmsUser, ACC_SIG } from '../accounts.service';

@Component({
  selector: 'app-header',
  templateUrl: './header.component.html',
  styleUrls: ['./header.component.scss']
})
export class HeaderComponent implements OnInit {
  localUser: SrpmsUser;
  displayName: string;
  userInfo: string[];

  constructor(public dialog: MatDialog, public accountService: AccountsService) {
  }

  ngOnInit() {
    // Watch local storage and update info as it change
    this.accountService.getLocalUser().subscribe(user => {
      if (user) {
        this.localUser = user;
        if (user.first_name || user.last_name) {
          this.displayName = [user.first_name, user.last_name].join(' ');
        } else {
          this.displayName = user.username;
        }
        this.userInfo = [];
        if (user.uni_id) {
          this.userInfo.push(user.uni_id);
        }
        if (user.email) {
          this.userInfo.push(user.email);
        }
        if (user.expire_date) {
          this.userInfo.push('Expire on: ' + new Date(user.expire_date).getDate());
        }
      } else {
        this.clearInfo();
      }
    });
  }

  openLoginDialog(): void {
    this.dialog.open(LoginDialogComponent);
  }

  clearInfo(): void {
    this.localUser = null;
    this.displayName = null;
    this.userInfo = [];
  }
}
