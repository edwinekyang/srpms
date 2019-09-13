import { Component, Input } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { ElementBase } from '../element-base';

@Component({
  selector: 'app-contract-form-element',
  templateUrl: './contract-form-element.component.html'
})
export class ContractFormElementComponent {
  @Input() element: ElementBase<any>;
  @Input() form: FormGroup;
  get isValid() { return this.form.controls[this.element.key].valid; }
}
