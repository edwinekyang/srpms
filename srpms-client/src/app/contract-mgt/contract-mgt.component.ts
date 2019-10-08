import {Component, OnInit} from '@angular/core';
import {HttpErrorResponse} from '@angular/common/http';
import {ContractService, Course} from '../contract.service';
import {ContractMgtService} from '../contract-mgt.service';
import {AccountsService, SrpmsUser} from '../accounts.service';
import {Router} from '@angular/router';
import {ContractDialogComponent} from '../contract-dialog/contract-dialog.component';
import {MatDialog} from '@angular/material';

export interface ContractList<T> {
    contractId: string;
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
    examineId: any;
    template: number;
    assessmentName: string;
    contract: number;
    due: string;
    weight: number;
    examiner: number;
    isAllExaminersApproved: boolean;
    examinerApprovalDate: string;
    additionalDescription: string;
}


@Component({
    selector: 'app-contract-mgt',
    templateUrl: './contract-mgt.component.html',
    styleUrls: ['./contract-mgt.component.scss'],
})


export class ContractMgtComponent implements OnInit {
    private errorMessage: string;
    public preContractList: ContractList<any>[] = [];
    public postContractList: ContractList<any>[] = [];
    private preList: number[] = [];
    private postList: number[] = [];
    public preAssessmentList: AssessmentList<any>[] = [];
    public postAssessmentList: AssessmentList<any>[] = [];
    public route: string;
    public courses: Course[] = [];

    constructor(
        public contractService: ContractService,
        private contractMgtService: ContractMgtService,
        public accountService: AccountsService,
        private router: Router,
        public dialog: MatDialog,
    ) {
        this.route = this.router.url;
    }

    ngOnInit() {
        this.initView().then();
    }

