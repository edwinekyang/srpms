import { Injectable } from '@angular/core';

import { DropdownElement } from './element-dropdown';
import { ElementBase } from './element-base';
import { TextboxElement } from './element-textbox';
import { RadioBoxElement } from './element-radiobox';
import {TextareaElement} from './element-textarea';
import {ContractService, Course} from './contract.service';
import {HttpErrorResponse} from '@angular/common/http';


@Injectable()
export class ElementService {
    private course: Course[] = [];
    constructor(public contractService: ContractService) {
        this.showCourses();
    }

    errorMessage: string;
    private courseDropdown = [];

    showCourses() {
        this.contractService.getCourses()
            .subscribe(
                (data: Course[]) => {
                    this.course = data;
                    this.getElements();
                },
                error => {
                    if (error instanceof HttpErrorResponse) {
                        this.errorMessage = error.error.detail;
                    }
                });
    }

    // TODO: get from a remote source of question metadata
    getElements() {
        this.course.forEach((item) => {
            this.courseDropdown.push({key: item.course_number + '(' + item.name + ')', value: item.id
                , flag:
                    (item.course_number === 'COMP2710' || item.course_number === 'COMP3710') ? 'specialTopics' :
                    'project'});
        });

        let elements: ElementBase<any>[];
        elements = [

            // For Section Divider
            new TextboxElement({
                order: 1
            }),

            new DropdownElement({
                key: 'course',
                label: 'Course',
                choices: this.courseDropdown,
                order: 2,
            }),

            new TextboxElement({
                key: 'proejctSupervisor',
                label: 'PROJECT SUPERVISOR',
                value: 1,
                required: true,
                order: 3,
                flag: 'common'
            }),

            new RadioBoxElement({
                key: 'semester',
                label: 'COMMENCING SEMESTER',
                choices: [
                    {key: 'S1', value: 1},
                    {key: 'S2', value: 2}
                ],
                required: true,
                order: 4,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'year',
                label: 'YEAR',
                value: '',
                required: true,
                order: 5,
                placeholder: '(ex: 2019)',
                flag: 'common'
            }),

            new RadioBoxElement({
                key: 'duration',
                label: 'DURATION',
                choices: [
                    {key: '1 Semester', value: 1},
                    {key: '2 Semesters(12u courses only)', value: 2}
                ],
                required: true,
                order: 6,
                flag: 'project'
            }),

            // For Section Divider
            new TextboxElement({
                order: 10
            }),

            new TextareaElement({
                key: 'title',
                label: 'PROJECT TITLE',
                value: '',
                required: true,
                order: 11,
                flag: 'common'
            }),

            new TextareaElement({
                key: 'objectives',
                label: 'LEARNING OBJECTIVES',
                value: '',
                required: true,
                order: 12,
                flag: 'common'
            }),

            new TextareaElement({
                key: 'description',
                label: 'PROJECT DESCRIPTION',
                value: '',
                required: true,
                order: 13,
                flag: 'common'
            }),

            // For Section Divider
            new TextboxElement({
                order: 20
            }),

            new DropdownElement({
                key: 'assessment1',
                label: 'Assessment 1',
                choices: [
                    {key: 'Report', value: 1},
                    {key: 'Artefact', value: 2},
                    {key: 'Presentation', value: 3},
                ],
                order: 21,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment1Description',
                label: 'STYLE',
                value: '',
                required: false,
                order: 22,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment1Mark',
                label: 'MARK',
                value: '',
                required: true,
                order: 23,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment1Due',
                label: 'DUE DATE',
                value: '',
                required: true,
                order: 24,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment1Examiner',
                label: 'EXAMINER',
                value: '',
                required: false,
                order: 25,
                flag: 'common'
            }),

            // For Section Divider
            new TextboxElement({
                order: 30
            }),

            new DropdownElement({
                key: 'assessment2',
                label: 'Assessment 2',
                choices: [
                    {key: 'Report', value: 1},
                    {key: 'Artefact', value: 2},
                    {key: 'Presentation', value: 3},
                ],
                order: 31,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment2Description',
                label: 'STYLE',
                value: '',
                required: false,
                order: 32,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment2Mark',
                label: 'MARK',
                value: '',
                required: true,
                order: 33,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment2Due',
                label: 'DUE DATE',
                value: '',
                required: true,
                order: 34,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment2Examiner',
                label: 'SUPERVISOR',
                value: '',
                required: true,
                order: 35,
                flag: 'common'
            }),

            // For Section Divider
            new TextboxElement({
                order: 40
            }),

            new TextboxElement({
                key: 'assessment3',
                label: 'PRESENTATION',
                value: '3',
                required: true,
                order: 41,
                flag: 'project'
            }),

            new DropdownElement({
                key: 'assessment3',
                label: 'Assessment 3',
                choices: [
                    {key: 'Report', value: 1},
                    {key: 'Artefact', value: 2},
                    {key: 'Presentation', value: 3},
                ],
                order: 42,
                flag: 'special'
            }),

            new TextboxElement({
                key: 'assessment3Description',
                label: 'STYLE',
                value: '',
                required: false,
                order: 43,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment3Mark',
                label: 'MARK',
                value: '',
                required: true,
                order: 44,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment3Due',
                label: 'DUE DATE',
                value: '',
                required: true,
                order: 45,
                flag: 'common'
            }),

            new TextboxElement({
                key: 'assessment3Examiner',
                label: 'COURSE CONVENOR',
                value: '',
                required: true,
                order: 46,
                flag: 'common'
            }),

        ];

        return elements.sort((a, b) => a.order - b.order);
    }
}
