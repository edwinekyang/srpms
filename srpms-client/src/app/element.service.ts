/**
 * @fileoverview This file contains each element of the form.
 * @author euikyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 * @author Dajie Yang (u6513788) <dajie.yang@anu.edu.au>
 */
import { Injectable } from '@angular/core';

import { DropdownElement } from './element-dropdown';
import { ElementBase } from './element-base';
import { TextboxElement } from './element-textbox';
import { RadioBoxElement } from './element-radiobox';
import { TextareaElement } from './element-textarea';
import { ContractService } from './contract.service';
import { Course } from './reseach_mgt-objects';
import { UserElement } from './element-user';
import { AccountsService, SrpmsUser } from './accounts.service';
import { HttpErrorResponse } from '@angular/common/http';
import { DatepickerElement } from './element-datepicker';


@Injectable()
export class ElementService {
  constructor(public contractService: ContractService,
              private accountsService: AccountsService) {
  }

  private courseDropdown = [];
  private formalSupervisors = [];
  private courseConveners = [];
  private allUsers = [];

  // TODO: get from a remote source of contract metadata
  getElements() {
    this.contractService.getCourses().subscribe(
      courses => {
        courses.forEach((course: Course) => this.courseDropdown.push(
          {
            key: course.course_number + '(' + course.name + ')',
            value: course.id,
            flag: (course.course_number === 'COMP2710' || course.course_number === 'COMP3710') ? 'special' :
              'project'
          }));
      }
    );

    this.accountsService.getAllUsers().subscribe(
      users => {
        users.forEach((user: SrpmsUser) => this.allUsers.push(user));
      }
    );

    this.accountsService.getFormalSupervisors().subscribe(
      users => {
        users.forEach((user: SrpmsUser) => this.formalSupervisors.push(user));
      }
    );

    this.accountsService.getCourseConveners().subscribe(
      users => {
        users.forEach((user: SrpmsUser) => this.courseConveners.push(user));
      }
    );

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

      new UserElement({
        key: 'projectSupervisor',
        label: 'PROJECT SUPERVISOR',
        choices: this.formalSupervisors,
        required: true,
        order: 3,
        flag: 'common'
      }),

      new RadioBoxElement({
        key: 'semester',
        label: 'COMMENCING SEMESTER*',
        choices: [
          { key: 'S1', value: 1 },
          { key: 'S2', value: 2 }
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
          { key: '1 Semester', value: 1 },
          { key: '2 Semesters(12u courses only)', value: 2 }
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
          { key: 'Report', value: 1 },
          { key: 'Artefact', value: 2 },
          { key: 'Presentation', value: 3 },
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

      new DatepickerElement({
        key: 'assessment1Due',
        label: 'DUE DATE',
        value: '',
        required: false,
        order: 26,
        flag: 'common',
        placeholder: 'Choose a date',
      }),

      new UserElement({
        key: 'assessment1Examiner',
        label: 'EXAMINER',
        choices: this.allUsers,
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
          { key: 'Report', value: 1 },
          { key: 'Artefact', value: 2 },
          { key: 'Presentation', value: 3 },
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

      new DatepickerElement({
        key: 'assessment2Due',
        label: 'DUE DATE',
        value: '',
        required: false,
        order: 36,
        flag: 'common',
        placeholder: 'Choose a date',
      }),

      new UserElement({
        key: 'assessment2Examiner',
        label: 'EXAMINER',
        choices: this.allUsers,
        required: false,
        order: 37,
        flag: 'project'
      }),

      new UserElement({
        key: 'assessment2Examiner',
        label: 'EXAMINER',
        choices: this.allUsers,
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
          { key: 'Report', value: 1 },
          { key: 'Artefact', value: 2 },
          { key: 'Presentation', value: 3 },
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

      new DatepickerElement({
        key: 'assessment3Due',
        label: 'DUE DATE',
        value: '',
        required: false,
        order: 47,
        flag: 'common',
        placeholder: 'Choose a date',
      }),

      new UserElement({
        key: 'assessment3Examiner',
        label: 'COURSE CONVENOR',
        choices: this.courseConveners,
        required: true,
        order: 48,
        flag: 'project'
      }),


      new UserElement({
        key: 'assessment3Examiner',
        label: 'EXAMINER',
        choices: this.allUsers,
        required: false,
        order: 49,
        flag: 'special'
      }),

    ];

    return elements.sort((a, b) => a.order - b.order);
  }
}
