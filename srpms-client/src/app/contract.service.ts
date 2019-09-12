import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';

export interface Course {
  course_id: number;
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

  getCourses(): Observable<Course> {
    return this.http.get<Course>(`${this.API_URL}research_mgt/courses/`, this.httpOptions)
      .pipe(
        catchError(this.handleError<Course>('getCourses'))
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
}
