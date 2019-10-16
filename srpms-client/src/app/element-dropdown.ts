/**
 * @fileoverview This file decides attributes of dropdown type element.
 * @author euiyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import { ElementBase } from './element-base';

export class DropdownElement extends ElementBase<string> {
    controlType = 'dropdown';
    choices: {key: string, value: string}[] = [];

    constructor(options: any = {}) {
        super(options);
        this.choices = options.choices || [];
    }
}
