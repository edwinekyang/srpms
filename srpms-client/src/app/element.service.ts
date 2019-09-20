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
                    {key: 'COMP8750', value: '1'},
                ],
                order: 1
            }),

            new TextboxElement({
                key: 'proejctSupervisor',
                label: 'PROJECT SUPERVISOR',
                value: 1,
                required: true,
                order: 4
            }),

            new TextboxElement({
                key: 'semester',
                label: 'SEMESTER',
                value: '',
                required: true,
                order: 6
            }),

            new TextboxElement({
                key: 'year',
                label: 'YEAR',
                value: '',
                required: true,
                order: 7
            }),

            new TextboxElement({
                key: 'duration',
                label: 'DURATION',
                value: '',
                required: true,
                order: 8
            }),

            new TextboxElement({
                key: 'title',
                label: 'PROJECT TITLE',
                value: '',
                required: true,
                order: 9
            }),

            new TextboxElement({
                key: 'objectives',
                label: 'LEARNING OBJECTIVES',
                value: '',
                required: true,
                order: 10
            }),

            new TextboxElement({
                key: 'description',
                label: 'PROJECT DESCRIPTION',
                value: '',
                required: true,
                order: 11
            }),

            new DropdownElement({
                key: 'assessment1',
                label: 'Assessment1',
                choices: [
                    {key: 'Report', value: 1},
                    {key: 'Artefact', value: 2},
                    {key: 'Presentation', value: 3},
                ],
                order: 12
            }),

            new TextboxElement({
                key: 'assessment1Description',
                label: 'STYLE',
                value: '',
                required: false,
                order: 13
            }),

            new TextboxElement({
                key: 'assessment1Mark',
                label: 'MARK',
                value: '',
                required: true,
                order: 14
            }),

            new TextboxElement({
                key: 'assessment1Due',
                label: 'DUE DATE',
                value: '',
                required: true,
                order: 15
            }),

            new TextboxElement({
                key: 'assessment1Examiner',
                label: 'EXAMINER',
                value: '',
                required: false,
                order: 16
            }),

            new DropdownElement({
                key: 'assessment2',
                label: 'Assessment2',
                choices: [
                    {key: 'Report', value: 1},
                    {key: 'Artefact', value: 2},
                    {key: 'Presentation', value: 3},
                ],
                order: 17
            }),

            new TextboxElement({
                key: 'assessment2Description',
                label: 'STYLE',
                value: '',
                required: false,
                order: 18
            }),

            new TextboxElement({
                key: 'assessment2Mark',
                label: 'MARK',
                value: '',
                required: true,
                order: 19
            }),

            new TextboxElement({
                key: 'assessment2Due',
                label: 'DUE DATE',
                value: '',
                required: true,
                order: 20
            }),

            new TextboxElement({
                key: 'assessment2Examiner',
                label: 'SUPERVISOR',
                value: '',
                required: true,
                order: 21
            }),

            new TextboxElement({
                key: 'assessment3',
                label: 'PRESENTATION',
                value: '3',
                required: true,
                order: 22
            }),

            new TextboxElement({
                key: 'assessment3Description',
                label: 'STYLE',
                value: '',
                required: false,
                order: 23
            }),

            new TextboxElement({
                key: 'assessment3Mark',
                label: 'MARK',
                value: '10',
                required: true,
                order: 24
            }),

            new TextboxElement({
                key: 'assessment3Due',
                label: 'DUE DATE',
                value: '',
                required: true,
                order: 25
            }),

            new TextboxElement({
                key: 'assessment3Examiner',
                label: 'COURSE CONVENOR',
                value: 1,
                required: true,
                order: 26
            }),

        ];

        return elements.sort((a, b) => a.order - b.order);
    }
}
