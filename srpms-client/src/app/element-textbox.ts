import { ElementBase } from './element-base';

export class TextboxElement extends ElementBase<string> {
    controlType = 'textbox';
    type: string;
    disabled: boolean;
    placeholder: string;
    maxlength: number;

    constructor(options: any = {}) {
        super(options);
        this.type = options.type || '';
        this.disabled = !!options.disabled;
        this.placeholder = options.placeholder || '';
        this.maxlength = options.maxlength;
    }
}
