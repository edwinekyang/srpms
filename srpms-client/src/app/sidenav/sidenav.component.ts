/**
 * @fileoverview This file draws the side navigation bar based on the user's related contracts.
 * @author euikyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import {Component, OnInit} from '@angular/core';
import {ContractMgtService} from '../contract-mgt.service';
import {Observable} from 'rxjs';
import {AccountsService, SrpmsUser} from '../accounts.service';

export interface UserStatus {
  haveOwn: boolean;
  haveConvene: boolean;
  haveSupervise: boolean;
  haveExamine: boolean;
  haveNonformal: boolean;
}

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.component.html',
  styleUrls: ['./sidenav.component.scss'],
  providers: [ContractMgtService],
})

export class SidenavComponent implements OnInit {
  private userID: any;
  public userStatus: Observable<SrpmsUser>;
  public haveOwn: boolean;
  public haveConvene: boolean;
  public haveSupervise: boolean;
  public haveExamine: boolean;
  public haveNonformal: boolean;

  constructor(
      public contractMgtService: ContractMgtService,
      public accountService: AccountsService,
  ) {
  }

  ngOnInit() {
    if (localStorage.getItem('srpmsUser') !== 'undefined' &&
      localStorage.getItem('srpmsUser') !== null) {
      this.accountService.watchStorage().subscribe(data => {
        this.userID = JSON.parse(localStorage.getItem('srpmsUser')).id;
        this.userStatus = this.contractMgtService.getRelatedContracts(this.userID);
        this.contractMgtService.getRelatedContracts(this.userID).subscribe(user => {
          // @ts-ignore
          this.haveConvene = user.convene.length > 0;
          // @ts-ignore
          this.haveOwn = user.own.length > 0;
          // @ts-ignore
          this.haveSupervise = user.supervise.length > 0 && user.is_approved_supervisor;
          // @ts-ignore
          this.haveNonformal = user.supervise.length > 0 && !user.is_approved_supervisor;
          // @ts-ignore
          this.haveExamine = user.examine.length > 0;
        });
      });
    }
  }

}
