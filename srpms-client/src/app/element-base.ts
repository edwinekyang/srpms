/**
 * @fileoverview This file decides attributes of element base.
 * @author euikyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
export class ElementBase<T> {
  value: T;
  key: string;
  label: string;
  required: boolean;
  order: number;
  controlType: string;
  choices: any;
  type: any;
  flag: string;
  disabled: boolean;
  placeholder: string;
  maxlength: number;

    constructor(options: {
      value?: T,
      key?: string,
      label?: string,
      required?: boolean,
      order?: number,
      controlType?: string,
      flag?: string
    } = {}) {
      this.value = options.value;
      this.key = options.key || '';
      this.label = options.label || '';
      this.required = !!options.required;
      this.order = options.order === undefined ? 1 : options.order;
      this.controlType = options.controlType || '';
      this.flag = options.flag || '';
    }
}
