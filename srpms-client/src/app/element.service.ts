import { Injectable } from '@angular/core';

import { DropdownElement } from './element-dropdown';
import { ElementBase } from './element-base';
import { TextboxElement } from './element-textbox';

@Injectable()
export class ElementService {

    // TODO: get from a remote source of question metadata
    // TODO: make asynchronous
    getElements() {

        let elements: ElementBase<any>[];
        elements = [

            new DropdownElement({
                key: 'course',
                label: 'Course',
                choices: [
                    {key: 'COMP8750', value: 'COMP8750'},
                ],
                order: 3
            }),

            new TextboxElement({
                key: 'firstName',
                label: 'First name',
                value: 'Edwin',
                required: true,
                order: 1
            }),

            new TextboxElement({
                key: 'emailAddress',
                label: 'Email',
                type: 'email',
                order: 2
            })
        ];

        return elements.sort((a, b) => a.order - b.order);
    }
}
