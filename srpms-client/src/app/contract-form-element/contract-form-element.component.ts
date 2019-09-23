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

  @Output() formFlagEvent = new EventEmitter<string>();

  get isValid() { return this.form.controls[this.element.key].valid; }
  constructor() {
  }
  ngOnInit(): void {
    this.order = this.element.order;
  }

  getErrorMessage(formControl) {
    return formControl.hasError('required') ? 'You must enter a value' : '';
  }

  sendFormFlag() {
    this.element.choices.forEach((item) => {
      if (item.value === this.form.controls.course.value) {
          this.formFlag = item.flag;
          this.formFlagEvent.emit(this.formFlag);
      }
    });
  }
}
