import { ElementBase } from './element-base';

export class TextareaElement extends ElementBase<string> {
    controlType = 'textarea';
    type: string;

    constructor(options: any = {}) {
        super(options);
        this.type = options.type || '';
    }
}
