import { ElementBase } from './element-base';

export class DropdownElement extends ElementBase<string> {
    controlType = 'dropdown';
    choices: {key: string, value: string}[] = [];

    constructor(options: any = {}) {
        super(options);
        this.choices = options.choices || [];
    }
}
