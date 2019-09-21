import { ElementBase } from './element-base';

export class RadioBoxElement extends ElementBase<string> {
    controlType = 'radiobox';
    choices: {key: string, value: string}[] = [];

    constructor(options: any = {}) {
        super(options);
        this.choices = options.choices || [];
    }
}
