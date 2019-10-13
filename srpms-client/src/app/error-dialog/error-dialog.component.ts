import {Component, Inject, OnInit} from '@angular/core';
import {MAT_DIALOG_DATA, MatDialogRef} from '@angular/material';
import {Router} from '@angular/router';

@Component({
  selector: 'app-error-dialog',
  templateUrl: './error-dialog.component.html',
  styleUrls: ['./error-dialog.component.scss']
})
export class ErrorDialogComponent implements OnInit {
  public route: string;
  public errorTitles = [];

  constructor(
      public dialogRef: MatDialogRef<ErrorDialogComponent>,
      @Inject(MAT_DIALOG_DATA) public data: any,
      private router: Router,
  ) {
    console.log(data);
    this.errorTitles = Object.keys(data);
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
