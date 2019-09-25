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
