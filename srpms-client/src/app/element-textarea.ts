/**
 * @fileoverview This file decides attributes of textarea type element.
 * @author euiyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import { ElementBase } from './element-base';

export class TextareaElement extends ElementBase<string> {
    controlType = 'textarea';
    type: string;
    maxlength: number;

    constructor(options: any = {}) {
        super(options);
        this.type = options.type || '';
        this.maxlength = options.maxlength;
    }
}
