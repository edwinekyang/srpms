import {Component, EventEmitter, Input, OnInit, Output} from '@angular/core';
import { FormGroup } from '@angular/forms';

import { ElementBase } from '../element-base';

@Component({
  selector: 'app-contract-form-element',
  templateUrl: './contract-form-element.component.html',
  styleUrls: ['./contract-form-element.component.scss']
})
export class ContractFormElementComponent implements OnInit {

  @Input() element: ElementBase<any> = new ElementBase<any>();
  @Input() form: FormGroup;
  @Input() elementFlag: string;
  order: number;
  formFlag: string;
  courseValue: number;
  message = {};

  @Output() formFlagEvent = new EventEmitter<any>();

  constructor() {
  }

  ngOnInit(): void {
    this.order = this.element.order;
  }

  /**
   * Retrieves the error message for the form element
   * Currently only required validation exists.
   *
   * @param formControl - Form Control object
   */
  getErrorMessage(formControl) {
    return formControl.hasError('required') ? 'You must enter a value' : '';
  }

  /**
   * Sends the flag to ContractFormComponent
   */
  sendFormFlag() {
    this.element.choices.forEach((item) => {
      if (item.value === this.form.controls.course.value) {
        this.formFlag = item.flag;
        this.courseValue = item.value;
        this.message = {
          formFlag: this.formFlag,
          courseValue: item.value,
        };
        this.formFlagEvent.emit(this.message);
      }
    });
  }
}
