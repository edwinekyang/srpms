import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { catchError, map } from 'rxjs/operators';
import { BehaviorSubject, Observable, of, Subject, throwError } from 'rxjs';

export const ACC_SIG = {
  LOGIN: 'login',
  LOGOUT: 'logout',
  TOK_REF_EXPIRE: 'refresh token expired',
  TOK_REF_NOTFOUND: 'refresh token does not exist'
};

export interface JWToken {
  access: string;  // For authentication, short expire time
  refresh: string;  // For refresh the authentication token, longer expire time
}

/* tslint:disable:variable-name */
export interface SrpmsUser {
  id: number;
  username: string;
  first_name: string;
  last_name: string;
  email: string;
  expire_date: string;
  uni_id: string;
}

/* tslint:enable:variable-name */

/**
 * Account service for handling authentication and user information.
 *
 * Please note that the service does not provide `isAuthenticated` function, as it does not
 * make sense for token-based authentication. For example, the token might expire 3s after
 * checking, and make the return value meaning less. As such, please use the `getLocalUser`
 * function for this purpose. In the case that token expire, the back-end would not authorize
 * anyway, and the auth-interceptor service would log the current user out.
 */
@Injectable({
  providedIn: 'root'
})
export class AccountsService {

  constructor(private http: HttpClient) {
  }

  private API_URL = '/api/';

  // BehaviorSubject can return last time value for new subscribers, normal subject cannot
  private storageSub = new BehaviorSubject<string>(null);

  public httpOptions = {
    headers: new HttpHeaders({
      'Content-Type': 'application/json'
    })
  };

  static getLocalAccessToken(): string {
    return JSON.parse(localStorage.getItem('srpmsAccessToken'));
  }

  /**
   * Decode the token to read the username and expiration timestamp
   */
  static decodeToken(token: string): [number, Date] {
    const tokenParts = token.split(/\./);
    const tokenDecoded = JSON.parse(window.atob(tokenParts[1]));
    const tokenExpireDate = new Date(tokenDecoded.exp * 1000);
    const userID = tokenDecoded.user_id;
    return [userID, new Date(tokenExpireDate)];
  }

  private static log(message: string) {
    console.log(`Account Service: ${message}`);
  }

  // Used to inform component that local storage has changed.
  private watchStorage(): Observable<string> {
    return this.storageSub.asObservable();
  }

  private clearLocal(): void {
    localStorage.removeItem('srpmsAccessToken');
    localStorage.removeItem('srpmsRefreshToken');
    localStorage.removeItem('srpmsUser');
    this.storageSub.next(ACC_SIG.LOGOUT);
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
      AccountsService.log(`${operation} failed: ${error.message}`);

      // Let the app keep running by returning an empty result.
      return of(result as T);
    };
  }

  /**
   * Update local storage to store authentication information
   */
  private updateData(token: JWToken): void {
    const [userID, ] = AccountsService.decodeToken(token.access);

    if (token.access) {
      localStorage.setItem('srpmsAccessToken', JSON.stringify(token.access));
    }
    if (token.refresh) {
      localStorage.setItem('srpmsRefreshToken', JSON.stringify(token.refresh));
    }

    this.getUser(userID)
      .pipe(
        map(user => {
          localStorage.setItem('srpmsUser', JSON.stringify(user));
          this.storageSub.next(ACC_SIG.LOGIN);
        }),
        catchError(this.handleError<SrpmsUser>(`updateData id=${userID}`))).subscribe();
  }

  login(loginForm): Observable<void> {
    return this.http.post<JWToken>(this.API_URL + 'accounts/token/', JSON.stringify(loginForm), this.httpOptions)
      .pipe(
        map(token => this.updateData(token)),
        catchError(err => throwError(err)));
  }

  refreshToken(): Observable<string> {
    const refreshToken: string = JSON.parse(localStorage.getItem('srpmsRefreshToken'));

    if (refreshToken) {
      const [, refreshExpire] = AccountsService.decodeToken(refreshToken);
      if (new Date() < refreshExpire) {
        return this.http.post<JWToken>(this.API_URL + 'accounts/token/refresh/', { refresh: refreshToken }, this.httpOptions)
          .pipe(map(token => {
            this.updateData(token);
            return token.access;
          }));
      } else {
        return throwError(new Error(ACC_SIG.TOK_REF_EXPIRE));
      }
    } else {
      return throwError(new Error(ACC_SIG.TOK_REF_NOTFOUND));
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
  }

  /**
   * Return user object stored in the local storage, return null if not exist.
   */
  getLocalUser(): Observable<SrpmsUser> {
    return this.watchStorage()
      .pipe(
        map(() => {
          const user: SrpmsUser = JSON.parse(localStorage.getItem('srpmsUser'));
          if (user) {
            return user;
          } else {
            return null;
          }
        })
      );
  }

  getUser(id: number): Observable<SrpmsUser> {
    const url = `${this.API_URL}accounts/user/${id}/`;
    return this.http.get<SrpmsUser>(url, this.httpOptions)
      .pipe(catchError(this.handleError<SrpmsUser>(`updateDate id=${id}`)));
  }
}
