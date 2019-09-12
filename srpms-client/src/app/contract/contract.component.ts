import { Component, OnInit } from '@angular/core';
import { HttpErrorResponse} from '@angular/common/http';
import { ContractService, Course } from '../contract.service';

@Component({
  selector: 'app-contract',
  templateUrl: './contract.component.html',
  styleUrls: ['./contract.component.scss']
})

export class ContractComponent implements OnInit {
  errorMessage: string;

  // tslint:disable-next-line:variable-name
  constructor(
    public course: Course,
    public message: string,
    private contractService: ContractService,
    ) {
      this.errorMessage = message;
  }

  ngOnInit() {
  }

  showCourses() {
    this.contractService.getCourses()
      .subscribe(
          (data: Course) => this.course = {
        course_id: data.course_id,
        course_number: data.course_number,
        name: data.name},
          error => {
            if (error instanceof HttpErrorResponse) {
              this.errorMessage = error.error.detail;
            }
          });
  }
}
