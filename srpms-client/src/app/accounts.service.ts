import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { catchError, map } from 'rxjs/operators';
import { Observable, of, Subject } from 'rxjs';

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
  expire_date: string;
  uni_id: string;
}

/* tslint:enable:variable-name */

@Injectable({
  providedIn: 'root'
})
export class AccountsService {
  private API_URL = '/api/';

  private storageSub = new Subject<boolean>();

  constructor(private http: HttpClient) {
  }

  public token: JWToken;
  public tokenExpireDate: Date;
  public userID: number;

  public httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  // Used to inform component that local storage has changed.
  watchStorage(): Observable<boolean> {
    return this.storageSub.asObservable();
  }

  /**
   * Decode the token to read the username and expiration timestamp
   */
  private decodeToken(token: string): [number, Date] {
    const tokenParts = token.split(/\./);
    const tokenDecoded = JSON.parse(window.atob(tokenParts[1]));
    const tokenExpireDate = new Date(tokenDecoded.exp * 1000);
    const userID = tokenDecoded.user_id;
    return [userID, tokenExpireDate];
  }

  private clearLocal(): void {
    localStorage.removeItem('srpmsToken');
    localStorage.removeItem('srpmsExpire');
    localStorage.removeItem('srpmsUser');
    this.storageSub.next(true);
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

  /**
   * Update local storage to store authentication information
   */
  private updateData(token: JWToken): void {
    this.token = token;
    [this.userID, this.tokenExpireDate] = this.decodeToken(this.token.access);

    localStorage.setItem('srpmsToken', JSON.stringify(this.token));
    localStorage.setItem('srpmsExpire', JSON.stringify(this.tokenExpireDate));

    this.getUser(this.userID)
      .pipe(
        map(user => {
          localStorage.setItem('srpmsUser', JSON.stringify(user));
          this.storageSub.next(true);
        }),
        catchError(this.handleError<SrpmsUser>(`updateDate id=${this.userID}`))).subscribe();
  }

  isAuthenticated(): boolean {
    // TODO: route guard
    const jwTokenExpire: Date = new Date(JSON.parse(localStorage.getItem('srpmsExpire')));

    return jwTokenExpire && new Date() <= jwTokenExpire;
  }

  login(username: string, password: string): void {
    this.http.post<JWToken>(this.API_URL + 'accounts/token/', JSON.stringify({ username, password }), this.httpOptions)
      .pipe(
        map(token => this.updateData(token)),
        catchError(this.handleError<SrpmsUser>(`Login username=${username}`))).subscribe();
  }

  refreshToken(): boolean {
    const jwToken: JWToken = JSON.parse(localStorage.getItem('srpmsToken'));

    if (jwToken) {
      const [, refreshExpire] = this.decodeToken(jwToken.refresh);
      if (new Date() < new Date(refreshExpire)) {
        this.http.post<JWToken>(this.API_URL + 'accounts/token/refresh/', jwToken.refresh, this.httpOptions)
          .pipe(map(token => this.updateData(token))).subscribe();
        return true;
      } else {
        console.log('All token expired');
        return false;
      }
    } else {
      throw new Error('You don\'t have token locally');
    }
  }

  /**
   * For JWT, you cannot expire a token on demand to log a user out.
   * However, you can:
   *   1. Remove the local stored token.
   *   2. TODO: black list the token on server side.
   */
  logout(): void {
    this.clearLocal();
    this.token = null;
    this.userID = null;
    this.userID = null;
  }

  getUser(id: number): Observable<SrpmsUser> {
    const url = `${this.API_URL}accounts/user/${this.userID}`;
    return this.http.get<SrpmsUser>(url, this.httpOptions)
      .pipe(catchError(this.handleError<SrpmsUser>(`updateDate id=${id}`)));
  }
}
