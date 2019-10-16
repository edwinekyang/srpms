/**
 * @fileoverview This file draws the side navigation bar based on the user's related contracts.
 * @author euiyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import { Component, OnInit } from '@angular/core';
import {ContractMgtService} from '../contract-mgt.service';

@Component({
  selector: 'app-sidenav',
  templateUrl: './sidenav.component.html',
  styleUrls: ['./sidenav.component.scss'],
  providers: [ContractMgtService],
})

export class SidenavComponent implements OnInit {
  private userID: any;
  public haveOwn: boolean;
  public haveConvene: boolean;
  public haveSupervise: boolean;
  public haveExamine: boolean;

  constructor(
      public contractMgtService: ContractMgtService,
  ) {
    if (JSON.parse(localStorage.getItem('srpmsUser'))) {
      this.userID = JSON.parse(localStorage.getItem('srpmsUser')).id;
      contractMgtService.getRelatedContracts(this.userID).subscribe(user => {
        // @ts-ignore
        this.haveConvene = user.convene.length > 0;
        // @ts-ignore
        this.haveOwn = user.own.length > 0;
        // @ts-ignore
        this.haveSupervise = user.supervise.length > 0;
        // @ts-ignore
        this.haveExamine = user.examine.length > 0;
      });
    }
  }

  ngOnInit() {
  }

}
