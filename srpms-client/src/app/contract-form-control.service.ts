import { Injectable } from '@angular/core';
import { FormControl, FormGroup, Validators } from '@angular/forms';
import { ElementBase } from './element-base';

@Injectable()
export class ContractFormControlService {
    constructor() { }

    toFormGroup(elements: ElementBase<any>[], flag: string) {
        let elementFlag: string;
        elementFlag = flag ? flag : 'course';
        const group: any = {};

        elements.forEach(element => {
            group[element.key] = element.required && (element.flag === 'common' || element.flag === elementFlag) ?
                new FormControl(element.value || '', Validators.required)
                : new FormControl(element.value || '');
        });
        return new FormGroup(group);
    }
}
