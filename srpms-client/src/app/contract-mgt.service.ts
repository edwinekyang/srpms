/**
 * @fileoverview This file contains the services relevant to ContractMgtComponent.
 * @author euikyum.yang@anu.edu.au (Euikyum (Edwin) Yang)
 */
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { API_URL } from './api-url';
import { Assessment, AssessmentExamine, Contract, Supervise } from './reseach_mgt-objects';
import { SrpmsUser } from './accounts.service';

@Injectable({
  providedIn: 'root'
})
export class ContractMgtService {
  private API_URL = API_URL;

  constructor(
    private http: HttpClient,
  ) {
  }

  public httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json',
    })
  };

  private static log(message: string) {
    console.log(`ContractMgt Service: ${message}`);
  }

  /**
   * Retrieves the supervise relation of the contract
   *
   * @param contractId - Contract ID
   */
  getSupervise(contractId: number): Observable<Supervise[]> {
    return this.http.get<Supervise[]>(`${this.API_URL}research_mgt/contracts/${contractId}/supervise/`, this.httpOptions)
      .pipe(
        catchError(this.handleError<Supervise[]>('getSupervise'))
      );
  }

  /**
   * Retrieves the assessment relation list of the contract
   *
   * @param contractId - Contract ID
   */
  getAssessments(contractId: number): Observable<Assessment[]> {
    return this.http.get<Assessment[]>(`${this.API_URL}research_mgt/contracts/${contractId}/assessments/`, this.httpOptions);
    /*.pipe(
        catchError(this.handleError<any[]>('getAssessmentMethods'))
    );*/
  }

  /**
   * Handles the error caused by the service
   *
   * @param operation - Operation flag
   * @param result - General result type
   */
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {

      // log to console
      console.error(error);

      ContractMgtService.log(`${operation} failed: ${error.message}`);

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }

  /**
   * Confirms the examine relations of the assessment
   *
   * @param contractId - Contract ID
   * @param assessmentId - Assessment relation ID
   * @param examineId - Examine relation ID
   * @param s - JSON string object that confirms the examine relation of the corresponding assessment relation
   */
  confirmExamine(contractId: number, assessmentId: number, examineId: number, s: string) {
    // tslint:disable-next-line:max-line-length
    return this.http.put<AssessmentExamine>(`${this.API_URL}research_mgt/contracts/${contractId}/assessments/${assessmentId}/examine/${examineId}/approve/`,
      s, this.httpOptions);
    /*.pipe(
        catchError(this.handleError<any[]>('confirmExamine'))
    );*/
  }

  /**
   * Approves the contract used by the contract supervisor
   *
   * @param contractId - Contract ID
   * @param superviseId - Supervise relation ID
   * @param s - JSON string object that approves the contract
   */
  approveContract(contractId: number, superviseId: number, s: string) {
    return this.http.put(`${this.API_URL}research_mgt/contracts/${contractId}/supervise/${superviseId}/approve/`,
      s, this.httpOptions);
    /*.pipe(
        catchError(this.handleError<any[]>('approveContract'))
    );*/
  }

  /**
   * Submits the contract used by the contract owner
   *
   * @param contractId - Contract ID
   */
  updateSubmitted(contractId: number): Observable<any> {
    return this.http.put(`${this.API_URL}research_mgt/contracts/${contractId}/submit/`, JSON.stringify({
      submit: true,
    }), this.httpOptions);
    /*.pipe(
        catchError(this.handleError<any>('updateSubmitted'))
    );*/

  }

  /**
   * Creates the examine relation of the assessment
   *
   * @param contractId - Contract ID
   * @param assessmentId - Assessment relation ID
   * @param s - JSON string object that creates the examine relation of the corresponding assessment relation
   */
  addExamine(contractId: number, assessmentId: any, s: string): Observable<AssessmentExamine> {
    return this.http.post<AssessmentExamine>(this.API_URL + `research_mgt/contracts/${contractId}/assessments/${assessmentId}/examine/`,
      s, this.httpOptions);
    /*.pipe(
        catchError(this.handleError<any>('addExamine'))
    );*/
  }

  /**
   * Updates the general contract information used by the contract owner
   *
   * @param contractId - Contract ID
   * @param s - JSON string object that contains the information to update
   */
  updateContract(contractId: number, s: any): Observable<Contract> {
    return this.http.patch<Contract>(this.API_URL + `research_mgt/contracts/${contractId}/`, s, this.httpOptions)
      .pipe(
        catchError(this.handleError<Contract>('updateContract'))
      );
  }

  /**
   * Updates the supervise relation of the contract used by the contract owner
   *
   * @param contractId - Contract ID
   * @param superviseId - Supervise relation ID
   * @param s - JSON string object that contains the information to update
   */
  updateSupervise(contractId: number, superviseId: number, s: string): Observable<Supervise> {
    return this.http.patch<Supervise>(this.API_URL + `research_mgt/contracts/${contractId}/supervise/${superviseId}/`,
      s, this.httpOptions);
    /*.pipe(
        catchError(this.handleError<any>('addSupervise'))
    );*/
  }

  /**
   * Retrieves the whole contract list
   */
  getContracts(): Observable<Contract[]> {
    return this.http.get<Contract[]>(`${this.API_URL}research_mgt/contracts/`, this.httpOptions)
      .pipe(
        catchError(this.handleError<Contract[]>('getContracts'))
      );
  }

  /**
   * Retrieves the contract
   *
   * @param contractId - Contract ID
   */
  getContract(contractId: number): Observable<Contract> {
    return this.http.get<Contract>(`${this.API_URL}research_mgt/contracts/${contractId}/`, this.httpOptions)
      .pipe(
        catchError(this.handleError<Contract>('getContract'))
      );
  }

  /**
   * Retrieves the related contracts to the user that includes
   * own, convene, supervise and examine
   *
   * @param userId - User ID
   */
  getRelatedContracts(userId: number): Observable<SrpmsUser> {
    return this.http.get<SrpmsUser>(this.API_URL + `research_mgt/users/${userId}/`, this.httpOptions);
    /*.pipe(
        catchError(this.handleError<any>('getRelatedContracts'))
    );*/
  }

  /**
   * Updates the contract's assessment
   *
   * @param contractId - Contract ID
   * @param assessmentId - Assessment relation ID
   * @param s - JSON string object that updates the corresponding assessment relation
   */
  updateAssessment(contractId: number, assessmentId: number, s: string): Observable<Assessment> {
    return this.http.patch<Assessment>(this.API_URL + `research_mgt/contracts/${contractId}/assessments/${assessmentId}/`,
      s, this.httpOptions);
    // .pipe(
    //     catchError(this.handleError<any>('updateAssessment'))
    // );
  }

  /**
   * Updates the contract's examiner
   *
   * @param contractId - Contract ID
   * @param assessmentId - Assessment relation ID
   * @param examineId - Examine relation ID
   * @param s - JSON string object that approves the examine relation of the corresponding assessment
   */
  updateExamine(contractId: number, assessmentId: number, examineId: number, s: string): Observable<AssessmentExamine> {
    return this.http.put<AssessmentExamine>(
      this.API_URL + `research_mgt/contracts/${contractId}/assessments/${assessmentId}/examine/${examineId}/`,
      s, this.httpOptions);
    // .pipe(
    //   catchError(this.handleError<any>('updateExamine'))
    // );
  }

  /**
   * Finalises the contract used by the course convener
   *
   * @param contractId - Contract ID
   * @param s - JSON string object that finalises the corresponding contract
   */
  approveConvene(contractId: number, s: string) {
    return this.http.patch(this.API_URL + `research_mgt/contracts/${contractId}/approve/`,
      s, this.httpOptions)
      .pipe(
        catchError(this.handleError<any>('approveConvene'))
      );
  }

  /**
   * Deletes the contract used by the contract owner
   *
   * @param contractId - Contract ID
   */
  deleteContract(contractId: number) {
    return this.http.delete(this.API_URL + `research_mgt/contracts/${contractId}`, this.httpOptions);
  }

  deleteExamine(contractId: number, assessmentId: number, examineId: number) {
    return this.http.delete(this.API_URL + `research_mgt/contracts/${contractId}/assessments/${assessmentId}/examine/${examineId}/`,
      this.httpOptions);
    /*.pipe(
        catchError(this.handleError<any>('updateExamine'))
    );*/
  }

  createNonformalSupervisor(contractId: number, s: string): Observable<Supervise> {
    return this.http.post<Supervise>(this.API_URL + `research_mgt/contracts/${contractId}/supervise/`, s, this.httpOptions);
  }
}
