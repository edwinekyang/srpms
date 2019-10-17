/**
 * @fileoverview This file decides attributes of radiobox type element.
 * @author euikyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import { ElementBase } from './element-base';

export class RadioBoxElement extends ElementBase<string> {
    controlType = 'radiobox';
    choices: {key: string, value: string}[] = [];

    constructor(options: any = {}) {
        super(options);
        this.choices = options.choices || [];
    }
}
