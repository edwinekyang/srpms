/**
 * @fileoverview This file draws the successful dialog from the actions.
 * @author euikyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import {Component, Inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material';
import {Router} from '@angular/router';

@Component({
  selector: 'app-contract-form-dialog',
  templateUrl: './contract-dialog.component.html',
  styleUrls: ['./contract-dialog.component.scss']
})
export class ContractDialogComponent implements OnInit {
  public route: string;

  constructor(
      public dialogRef: MatDialogRef<ContractDialogComponent>,
      @Inject(MAT_DIALOG_DATA) public data: any,
      private router: Router,
  ) {
    this.route = this.router.url;
  }

  ngOnInit() {}

  /**
   * Closes the dialog on click
   */
  onClick() {
    this.dialogRef.close();
  }

}
