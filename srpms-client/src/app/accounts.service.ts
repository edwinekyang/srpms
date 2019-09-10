import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { catchError, map, tap } from 'rxjs/operators';
import { Observable, of } from 'rxjs';

export class JWToken {
  access: string;  // For authentication, short expire time
  refresh: string;  // For refresh the authentication token, longer expire time
}

/* tslint:disable:variable-name */
export class SrpmsUser {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  expire_date: Date;
  uniID: string;
}

/* tslint:enable:variable-name */

@Injectable({
  providedIn: 'root'
})
export class AccountsService {
  private API_URL = '/api/';

  constructor(private http: HttpClient) {
  }

  public token: JWToken;
  public tokenExpireDate: Date;
  public userID: number;
  public user: SrpmsUser;

  public httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  isAuthenticated(): boolean {
    // TODO: route guard
    const jwTokenExpire: Date = new Date(JSON.parse(localStorage.getItem('srpmsExpire')));

    return jwTokenExpire && new Date() <= jwTokenExpire;
  }

  getLocalUser(): SrpmsUser {
    return JSON.parse(localStorage.getItem('srpmsUser'));
  }

  private log(message: string) {
    console.log(`Account Service: ${message}`);
  }

  /**
   * Handle Http operation that failed. Let the app continue.
   *
   * @param operation - name of the operation that failed
   * @param result - optional value to return as the observable result
   */
  private handleError<T>(operation = 'operation', result?: T) {
    return (error: any): Observable<T> => {

      // TODO: send the error to remote logging infrastructure
      console.error(error); // log to console instead

      // TODO: better job of transforming error for user consumption
      this.log(`${operation} failed: ${error.message}`);

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }

  login(username: string, password: string): void {
    this.http.post<JWToken>(this.API_URL + 'accounts/token/', JSON.stringify({ username, password }), this.httpOptions)
      .pipe(
        map(token => this.updateData(token)),
        catchError(this.handleError<SrpmsUser>(`Login username=${username}`))).subscribe();
  }

  refreshToken(): void {
    const jwToken: JWToken = JSON.parse(localStorage.getItem('srpmsToken'));

    if (jwToken) {
      this.http.post<JWToken>('/api/accounts/token/refresh/', jwToken.refresh, this.httpOptions)
        .pipe(map(token => this.updateData(token)));
    } else {
      throw new Error('You don\'t have token locally');
    }
  }

  getUser(id: number): Observable<SrpmsUser> {
    const url = `${this.API_URL}accounts/user/${this.userID}`;
    return this.http.get<SrpmsUser>(url, this.httpOptions)
      .pipe(catchError(this.handleError<SrpmsUser>(`updateDate id=${id}`)));
  }

  private updateData(token: JWToken): void {
    this.token = token;

    // Decode the token to read the username and expiration timestamp
    const tokenParts = this.token.access.split(/\./);
    const tokenDecoded = JSON.parse(window.atob(tokenParts[1]));
    this.tokenExpireDate = new Date(tokenDecoded.exp * 1000);
    this.userID = tokenDecoded.user_id;

    localStorage.setItem('srpmsToken', JSON.stringify(this.token));
    localStorage.setItem('srpmsExpire', JSON.stringify(this.tokenExpireDate));

    const url = `${this.API_URL}accounts/user/${this.userID}`;
    this.getUser(this.userID)
      .pipe(
        map(user => localStorage.setItem('srpmsUser', JSON.stringify(user))),
        catchError(this.handleError<SrpmsUser>(`updateDate id=${this.userID}`))).subscribe();
  }
}
