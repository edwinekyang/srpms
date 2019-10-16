import { Injectable } from '@angular/core';
import {HttpClient, HttpErrorResponse, HttpHeaders} from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { API_URL } from './api-url';

export interface Course {
  id: number;
  course_number: string;
  name: string;
  units: number;
}

@Injectable({
  providedIn: 'root'
})
export class ContractService {

  constructor(private http: HttpClient) { }

  private API_URL = API_URL;

  public httpOptions = {
    headers: new HttpHeaders({
      'Content-Type':  'application/json',
    })
  };

  private static log(message: string) {
    console.log(`Contract Service: ${message}`);
  }

  /**
   * Retrieves the course list
   */
  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>(`${this.API_URL}research_mgt/courses/`, this.httpOptions);
        /*.pipe(
            catchError(this.handleError<Course[]>('getCourses'))
        );*/
  }

  private handleError<T>(operation = 'operation', result?: T) {
    return (error: HttpErrorResponse): Observable<T> => {

      console.error(error.status); // log to console instead

      ContractService.log(`${operation} failed: ${error.message}`);

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }

  /**
   * Creates the contract
   *
   * @param payLoad - Contract general information
   */
  addContract(payLoad: any): Observable<any> {
    return this.http.post<any>(this.API_URL + 'research_mgt/contracts/', payLoad, this.httpOptions)
        .pipe(
            catchError(this.handleError<any>('addContract'))
        );
  }

  /**
   * Updates the assessment relation of the contract
   *
   * @param contractId - Contract ID
   * @param assessmentId - Assessment relation ID
   * @param assessment - Assessment information to update
   */
  patchAssessment(contractId: any, assessmentId: any, assessment: string): Observable<any> {
    return this.http.patch<any>(this.API_URL + `research_mgt/contracts/${contractId}/assessments/${assessmentId}/`,
        assessment, this.httpOptions);
        /*.pipe(
            catchError(this.handleError<any>('patchAssessmentMethod'))
        );*/
  }

  /**
   * Creates the supervise relation of the contract
   *
   * @param contractId - Contract ID
   * @param supervise - Supervise information to create
   */
  addSupervise(contractId: any, supervise: string): Observable<any> {
    return this.http.post<any>(this.API_URL + `research_mgt/contracts/${contractId}/supervise/`, supervise, this.httpOptions);
        /*.pipe(
            catchError(this.handleError<any>('addSupervise'))
        );*/
  }
}
