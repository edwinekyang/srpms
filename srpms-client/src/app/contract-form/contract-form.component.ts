import { Component, Input, OnInit } from '@angular/core';
import { FormGroup } from '@angular/forms';
import { ElementBase } from '../element-base';
import { ContractFormControlService } from '../contract-form-control.service';

@Component({
  selector: 'app-contract-form',
  templateUrl: './contract-form.component.html',
  providers: [ ContractFormControlService ]
})
export class ContractFormComponent implements OnInit {

  @Input() elements: ElementBase<any>[] = [];
  form: FormGroup;
  payLoad = '';

  constructor(private cfcs: ContractFormControlService) {  }

  ngOnInit() {
    this.form = this.cfcs.toFormGroup(this.elements);
  }

  onSubmit() {
    this.payLoad = JSON.stringify(this.form.value);
  }
}
