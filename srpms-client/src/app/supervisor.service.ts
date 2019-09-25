import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';


@Injectable({
    providedIn: 'root'
})
export class SupervisorService {
    constructor(private http: HttpClient) { }

    private API_URL = '/api/';

    public httpOptions = {
        headers: new HttpHeaders({
            'Content-Type':  'application/json',
        })
    };

    private static log(message: string) {
        console.log(`Supervisor Service: ${message}`);
    }

    getSupervise(): Observable<any[]> {
        return this.http.get<any[]>(`${this.API_URL}research_mgt/supervise/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('getSupervise'))
            );
    }

    private handleError<T>(operation = 'operation', result?: T) {
        return (error: any): Observable<T> => {

            // TODO: send the error to remote logging infrastructure
            console.error(error); // log to console instead

            // TODO: better job of transforming error for user consumption
            SupervisorService.log(`${operation} failed: ${error.message}`);

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }
}
