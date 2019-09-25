import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface Course {
  id: number;
  course_number: string;
  name: string;
}

@Injectable({
  providedIn: 'root'
})
export class ContractService {

  constructor(private http: HttpClient) { }

  private API_URL = '/api/';

  public httpOptions = {
    headers: new HttpHeaders({
      'Content-Type':  'application/json',
    })
  };

  private static log(message: string) {
    console.log(`Contract Service: ${message}`);
  }

  getCourses(): Observable<Course[]> {
    return this.http.get<Course[]>(`${this.API_URL}research_mgt/course/`, this.httpOptions)
      .pipe(
        catchError(this.handleError<Course[]>('getCourses'))
      );
  }

  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {

      // TODO: send the error to remote logging infrastructure
      console.error(error); // log to console instead

      // TODO: better job of transforming error for user consumption
      ContractService.log(`${operation} failed: ${error.message}`);

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }

  addContract(payLoad: any): Observable<any> {
    return this.http.post<any>(this.API_URL + 'research_mgt/contracts/', payLoad, this.httpOptions)
      .pipe(
        catchError(this.handleError<any>('addContract'))
      );
  }

  addAssessmentMethod(assessment: string): Observable<any> {
    return this.http.post<any>(this.API_URL + 'research_mgt/assessment-methods/', assessment, this.httpOptions)
      .pipe(
        catchError(this.handleError<any>('addAssessmentMethod'))
      );
  }

  addSupervise(supervise: string): Observable<any> {
    return this.http.post<any>(this.API_URL + 'research_mgt/supervise/', supervise, this.httpOptions)
      .pipe(
        catchError(this.handleError<any>('addSupervise'))
      );
  }

  getContracts(): Observable<any> {
    return this.http.get<any>(`${this.API_URL}research_mgt/contracts/`, this.httpOptions)
        .pipe(
            catchError(this.handleError<any>('getContracts'))
        );
  }
}
