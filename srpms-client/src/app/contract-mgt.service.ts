import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { Observable, of } from 'rxjs';
import { catchError } from 'rxjs/operators';


@Injectable({
    providedIn: 'root'
})
export class ContractMgtService {

    private API_URL = '/api/';

    constructor(private http: HttpClient) { }
    public httpOptions = {
        headers: new HttpHeaders({
            'Content-Type':  'application/json',
        })
    };

    private static log(message: string) {
        console.log(`ContractMgt Service: ${message}`);
    }

    getSupervise(contractId: number): Observable<any[]> {
        return this.http.get<any[]>(`${this.API_URL}research_mgt/contracts/${contractId}/supervise/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('getSupervise'))
            );
    }

    getAssessments(contractId: any): Observable<any[]> {
        return this.http.get<any[]>(`${this.API_URL}research_mgt/contracts/${contractId}/assessments/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('getAssessmentMethods'))
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

    confirmExamine(contractId: any, assessmentId: any, examineId: any, s: string) {
        // tslint:disable-next-line:max-line-length
        return this.http.put(`${this.API_URL}research_mgt/contracts/${contractId}/assessments/${assessmentId}/examine/${examineId}/approve/`,
            s, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('confirmExamine'))
            );
    }

    approveContract(contractId: any, superviseId: any, s: string) {
        return this.http.put(`${this.API_URL}research_mgt/contracts/${contractId}/supervise/${superviseId}/approve/`,
            s, this.httpOptions)
            .pipe(
                catchError(this.handleError<any[]>('approveContract'))
            );
    }

    updateSubmitted(contractId: any): Observable<any> {
        return this.http.put(`${this.API_URL}research_mgt/contracts/${contractId}/submit/`, JSON.stringify({
            submit: true,
        }), this.httpOptions)
            .pipe(
                catchError(this.handleError<any>('updateSubmitted'))
            );

    }

    addExamine(contractId: number, assessmentId: any, s: string) {
        return this.http.post(this.API_URL + `research_mgt/contracts/${contractId}/assessments/${assessmentId}/examine/`,
            s, this.httpOptions)
            .pipe(
                catchError(this.handleError<any>('addExamine'))
            );
    }

    updateContract(contractId: number, payload: any): Observable<any> {
        return this.http.patch<any>(this.API_URL + `research_mgt/contracts/${contractId}/`, payload, this.httpOptions)
            .pipe(
                catchError(this.handleError<any>('updateContract'))
            );
    }

    updateSupervise(contractId: any, superviseId: any, supervise: string): Observable<any> {
        return this.http.patch<any>(this.API_URL + `research_mgt/contracts/${contractId}/supervise/${superviseId}/`,
            supervise, this.httpOptions)
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

    getContract(id: any): Observable<any> {
        return this.http.get<any>(`${this.API_URL}research_mgt/contracts/${id}/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any>('getContract'))
            );
    }

    getOwnContracts(userId: any) {
        return this.http.get(this.API_URL + `research_mgt/users/${userId}/`, this.httpOptions)
            .pipe(
                catchError(this.handleError<any>('getOwnContracts'))
            );
    }

    updateAssessment(contractId: number, assessmentId: number, s: string) {
        return this.http.patch(this.API_URL + `research_mgt/contracts/${contractId}/assessments/${assessmentId}/`,
            s, this.httpOptions)
            .pipe(
                catchError(this.handleError<any>('updateAssessment'))
            );
    }

    updateExamine(contractId: number, assessmentId: number, examineId: number, s: string) {
        return this.http.patch(this.API_URL + `research_mgt/contracts/${contractId}/assessments/${assessmentId}/examine/${examineId}/`,
            s, this.httpOptions)
            .pipe(
                catchError(this.handleError<any>('updateExamine'))
            );
    }
}
