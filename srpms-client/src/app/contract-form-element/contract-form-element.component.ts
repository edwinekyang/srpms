import { Component, Input, OnInit } from '@angular/core';
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
  order: number;
  get isValid() { return this.form.controls[this.element.key].valid; }
  constructor() {
  }
  ngOnInit(): void {
    this.order = this.element.order;
  }

  getErrorMessage(formContorl) {
    return formContorl.hasError('required') ? 'You must enter a value' : '';
  }
}
