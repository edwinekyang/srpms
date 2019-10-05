import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';
import { BehaviorSubject } from 'rxjs';


@Injectable({
    providedIn: 'root'
})
export class ContractMgtService {
    constructor(private http: HttpClient) { }
    public httpOptions = {
        headers: new HttpHeaders({
            'Content-Type':  'application/json',
        })
    };

    private static log(message: string) {
        console.log(`ContractMgt Service: ${message}`);
    }

    changeMessage(message: any) {
        this.messageSource.next(message);
    }

    getSupervise(): Observable<any[]> {
        return this.http.get<any[]>(`${this.API_URL}research_mgt/supervise/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('getSupervise'))
            );
    }

    getExamine(): Observable<any[]> {
        return this.http.get<any[]>(`${this.API_URL}research_mgt/supervise/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('getExamine'))
            );
    }

    getAssessmentMethods(): Observable<any[]> {
        return this.http.get<any[]>(`${this.API_URL}research_mgt/assessment-methods/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('getAssessmentMethods'))
            );
    }

    getAssessmentTemplates(): Observable<any[]> {
        return this.http.get<any[]>(`${this.API_URL}research_mgt/assessment-templates/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('getAssessmentTemplates'))
            );
    }

    getAssessmentTemplate(id: any): Observable<any> {
        return this.http.get<any[]>(`${this.API_URL}research_mgt/assessment-templates/${id}/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('getAssessmentTemplate'))
            );
    }

    getAssessmentMethod(id: any): Observable<any> {
        return this.http.get<any[]>(`${this.API_URL}research_mgt/assessment-methods/${id}/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('getAssessmentMethod'))
            );
    }

    private handleError<T>(operation = 'operation', result?: T) {
        return (error: any): Observable<T> => {

            // TODO: send the error to remote logging infrastructure
            console.error(error); // log to console instead

            // TODO: better job of transforming error for user consumption
            ContractMgtService.log(`${operation} failed: ${error.message}`);

            // Let the app keep running by returning an empty result.
            return of(result as T);
        };
    }
}
