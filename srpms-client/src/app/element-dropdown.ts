import { ElementBase } from './element-base';

export class DropdownElement extends ElementBase<string> {
    controlType = 'dropdown';
    options: {key: string, value: string}[] = [];

    constructor(options: any = {}) {
        super(options);
        this.options = options.options || [];
    }
}
