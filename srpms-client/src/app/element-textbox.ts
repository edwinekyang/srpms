import { ElementBase } from './element-base';

export class TextboxElement extends ElementBase<string> {
    controlType = 'textbox';
    type: string;

    constructor(options: any = {}) {
        super(options);
        this.type = options.type || '';
    }
}
