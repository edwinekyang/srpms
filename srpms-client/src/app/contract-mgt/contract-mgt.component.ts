/**
 * @fileoverview This file draws the contract management page.
 * @author euikyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import {Component, OnInit} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {ContractService} from '../contract.service';
import { Assessment, Contract, Course } from '../reseach_mgt-objects';
import {ContractMgtService} from '../contract-mgt.service';
import {AccountsService, SrpmsUser} from '../accounts.service';
import {Router} from '@angular/router';
import {ContractDialogComponent} from '../contract-dialog/contract-dialog.component';
import {MatDialog} from '@angular/material';
import {FormControl, FormGroup} from '@angular/forms';
import {ErrorDialogComponent} from '../error-dialog/error-dialog.component';
import {ContractMgtDialogComponent} from '../contract-mgt-dialog/contract-mgt-dialog.component';

export interface ContractList<T> {
    supervisorName?: Array<T>;
    contractId: number;
    studentName: string;
    studentId: string;
    title: string;
    contractObj: any;
    courseNumber: string;
    courseName: string;
    assessment: [];
    status: any;
}

export interface AssessmentList<T> {
    id: any;
    examineId: number;
    template: number;
    assessmentName: string;
    contract: number;
    due: string;
    weight: number;
    examiner: number;
    isAllExaminersApproved: boolean;
    examinerApprovalDate: string;
    additionalDescription: string;
    examinerName: string;
}


@Component({
    selector: 'app-contract-mgt',
    templateUrl: './contract-mgt.component.html',
    styleUrls: ['./contract-mgt.component.scss'],
})


export class ContractMgtComponent implements OnInit {
    private errorMessage = {};
    public preContractList: ContractList<any>[] = [];
    public postContractList: ContractList<any>[] = [];
    private preList: number[] = [];
    private postList: number[] = [];
    public preAssessmentList: AssessmentList<any>[] = [];
    public postAssessmentList: AssessmentList<any>[] = [];
    public route: string;
    public courses: Course[] = [];
    public examinerForm: FormGroup;
    public examinerFormValid: boolean;
    public isApprovedSupervisor = true;

    constructor(
        public contractService: ContractService,
        private contractMgtService: ContractMgtService,
        public accountService: AccountsService,
        private router: Router,
        public dialog: MatDialog,
    ) {
        this.route = this.router.url;
        this.examinerForm = new FormGroup({
            examiner1: new FormControl(''),
            examiner2: new FormControl(''),
            examiner3: new FormControl(''),
        });
        this.examinerForm.statusChanges.subscribe(() => {
            this.examinerFormValid = this.examinerForm.valid;
        });
    }

    ngOnInit() {
        this.initView().then(() => {

        });
    }

    /**
     * Initialises the view used by all types of user (Student, Supervisor, Examiner, Course Convener)
     * Pre-list here refers to contracts that hasn't been processed to the next stage for each corresponding user.
     * Post-list here refers to contracts that has been processed to the next stage for each corresponding user.
     * This function goes as following:
     * 1. Retrieves the pre-list
     * 2. Retrieves the assessments of the pre-list
     * 3. Re-arranges the pre-list information for the view
     * 4. Retrieves the post-list
     * 5. Retrieves the assessments of the post-list
     * 6. Re-arranges the post-list information for the view
     */
    async initView() {
        // Pre-list
        this.getPreContractIds().then(
            async () => {
                await this.showAssessments(this.preList, 'pre');
                await this.contractService.getCourses().toPromise().catch((err: HttpErrorResponse) => {
                    if (Math.floor(err.status / 100) === 4) {
                        Object.assign(this.errorMessage, err.error);
                    }
                })
                    .then(async (courses: Course[]) => {
                        this.courses = courses;
                        await this.showContracts(this.preList, 'pre');
                    });
            });

        // Post-list
        this.getPostContractIds().then(
            async () => {
                await this.showAssessments(this.postList, 'post');
                await this.contractService.getCourses().toPromise().catch((err: HttpErrorResponse) => {
                    if (Math.floor(err.status / 100) === 4) {
                        Object.assign(this.errorMessage, err.error);
                    }
                })
                    .then(async (courses: Course[]) => {
                        this.courses = courses;
                        await this.showContracts(this.postList, 'post');
                    });
            });
    }

    /**
     * Retrieves the pre-list
     * Based on the route, action is differentiated.
     * - '/submit'
     *   1. Retrieves the contract IDs that they own
     *   2. Retrieves the contract and select it if the contract has not been submitted
     *   3. Adds the contract ID to 'preList'
     *
     * - '/supervise'
     *   1. Retrieves the contract IDs that they supervise
     *   2. Retrieves the contract and select it which has following conditions:
     *      Contract has been submitted.
     *      Contract has not been approved by the contract supervisor.
     *   3. Adds the contract ID to 'preList'
     *
     * - '/examine'
     *   1. Retrieves the contract IDs that they examine
     *   2. Retrieves the assessments of the contract and select from them which have following conditions:
     *      Assessment has the same examiner ID with the user currently logged in,
     *      Corresponding assessment's 'examiner_appoval_date' is null.
     *   3. Adds the contract ID to 'preList'
     *
     * - '/convene'
     *   1. Retrieves the contracts IDs that they convene
     *   2. Retrieves the contract that has been approved by the contract supervisor
     *      and has not been finalised by the course convener
     *   3. Select the contract that all examiners' have been confirmed the request
     *      except the case the course convener is one of the examiners of the contract
     *      In this case, this contract ID is also added to 'preList'
     *      Confirmations of this examine relation will automatically be triggered
     *      by the system prior to they finalise the contract
     *   4. Adds the contract ID to 'preList'
     */
    async getPreContractIds() {
        if (this.route === '/supervise') {
            await this.contractMgtService.getRelatedContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async (data: any) => {
                    this.isApprovedSupervisor = data.is_approved_supervisor;
                    // @ts-ignore
                    const promisesPreList = data.supervise.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (contract.is_submitted && !contract.supervise[0].is_supervisor_approved) {
                                this.preList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPreList).catch((err: HttpErrorResponse) => {
                        if (Math.floor(err.status / 100) === 4) {
                            Object.assign(this.errorMessage, err.error);
                        }
                    });
                });
        } else if (this.route === '/nonformal') {
            await this.contractMgtService.getRelatedContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
              .then(async (data: any) => {
                  this.isApprovedSupervisor = data.is_approved_supervisor;
                  // @ts-ignore
                  const promisesPreList = data.supervise.map(async id => {
                      await this.contractMgtService.getContract(id).toPromise().then(contract => {
                          if (contract.is_submitted && contract.is_examiner_nominated && !contract.is_all_supervisors_approved) {
                              this.preList.push(id);
                          }
                      });
                  });
                  await Promise.all(promisesPreList).catch((err: HttpErrorResponse) => {
                      if (Math.floor(err.status / 100) === 4) {
                          Object.assign(this.errorMessage, err.error);
                      }
                  });
              });
        } else if (this.route === '/examine') {
            await this.contractMgtService.getRelatedContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    // @ts-ignore
                    const promisesPreList = data.examine.map(async id => {
                        await this.contractMgtService.getAssessments(id).toPromise().then(async assessments => {
                            const promiseAssessments = assessments.map(assessment => {
                                if (assessment.assessment_examine[0].examiner ===
                                    JSON.parse(localStorage.getItem('srpmsUser')).id &&
                                    !assessment.assessment_examine[0].examiner_approval_date) {
                                    this.preList.push(id);
                                }
                            });
                            await Promise.all(promiseAssessments).catch((err: HttpErrorResponse) => {
                                if (Math.floor(err.status / 100) === 4) {
                                    Object.assign(this.errorMessage, err.error);
                                }
                            });
                        });
                    });
                    await Promise.all(promisesPreList).catch((err: HttpErrorResponse) => {
                        if (Math.floor(err.status / 100) === 4) {
                            Object.assign(this.errorMessage, err.error);
                        }
                    });
                });
        } else if (this.route === '/submit') {
            await this.contractMgtService.getRelatedContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    // @ts-ignore
                    const promisesPreList = data.own.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (!contract.is_submitted) {
                                this.preList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPreList).catch((err: HttpErrorResponse) => {
                        if (Math.floor(err.status / 100) === 4) {
                            Object.assign(this.errorMessage, err.error);
                        }
                    });
                });
        } else if (this.route === '/convene') {
            await this.contractMgtService.getRelatedContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    // @ts-ignore
                    const promisePreList = data.convene.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(async contract => {
                            if (contract.is_submitted && !contract.is_convener_approved) {
                                this.preList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisePreList).catch((err: HttpErrorResponse) => {
                        if (Math.floor(err.status / 100) === 4) {
                            Object.assign(this.errorMessage, err.error);
                        }
                    });
                });
        }
    }

    /**
     * Retrieves the post-list
     * Based on the route, action is differentiated.
     * - '/submit'
     *   1. Retrieves the contract IDs that they own
     *   2. Retrieves the contract and select it if the contract has been submitted
     *   3. Adds the contract ID to 'postList'
     *
     * - '/supervise'
     *   1. Retrieves the contract IDs that they supervise
     *   2. Retrieves the contract and select it which has following conditions:
     *      Contract has been submitted.
     *      Contract has been approved by the contract supervisor.
     *   3. Adds the contract ID to 'postList'
     *
     * - '/examine'
     *   1. Retrieves the contract IDs that they examine
     *   2. Retrieves the assessments of the contract and select from them which have following conditions:
     *      Assessment has the same examiner ID with the user currently logged in,
     *      Corresponding assessment's 'examiner_appoval_date' has value.
     *   3. Adds the contract ID to 'postList'
     *
     * - '/convene'
     *   1. Retrieves the contracts IDs that they convene
     *   2. Retrieves the contract that has been approved by the contract supervisor
     *      and has been finalised by the course convener
     *   3. Adds the contract ID to 'preList'
     */
    async getPostContractIds() {
        if (this.route === '/supervise') {
            await this.contractMgtService.getRelatedContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    // @ts-ignore
                    const promisesPostList = data.supervise.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (contract.is_submitted && contract.supervise[0].is_supervisor_approved) {
                                this.postList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPostList).catch((err: HttpErrorResponse) => {
                        if (Math.floor(err.status / 100) === 4) {
                            Object.assign(this.errorMessage, err.error);
                        }
                    });
                });
        } else if (this.route === '/submit') {
            await this.contractMgtService.getRelatedContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    // @ts-ignore
                    const promisesPostList = data.own.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (contract.is_submitted) {
                                this.postList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPostList).catch((err: HttpErrorResponse) => {
                        if (Math.floor(err.status / 100) === 4) {
                            Object.assign(this.errorMessage, err.error);
                        }
                    });
                });
        }  else if (this.route === '/nonformal') {
            await this.contractMgtService.getRelatedContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
              .then(async (data: any) => {
                  this.isApprovedSupervisor = data.is_approved_supervisor;
                  // @ts-ignore
                  const promisesPreList = data.supervise.map(async id => {
                      await this.contractMgtService.getContract(id).toPromise().then(contract => {
                          if (contract.is_submitted && contract.is_all_supervisors_approved) {
                              this.postList.push(id);
                          }
                      });
                  });
                  await Promise.all(promisesPreList).catch((err: HttpErrorResponse) => {
                      if (Math.floor(err.status / 100) === 4) {
                          Object.assign(this.errorMessage, err.error);
                      }
                  });
              });
        } else if (this.route === '/examine') {
            await this.contractMgtService.getRelatedContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    // @ts-ignore
                    const promisesPostList = data.examine.map(async id => {
                        await this.contractMgtService.getAssessments(id).toPromise().then(async assessments => {
                            const promiseAssessments = assessments.map(assessment => {
                                if (assessment.assessment_examine[0].examiner ===
                                    JSON.parse(localStorage.getItem('srpmsUser')).id &&
                                    assessment.assessment_examine[0].examiner_approval_date) {
                                    this.postList.push(id);
                                }
                            });
                            await Promise.all(promiseAssessments).catch((err: HttpErrorResponse) => {
                                if (Math.floor(err.status / 100) === 4) {
                                    Object.assign(this.errorMessage, err.error);
                                }
                            });
                        });
                    });
                    await Promise.all(promisesPostList).catch((err: HttpErrorResponse) => {
                        if (Math.floor(err.status / 100) === 4) {
                            Object.assign(this.errorMessage, err.error);
                        }
                    });
                });
        } else if (this.route === '/convene') {
            await this.contractMgtService.getRelatedContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    // @ts-ignore
                    const promisePostList = data.convene.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(async contract => {
                            if (contract.is_all_supervisors_approved && contract.is_all_assessments_approved) {
                                this.postList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisePostList).catch((err: HttpErrorResponse) => {
                        if (Math.floor(err.status / 100) === 4) {
                            Object.assign(this.errorMessage, err.error);
                        }
                    });
                });
        }
    }

    /**
     * Re-arrange the contract information for the view
     * Contract has 5 stages in the perspective of the course convener
     * 1. Submitted - Submitted contract from the contract owner
     * 2. Nominated - Examiner for the report is nominated
     * 3. Approved - Contract is approved by the contract supervisor
     * 4. Confirmed - Examiner request for the report is confirmed by the examiner
     * 5. Finalised - Contract is finalised by the convener
     * These statuses are showed in the pre-list for the convener ('/convene')
     *
     * And has 3 stages in the perspective of the contract owner
     * 1. Submitted - Submitted contract from the owner
     * 2. Approved - Contract is approved by the supervisor
     * 3. Finalised - Contract is finalised by the convener
     * These statuses are showed in the post-list for the owner ('/submit')
     *
     * Whether the type is 'pre' or 'post', this function behaves differently.
     * 1. Retrieves the contract using contractIdList
     * 2. Retrieves the owner of the contract
     * 3. 'pre'
     *   - Select the assessment that has the same contract ID
     *   - Adds to 'preAssessmentList'
     *   - Select course that has the matching course ID with the contract
     *   - Re-arrange the contract information to 'preContractList'
     *
     * 3. 'post'
     *   - Select the assessment that has the same contract ID
     *   - Adds to 'postAssessmentList'
     *   - Select course that has the matching course ID with the contract
     *   - Re-arrange the contract information to 'postContractList'
     *
     * @param contractIdList - Contract ID List
     * @param type - Type flag (either 'pre' or 'post')
     */
    async showContracts(contractIdList: number[], type: string) {
        let assessmentList: any;
        const promiseContractIdList = contractIdList.map(async (contractId: number) => {
            await this.contractMgtService.getContract(contractId).toPromise()
                .then(async (contract: Contract) => {
                    await this.accountService.getUser(contract.owner).toPromise()
                        .then(async (student: SrpmsUser) => {
                            const supervisorName = [];
                            contract.supervise.map(async supervise => {
                                await this.accountService.getUser(supervise.supervisor).toPromise()
                                    .then((user: SrpmsUser) => {
                                        supervisorName.push(user.first_name + ' ' + user.last_name +
                                            (supervise.is_formal ? '(F)' : '(NF)'));
                                    });
                            });
                            assessmentList = [];
                            if (type === 'pre') {
                                this.preAssessmentList.forEach(assessment => {
                                    if (assessment.contract === contractId) {
                                        assessmentList.push(assessment);
                                    }
                                });
                            } else if (type === 'post') {
                                this.postAssessmentList.forEach(assessment => {
                                    if (assessment.contract === contractId) {
                                        assessmentList.push(assessment);
                                    }
                                });
                            }
                            const promisesCourses = this.courses.map(async course => {
                                if (course.id === contract.course) {
                                    if (type === 'pre') {
                                        let examineStatus: string;
                                        examineStatus = '';
                                        if (!contract.is_all_assessments_approved && contract.is_examiner_nominated) {
                                            examineStatus = 'Nominated';
                                        } else if (contract.is_all_assessments_approved) {
                                            examineStatus = 'Confirmed';
                                        }
                                        this.preContractList.push({
                                            supervisorName,
                                            courseNumber: course.course_number,
                                            courseName: course.name,
                                            contractId: contract.id,
                                            studentId: student.uni_id,
                                            studentName: student.first_name + ' ' + student.last_name,
                                            title: contract.special_topic ?
                                                contract.special_topic.title :
                                                contract.individual_project.title,
                                            contractObj: contract,
                                            assessment: assessmentList,
                                            status: examineStatus ?
                                                (examineStatus === 'Nominated' ?
                                                    contract.is_all_supervisors_approved ?
                                                        'Approved' : 'Nominated' :
                                                    examineStatus === 'Confirmed' && contract.is_convener_approved ? 'Finalised' :
                                                        'Confirmed') :
                                                (contract.is_all_supervisors_approved ? 'Approved' :
                                                    contract.is_submitted ? 'Submitted' : 'Draft'),
                                        });
                                    } else if (type === 'post') {
                                        this.postContractList.push({
                                            supervisorName,
                                            courseNumber: course.course_number,
                                            courseName: course.name,
                                            contractId: contract.id,
                                            studentId: student.uni_id,
                                            studentName: student.first_name + ' ' + student.last_name,
                                            title: contract.special_topic ?
                                                contract.special_topic.title :
                                                contract.individual_project.title,
                                            contractObj: contract,
                                            assessment: assessmentList,
                                            status: contract.is_convener_approved ? 'Finalised' :
                                                contract.is_all_supervisors_approved ? 'Approved' :
                                                    contract.is_submitted ? 'Submitted' : '',
                                        });
                                    }
                                }
                            });
                            await Promise.all(promisesCourses);
                        });
                });
        });
        await Promise.all(promiseContractIdList);
    }

    /**
     * Re-arrange the assessment information for the view
     * Whether the type is 'pre' or 'post', this function behaves differently.
     * 1. Retrieves the assessment relation of the contract
     * 2. 'pre'
     *   - Adds the assessment information to 'preAssessmentList'
     *
     * 3. 'post'
     *   - Adds the assessment information to 'postAssessmentList'
     *
     * @param contractIdList - Contract ID List
     * @param type - Type flag (either 'pre' or 'post')
     */
    async showAssessments(contractIdList: number[], type: string) {
        const promiseContractIdList = contractIdList.map(async id => {
            await this.contractMgtService.getAssessments(id).toPromise()
                .then(async assessments => {
                    const promiseAssessments = assessments.map(async (assessment: Assessment) => {
                        let examinerName: any;
                        examinerName = '';
                        if (assessment.assessment_examine[0]) {
                            const promiseExaminer = this.accountService.getUser(assessment.assessment_examine[0].examiner).toPromise();
                            await Promise.race([promiseExaminer]).then(result => {
                                examinerName = result.first_name + ' ' + result.last_name;
                            });
                        }
                        if (type === 'pre') {
                            this.preAssessmentList.push({
                                id: assessment.id,
                                examineId: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].id : null,
                                template: assessment.template,
                                assessmentName: assessment.template_info.name,
                                contract: assessment.contract,
                                due: assessment.due,
                                weight: assessment.weight,
                                examiner: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].examiner : null,
                                isAllExaminersApproved: assessment.is_all_examiners_approved,
                                examinerApprovalDate: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].examiner_approval_date : '',
                                additionalDescription: assessment.additional_description,
                                examinerName,
                            });
                        } else if (type === 'post') {
                            this.postAssessmentList.push({
                                id: assessment.id,
                                examineId: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].id : null,
                                template: assessment.template,
                                assessmentName: assessment.template_info.name,
                                contract: assessment.contract,
                                due: assessment.due,
                                weight: assessment.weight,
                                examiner: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].examiner : null,
                                isAllExaminersApproved: assessment.is_all_examiners_approved,
                                examinerApprovalDate: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].examiner_approval_date : '',
                                additionalDescription: assessment.additional_description,
                                examinerName,
                            });
                        }
                    });
                    await Promise.all(promiseAssessments);
                }, error => {
                    if (error instanceof HttpErrorResponse) {
                        this.errorMessage = error.error.detail;
                    }
                });
        });

        await Promise.all(promiseContractIdList);
    }

    /**
     * Submits the contract used by the contract owner
     *
     * @param contract - Contract Object
     */
    async submit(contract: any) {
        if (confirm('Are you sure?')) {
            await this.contractMgtService.updateSubmitted(contract.contractId).toPromise().catch((err: HttpErrorResponse) => {
                if (Math.floor(err.status / 100) === 4) {
                    Object.assign(this.errorMessage, err.error);
                }
            });
            if (Object.keys(this.errorMessage).length) {
                this.openFailDialog();
            } else {
                this.openSuccessDialog(contract.status);
            }
        }
    }

    /**
     * Approves the supervise relation of the contract used by the contract supervisor
     * This function goes as following:
     * 1. Approves the contract
     * 2. Confirms supervisor's examiner role of the corresponding assessment
     * 3. Opens the dialog
     *
     * @param contract - Contract object
     */
    async approveSupervise(contract: any) {
        if (confirm('Are you sure?')) {
            // Approve the contract
            const promiseApproveSupervise = async () => {
                await this.asyncForEach(contract.contractObj.supervise, async (supervise) => {
                    if ((JSON.parse(localStorage.getItem('srpmsUser')).id === supervise.supervisor &&
                      !supervise.is_supervisor_approved) || (this.route === '/convene')) {
                        await this.contractMgtService.approveContract(contract.contractId, supervise.id,
                          JSON.stringify({
                              approve: true,
                          })).toPromise().catch((err: HttpErrorResponse) => {
                            if (Math.floor(err.status / 100) === 4) {
                                Object.assign(this.errorMessage, err.error);
                            }
                        });
                    }
                });
            };
            await promiseApproveSupervise().then(() => {
                if (Object.keys(this.errorMessage).length) {
                    this.openFailDialog();
                } else {
                    if (this.isApprovedSupervisor) {
                        this.openSuccessDialog('ApproveSupervise');
                    } else {
                        this.openSuccessDialog('ConfirmSupervise');
                    }
                }
            });
        }
    }

    /**
     * Opens the dialog that contains corresponding information for the user's action
     * and reloads the page
     *
     * @param optionalStatus - Contract status(optional)
     */
    private openSuccessDialog(optionalStatus?: any) {
        const dialogRef = this.dialog.open(ContractDialogComponent, {
            width: '400px',
            data: optionalStatus ? optionalStatus : '',
        });

        dialogRef.afterClosed().subscribe(() => {
            this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
                this.router.navigate([this.route]).then(() => {});
            });
        });
    }

    public openActionDialog(contract: any, action: any) {
        if (action === 'nominateNonformalSupervisor') {
            if (confirm('Are you sure you want to nominate non-formal supervisor?')) {
                Object.assign(contract, {action});
                const dialogRef = this.dialog.open(ContractMgtDialogComponent, {
                    width: '400px',
                    data: contract,
                });
            }
        } else {
            Object.assign(contract, {action});
            const dialogRef = this.dialog.open(ContractMgtDialogComponent, {
                width: '400px',
                data: contract,
            });
        }
    }

    /**
     * Opens the dialog to notify the user's action has been failed
     * and reloads the page
     */
    private openFailDialog() {
        const dialogRef = this.dialog.open(ErrorDialogComponent, {
            width: '400px',
            data:  this.errorMessage,
        });

        dialogRef.afterClosed().subscribe(() => {
            this.router.navigateByUrl('/', { skipLocationChange: true }).then(() => {
                this.router.navigate([this.route]).then(() => {});
            });
        });
    }

    /**
     * Confirms the examiner request used by the examiner
     * 1. Select the assessment object that has the same examiner ID with the user ID currently logged in
     * 2. Confirms the examine relation of the assessment
     * 3. Opens the dialog
     *
     * @param contract - Contract object
     * @param assessments - Assessment list
     */
    async confirmExamine(contract: any, assessments?: any) {
        if (confirm('Are you sure?')) {
            if (this.route === '/examine') {
                let assessmentId: number;
                let examineId: number;
                assessmentId = 0;
                examineId = 0;
                const promiseAssessments = assessments.map(assessment => {
                    if (assessment.examiner === JSON.parse(localStorage.getItem('srpmsUser')).id) {
                        assessmentId = assessment.id;
                        examineId = assessment.examineId;
                    }
                });
                await Promise.all(promiseAssessments).then(async () => {
                    await this.contractMgtService.confirmExamine(contract.contractId, assessmentId, examineId,
                        JSON.stringify({
                            approve: true,
                        })).toPromise().catch((err: HttpErrorResponse) => {
                        if (Math.floor(err.status / 100) === 4) {
                            Object.assign(this.errorMessage, err.error);
                        }
                    }).then(() => {
                        if (Object.keys(this.errorMessage).length) {
                            this.openFailDialog();
                        } else {
                            this.openSuccessDialog('ConfirmExamine');
                        }
                    });
                });
            } else if (this.route === '/convene' && !contract.isAllExaminersApproved) {
                await this.contractMgtService.confirmExamine(contract.contract, contract.id, contract.examineId,
                    JSON.stringify({
                        approve: true,
                    })).toPromise().catch((err: HttpErrorResponse) => {
                    if (Math.floor(err.status / 100) === 4) {
                        Object.assign(this.errorMessage, err.error);
                    }
                }).then(() => {
                    if (Object.keys(this.errorMessage).length) {
                        this.openFailDialog();
                    } else {
                        this.openSuccessDialog('ConfirmExamine');
                    }
                });
            }
        }
    }

    /**
     * Finalises the contract used by the course convener
     * 1. Confirms the course convener's examiner role of the corresponding assessment
     * 2. Finalises the contract
     * 3. Opens the dialog
     *
     * @param contract - Contract Object
     */
    async approveConvene(contract: any) {
        if (confirm('Are you sure?')) {
            // Confirm course convener's examiner's role first if any
            await this.contractMgtService.getAssessments(contract.contractId).toPromise()
                .then(async assessments => {
                    const promiseAssessments = assessments.map(async assessment => {
                        if (assessment.assessment_examine[0].examiner === JSON.parse(localStorage.getItem('srpmsUser')).id) {
                            await this.contractMgtService.confirmExamine(
                                contract.contractId, assessment.id, assessment.assessment_examine[0].id,
                                JSON.stringify({
                                    approve: true,
                                })).toPromise().then(() => {

                            });
                        }
                    });

                    await Promise.all(promiseAssessments);
                });
            // Finalise the contract
            await this.contractMgtService.approveConvene(contract.contractId, JSON.stringify({
                approve: true,
            })).toPromise().catch((err: HttpErrorResponse) => {
                if (Math.floor(err.status / 100) === 4) {
                    Object.assign(this.errorMessage, err.error);
                }
            }).then(() => {
                this.openSuccessDialog('ApproveConvene');
            });
        }
    }

    /**
     * Nominates the examiner used by course convener
     *
     * @param contract - Contract object
     */
    async nominateExaminer(contract: any) {
        if (confirm('Are you sure?')) {
            // Nominate the examiner
            if (contract.status !== 'Nominated') {
                const promiseAssessment = contract.assessment.map(async assessment => {
                    if (this.examinerForm.value['examiner' + assessment.template]) {
                        const promiseAdd = this.contractMgtService.addExamine(contract.contractId, assessment.id, JSON.stringify({
                            examiner: this.examinerForm.value['examiner' + assessment.template],
                        })).toPromise();
                        await Promise.race([promiseAdd]).catch((err: HttpErrorResponse) => {
                            if (Math.floor(err.status / 100) === 4) {
                                Object.assign(this.errorMessage, err.error);
                            }
                        });
                    }
                });
                await Promise.all(promiseAssessment).catch((err: HttpErrorResponse) => {
                    if (Math.floor(err.status / 100) === 4) {
                        Object.assign(this.errorMessage, err.error);
                    }
                });
                if (Object.keys(this.errorMessage).length) {
                    this.openFailDialog();
                } else {
                    this.openSuccessDialog(contract.status);
                }
            }
        }
    }

    async delete(contract: any) {
        if (confirm('Are you sure?')) {
            await this.contractMgtService.deleteContract(contract.contractId).toPromise().catch((err: HttpErrorResponse) => {
                if (Math.floor(err.status / 100) === 4) {
                    Object.assign(this.errorMessage, err.error);
                }
            });
            if (Object.keys(this.errorMessage).length) {
                this.openFailDialog();
            } else {
                this.openSuccessDialog(contract.status + 'Deleted');
            }
        }
    }

    public async asyncForEach(array, callback) {
        for (let index = 0; index < array.length; index++) {
            await callback(array[index], index, array);
        }
    }
}
