/**
 * @fileoverview This file decides attributes of textbox type element.
 * @author euikyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import { ElementBase } from './element-base';

export class DatepickerElement extends ElementBase<string> {
    controlType = 'datepicker';
    type: string;
    disabled: boolean;
    placeholder: string;

    constructor(options: any = {}) {
        super(options);
        this.type = options.type || '';
        this.disabled = !!options.disabled;
        this.placeholder = options.placeholder || '';
    }
}
