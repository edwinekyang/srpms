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
                    (item.course_number === 'COMP2710' || item.course_number === 'COMP3710') ? 'special' :
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
                label: 'Course List',
                choices: this.courseDropdown,
                order: 2,
            }),

            new TextboxElement({
                key: 'projectSupervisor',
                label: 'PROJECT SUPERVISOR',
                value: 1,
                required: true,
                order: 3,
                flag: 'common'
            }),

            new RadioBoxElement({
                key: 'semester',
                label: 'COMMENCING SEMESTER*',
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
                flag: 'common',
                maxlength: 4
            }),

            new RadioBoxElement({
                key: 'duration',
                label: 'DURATION*',
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
                flag: 'common',
                maxlength: 80
            }),

            new TextareaElement({
                key: 'objectives',
                label: 'LEARNING OBJECTIVES',
                value: '',
                required: true,
                order: 12,
                flag: 'common',
                maxlength: 400
            }),

            new TextareaElement({
                key: 'description',
                label: 'PROJECT DESCRIPTION',
                value: '',
                required: true,
                order: 13,
                flag: 'common',
                maxlength: 800
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
                flag: 'special'
            }),

            new TextboxElement({
               key: 'assessment1',
               label: 'Assessment: Report',
               value: 1,
               required: true,
               order: 22,
               flag: 'project',
               disabled: true,
            }),

            new TextboxElement({
                key: 'assessment1Description',
                label: 'STYLE',
                value: '',
                required: false,
                order: 23,
                flag: 'project',
                placeholder: '(e.g. research report, software description, ...)',
            }),

            new TextboxElement({
                key: 'assessment1Description',
                label: 'STYLE',
                value: '',
                required: false,
                order: 24,
                flag: 'special',
            }),

            new TextboxElement({
                key: 'assessment1Mark',
                label: 'MARK',
                value: '',
                required: true,
                order: 25,
                flag: 'common',
                maxlength: 2
            }),

            new TextboxElement({
                key: 'assessment1Due',
                label: 'DUE DATE',
                value: '',
                required: true,
                order: 26,
                flag: 'common',
                placeholder: '(e.g. 2019-01-01)',
                maxlength: 10
            }),

            new TextboxElement({
                key: 'assessment1Examiner',
                label: 'EXAMINER',
                value: '',
                required: false,
                order: 27,
                flag: 'common'
            }),

            // For Section Divider
            new TextboxElement({
                order: 30
            }),

            new TextboxElement({
                key: 'assessment2',
                label: 'Assessment: Artefact',
                value: 2,
                required: true,
                order: 31,
                flag: 'project',
                disabled: true,
            }),

            new DropdownElement({
                key: 'assessment2',
                label: 'Assessment 2',
                choices: [
                    {key: 'Report', value: 1},
                    {key: 'Artefact', value: 2},
                    {key: 'Presentation', value: 3},
                ],
                order: 32,
                flag: 'special'
            }),

            new TextboxElement({
                key: 'assessment2Description',
                label: 'STYLE',
                value: '',
                required: false,
                order: 33,
                flag: 'project',
                placeholder: '(e.g. software, user interface, robot, ...)'
            }),

            new TextboxElement({
                key: 'assessment2Description',
                label: 'STYLE',
                value: '',
                required: false,
                order: 34,
                flag: 'special'
            }),

            new TextboxElement({
                key: 'assessment2Mark',
                label: 'MARK',
                value: '',
                required: true,
                order: 35,
                flag: 'common',
                maxlength: 2
            }),

            new TextboxElement({
                key: 'assessment2Due',
                label: 'DUE DATE',
                value: '',
                required: true,
                order: 36,
                flag: 'common',
                placeholder: '(e.g. 2019-01-01)',
                maxlength: 10
            }),

            new TextboxElement({
                key: 'assessment2Examiner',
                label: 'SUPERVISOR',
                value: '',
                required: true,
                order: 37,
                flag: 'project'
            }),

            new TextboxElement({
                key: 'assessment2Examiner',
                label: 'EXAMINER',
                value: '',
                required: false,
                order: 38,
                flag: 'special'
            }),

            // For Section Divider
            new TextboxElement({
                order: 40
            }),

            new TextboxElement({
                key: 'assessment3',
                label: 'Assessment: Presentation',
                value: 3,
                required: true,
                order: 41,
                flag: 'project',
                disabled: true,
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
                flag: 'special'
            }),

            new TextboxElement({
                key: 'assessment3Description',
                label: 'Style: Presentation',
                value: 'Presentation',
                required: true,
                order: 44,
                flag: 'project',
                disabled: true,
            }),

            new TextboxElement({
                key: 'assessment3Mark',
                label: '% of Mark: 10',
                value: 10,
                required: true,
                order: 45,
                flag: 'project',
                disabled: true
            }),

            new TextboxElement({
                key: 'assessment3Mark',
                label: 'MARK',
                value: '',
                required: true,
                order: 46,
                flag: 'special',
                maxlength: 2
            }),

            new TextboxElement({
                key: 'assessment3Due',
                label: 'DUE DATE',
                value: '',
                required: true,
                order: 47,
                flag: 'common',
                placeholder: '(e.g. 2019-01-01)',
                maxlength: 10
            }),

            new TextboxElement({
                key: 'assessment3Examiner',
                label: 'COURSE CONVENOR',
                value: '',
                required: true,
                order: 48,
                flag: 'project'
            }),


            new TextboxElement({
                key: 'assessment3Examiner',
                label: 'EXAMINER',
                value: '',
                required: false,
                order: 49,
                flag: 'special'
            }),

        ];

        return elements.sort((a, b) => a.order - b.order);
    }
}
