/**
 * @fileoverview This file contains the services relevant to ContractFormComponent.
 * @author euikyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import { Injectable } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ElementBase } from './element-base';

@Injectable()
export class ContractFormControlService {
    constructor() { }

    toFormGroup(elements: ElementBase<any>[], flag: string) {
        const group: any = {};
        if (flag === 'course') {
            elements.forEach(element => {
                group[element.key] = (element.flag === 'course') ? new FormControl(element.value || '',
                    Validators.required) : new FormControl(element.value || '');
            });
        } else {
            elements.forEach(element => {
                group[element.key] = element.required ? new FormControl(element.value || '', Validators.required) :
                    new FormControl(element.value || '');
            });
        }
        return new FormGroup(group);
    }
}
