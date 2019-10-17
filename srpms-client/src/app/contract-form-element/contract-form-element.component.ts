/**
 * @fileoverview This file draws each element of the form.
 * @author euikyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import { Component, EventEmitter, Input, OnInit, Output } from '@angular/core';
import { FormGroup } from '@angular/forms';

import { ElementBase } from '../element-base';
import { SrpmsUser } from '../accounts.service';
import { Observable } from 'rxjs';
import { map, startWith } from 'rxjs/operators';

@Component({
  selector: 'app-contract-form-element',
  templateUrl: './contract-form-element.component.html',
  styleUrls: [ './contract-form-element.component.scss' ]
})
export class ContractFormElementComponent implements OnInit {

  @Input() element: ElementBase<any> = new ElementBase<any>();
  @Input() form: FormGroup;
  @Input() elementFlag: string;
  order: number;
  formFlag: string;
  courseValue: number;
  message = {};
  filteredOptions: Observable<SrpmsUser[]>;

  @Output() formFlagEvent = new EventEmitter<any>();

  constructor() {
  }

  ngOnInit(): void {
    this.order = this.element.order;
    if (this.element.controlType === 'users') {
      this.filteredOptions = this.form.controls[this.element.key].valueChanges
        .pipe(
          startWith(''),
          map(value => typeof value === 'string' ? value : value.display_name),
          map(name => name ? this._filter(name) : this.element.choices.slice())
        );
    }
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

  userDisplayFn(user?: SrpmsUser): string | undefined {
    return user ? user.display_name + ' (' + user.uni_id + ')' : undefined;
  }

  private _filter(name: string): SrpmsUser[] {
    const filterValue = name.toLocaleLowerCase();
    return this.element.choices.filter(option => option.display_name.toLowerCase().indexOf(filterValue) === 0);
  }
}
