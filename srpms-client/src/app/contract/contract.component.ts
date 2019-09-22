import {Component, OnInit} from '@angular/core';
import { ContractService, Course } from '../contract.service';
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
  course: Course[] = [];
  elements: ElementBase<any>[] = [];

  constructor(
    public elementService: ElementService
  ) {
    this.elements = this.elementService.getElements();
    console.log(this.elements);
  }

  ngOnInit() {

  }
}
