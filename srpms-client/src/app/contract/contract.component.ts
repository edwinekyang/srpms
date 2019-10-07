import {Component, OnInit} from '@angular/core';
import { ContractService } from '../contract.service';
import { ElementService } from '../element.service';
import {ElementBase} from '../element-base';

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
  elements: ElementBase<any>[] = [];
  formFlag: string;
  filteredElements: ElementBase<any>[] = [];
  courseElement: ElementBase<any>[] = [];
  courseValue: string;

  constructor(
    public elementService: ElementService
  ) {
    this.elements = this.elementService.getElements();
    this.elements.forEach((data: any) => {
      if (data.key === 'course') {
        this.courseElement.push(data);
      }
    });
  }

  ngOnInit() {

  }

  receiveFormFlag($event) {
    this.filteredElements = [];
    this.formFlag = $event.formFlag;
    this.courseValue = $event.courseValue;
    this.elements.forEach((element: any) => {
      if (element.flag === 'common' || element.flag === this.formFlag || element.flag === '') {
        this.filteredElements.push(element);
      }
    });
  }
}
