import { ElementBase } from './element-base';
import { SrpmsUser } from './accounts.service';

export class UserElement extends ElementBase<string> {
  controlType = 'users';
  choices: SrpmsUser[];

  constructor(options: any = {}) {
    super(options);
    this.choices = options.choices || [];
  }
}
