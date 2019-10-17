/**
 * @fileoverview This file wraps the contract form and draws the contract page.
 * @author euiyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
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
    // Retrieves the list of form elements
    this.elements = this.elementService.getElements();

    // Filters the course dropdown only for the page initialisation
    this.elements.forEach((data: any) => {
      if (data.key === 'course') {
        this.courseElement.push(data);
      }
    });
  }

  ngOnInit() {}

  /**
   * Receives the flag from ContractFormComponent after the user has selected the course
   * and filters form element based on the received flag value (either 'project' or 'special')
   *
   * @param $event - Object that contains the flag and course value
   */
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
