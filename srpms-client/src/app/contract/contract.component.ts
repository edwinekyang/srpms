import {Component, OnInit} from '@angular/core';
import { HttpErrorResponse } from '@angular/common/http';
import { ContractService, Course } from '../contract.service';
import { ElementService } from '../element.service';

@Component({
  selector: 'app-contract',
  templateUrl: './contract.component.html',
  styleUrls: ['./contract.component.scss'],
  providers: [
    ContractService,
    ElementService
  ]
})

export class ContractComponent implements OnInit {
  errorMessage: string;
  course: Course;
  elements: any[];

  constructor(
    public contractService: ContractService,
    public elementService: ElementService
  ) {
      this.elements = elementService.getElements();
  }

  ngOnInit() {
  }

  showCourses() {
    this.contractService.getCourses()
      .subscribe(
          (data: Course) => this.course = {
        id: data.id,
        course_number: data.course_number,
        name: data.name},
          error => {
            if (error instanceof HttpErrorResponse) {
              this.errorMessage = error.error.detail;
            }
          });
  }
}