    /**
     * Initialises the view used by all types of user (Student, Supervisor, Examiner, Course Convener)
     * Pre-list here refers to contracts that hasn't been processed to the next stage for each corresponding user.
     * Post-list here refers to contracts that has been processed to the next stage for each corresponding user.
     * This function goes as following:
     * 1. Retrieves the pre-list
     * 2. Retrieves the assessments of the pre-list
     * 3. Re-arranges the pre-list information for the view
     * 4. Retrives the post-list
     * 5. Retrieves the assessments of the post-list
     * 6. Re-arranges the post-list information for the view
     */
    async initView() {
        // Pre-list
        this.getPreContractIds().then(
            async () => {
                await this.showAssessments(this.preList, 'pre');
                await this.contractService.getCourses().toPromise()
                    .then(async (courses: Course[]) => {
                        this.courses = courses;
                        await this.showContracts(this.preList, 'pre');
                    }, error => {
                        if (error instanceof HttpErrorResponse) {
                            this.errorMessage = error.error.detail;
                        }
                    });
            });

        // Post-list
        this.getPostContractIds().then(
            async () => {
                await this.showAssessments(this.postList, 'post');
                await this.contractService.getCourses().toPromise()
                    .then(async (courses: Course[]) => {
                        this.courses = courses;
                        await this.showContracts(this.postList, 'post');
                    }, error => {
                        if (error instanceof HttpErrorResponse) {
                            this.errorMessage = error.error.detail;
                        }
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
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPreList = data.supervise.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (contract.is_submitted && !contract.supervise[0].is_supervisor_approved) {
                                this.preList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPreList);
                });
        } else if (this.route === '/examine') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPreList = data.examine.map(async id => {
                        await this.contractMgtService.getAssessments(id).toPromise().then(async assessments => {
                            const promiseAssessments = assessments.map(assessment => {
                                if (assessment.assessment_examine[0].examiner ===
                                    JSON.parse(localStorage.getItem('srpmsUser')).id &&
                                    !assessment.assessment_examine[0].examiner_approval_date) {
                                    this.preList.push(id);
                                }
                            });
                            await Promise.all(promiseAssessments);
                        });
                    });
                    await Promise.all(promisesPreList);
                });
        } else if (this.route === '/submit') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPreList = data.own.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (!contract.is_submitted) {
                                this.preList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPreList);
                });
        } else if (this.route === '/convene') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisePreList = data.convene.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(async contract => {
                            if (contract.is_all_supervisors_approved && !contract.is_convener_approved) {
                                await this.contractMgtService.getAssessments(id).toPromise().then(async assessments => {
                                    let preFlag: boolean;
                                    preFlag = true;
                                    const promiseAssessments = assessments.map(assessment => {
                                        // Course convenor is one of the assessment examiner
                                        if (assessment.assessment_examine[0].examiner ===
                                            JSON.parse(localStorage.getItem('srpmsUser')).id &&
                                            !assessment.is_all_examiners_approved) {
                                            preFlag = preFlag ? preFlag || !assessment.is_all_examiners_approved : preFlag;
                                        // Other assessments that course convener is not the examiner
                                        } else {
                                            preFlag = preFlag ? assessment.is_all_examiners_approved : preFlag;
                                        }
                                    });
                                    await Promise.all(promiseAssessments).then(() => {
                                        if (preFlag) {
                                            this.preList.push(id);
                                        }
                                    });
                                });
                            }
                        });
                    });
                    await Promise.all(promisePreList);
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
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPostList = data.supervise.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (contract.is_submitted && contract.supervise[0].is_supervisor_approved) {
                                this.postList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPostList);
                });
        } else if (this.route === '/submit') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPostList = data.own.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(contract => {
                            if (contract.is_submitted) {
                                this.postList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisesPostList);
                });
        } else if (this.route === '/examine') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisesPostList = data.examine.map(async id => {
                        await this.contractMgtService.getAssessments(id).toPromise().then(async assessments => {
                            const promiseAssessments = assessments.map(assessment => {
                                if (assessment.assessment_examine[0].examiner ===
                                    JSON.parse(localStorage.getItem('srpmsUser')).id &&
                                    assessment.assessment_examine[0].examiner_approval_date) {
                                    this.postList.push(id);
                                }
                            });
                            await Promise.all(promiseAssessments);
                        });
                    });
                    await Promise.all(promisesPostList);
                });
        } else if (this.route === '/convene') {
            await this.contractMgtService.getOwnContracts(JSON.parse(localStorage.getItem('srpmsUser')).id).toPromise()
                .then(async data => {
                    const promisePostList = data.convene.map(async id => {
                        await this.contractMgtService.getContract(id).toPromise().then(async contract => {
                            if (contract.is_all_supervisors_approved && contract.is_all_assessments_approved) {
                                this.postList.push(id);
                            }
                        });
                    });
                    await Promise.all(promisePostList);
                });
        }
    }

    /**
     * Re-arrange the contract information for the view
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
     *
     * @param contractIdList - Contract ID List
     * @param type - Type flag (either 'pre' or 'post')
     */
    async showContracts(contractIdList: number[], type: string) {
        let assessmentList: any;
        const promiseContractIdList = contractIdList.map(async (contractId: number) => {
            await this.contractMgtService.getContract(contractId).toPromise()
                .then(async contract => {
                    await this.accountService.getUser(contract.owner).toPromise()
                        .then(async (student: SrpmsUser) => {
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
                                        this.preContractList.push({
                                            courseNumber: course.course_number,
                                            courseName: course.name,
                                            contractId: contract.id,
                                            studentId: student.uni_id,
                                            studentName: student.first_name + ' ' + student.last_name,
                                            title: contract.special_topics ?
                                                contract.special_topics.title :
                                                contract.individual_project.title,
                                            contractObj: contract,
                                            assessment: assessmentList,
                                            status: '',
                                        });
                                    } else if (type === 'post') {
                                        this.postContractList.push({
                                            courseNumber: course.course_number,
                                            courseName: course.name,
                                            contractId: contract.id,
                                            studentId: student.uni_id,
                                            studentName: student.first_name + ' ' + student.last_name,
                                            title: contract.special_topics ?
                                                contract.special_topics.title :
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
     *
     * @param contractIdList - Contract ID List
     * @param type - Type flag (either 'pre' or 'post')
     */
    async showAssessments(contractIdList: number[], type: string) {
        const promiseContractIdList = contractIdList.map(async id => {
            await this.contractMgtService.getAssessments(id).toPromise()
                .then(async assessments => {
                    const promiseAssessments = assessments.map(async assessment => {
                        if (type === 'pre') {
                            this.preAssessmentList.push({
                                id: assessment.id,
                                examineId: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].id : '',
                                template: assessment.template,
                                assessmentName: assessment.template_info.name,
                                contract: assessment.contract,
                                due: assessment.due,
                                weight: assessment.weight,
                                examiner: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].examiner : '',
                                isAllExaminersApproved: assessment.is_all_examiners_approved,
                                examinerApprovalDate: assessment.examiner_approval_date,
                                additionalDescription: assessment.additional_description,
                            });
                        } else if (type === 'post') {
                            this.postAssessmentList.push({
                                id: assessment.id,
                                examineId: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].id : '',
                                template: assessment.template,
                                assessmentName: assessment.template_info.name,
                                contract: assessment.contract,
                                due: assessment.due,
                                weight: assessment.weight,
                                examiner: assessment.assessment_examine[0] ?
                                    assessment.assessment_examine[0].examiner : '',
                                isAllExaminersApproved: assessment.is_all_examiners_approved,
                                examinerApprovalDate: assessment.examiner_approval_date,
                                additionalDescription: assessment.additional_description,
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
     * @param contractId - Contract ID
     */
    submit(contractId: any) {
        this.contractMgtService.updateSubmitted(contractId).subscribe(() => {
            this.openSuccessDialog();
        });
    }

    /**
     * Approves the supervise relation of the contract used by the contract supervisor
     * This function goes as following:
     * 1. Creates the examiner relation for the corresponding assessment of the contract
     * 2. Approves the contract
     * 3. Confirms supervisor's examiner role of the corresponding assessment
     * 4. Opens the dialog
     *
     * @param examinerId - Examiner's ID
     * @param contract - Contract object
     */
    async approveSupervise(examinerId: any, contract: any) {
        // Nominate the examiner
        const promiseNomination = contract.contractObj.assessment.map(async assessment => {
            if (assessment.template === 1) {
                await this.contractMgtService.addExamine(contract.contractId, assessment.id, JSON.stringify({
                    examiner: examinerId,
                }))
                    .toPromise().then(() => {

                    });
            }
        });

        await Promise.all(promiseNomination);

        // Approve the contract
        await this.contractMgtService.approveContract(contract.contractId, contract.contractObj.supervise[0].id,
            JSON.stringify({
                approve: true,
            }))
            .toPromise().then(() => {

            });

        // Confirm supervisor's examiner role of the one of the assessments
        const promiseConfirmExamine = contract.contractObj.assessment.map(async assessment => {
            if (assessment.template === 2) {
                await this.contractMgtService.confirmExamine(contract.contractId, assessment.id,
                    assessment.assessment_examine[0].id, JSON.stringify({
                        approve: true,
                    }))
                    .toPromise().then(() => {

                    });
            }
        });

        await Promise.all(promiseConfirmExamine).then(() => {
            this.openSuccessDialog();
        });

    }

    /**
     * Opens the dialog that contains corresponding information for the user's action
     * and reloads the page
     */
    private openSuccessDialog() {
        const dialogRef = this.dialog.open(ContractDialogComponent, {
            width: '400px',
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
     * @param contractId - Contract ID
     * @param assessments - Assessment list
     */
    async confirm(contractId: any, assessments: any) {
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
        await Promise.all(promiseAssessments).then(() => {
            this.contractMgtService.confirmExamine(contractId, assessmentId, examineId,
                JSON.stringify({
                    approve: true,
                })).subscribe(() => {
                this.openSuccessDialog();
            });
        });
    }

    /**
     * Finalises the contract
     * 1. Confirms the course convener's examiner role of the corresponding assessment
     * 2. Finalises the contract
     * 3. Opens the dialog
     *
     * @param contractId - Contract ID
     */
    async approveConvene(contractId: string) {
        // Confirm course convener's examiner's role first if any
        await this.contractMgtService.getAssessments(contractId).toPromise()
            .then(async assessments => {
                const promiseAssessments = assessments.map(async assessment => {
                    if (assessment.assessment_examine[0].examiner === JSON.parse(localStorage.getItem('srpmsUser')).id) {
                        await this.contractMgtService.confirmExamine(contractId, assessment.id, assessment.assessment_examine[0].id,
                            JSON.stringify({
                                approve: true,
                            })).toPromise().then(() => {

                        });
                    }
                });

                await Promise.all(promiseAssessments);
            });
        // Finalise the contract
        await this.contractMgtService.approveConvene(contractId, JSON.stringify({
            approve: true,
        })).toPromise().then(() => {
            this.openSuccessDialog();
        });
    }
}
