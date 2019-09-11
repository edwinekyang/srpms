import { Injectable } from '@angular/core';
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';

import { AccountsService, JWToken } from './accounts.service';
import { catchError, filter, switchMap, take } from 'rxjs/operators';

/**
 * Intercept HTTP request to implement token authorization and token auto-refresh.
 */
@Injectable()
export class AuthInterceptor implements HttpInterceptor {


  constructor(public accountService: AccountsService) {
  }

  private refreshTokenInProgress = false;
  private refreshTokenSub: BehaviorSubject<string> = new BehaviorSubject<string>(null);

  private static addAuthenticationToken(req: HttpRequest<any>) {
    const accessToken = AccountsService.getLocalAccessToken();

    if (!accessToken) {
      return req;
    } else {
      return req.clone({
        headers: req.headers.set('Authorization', 'Bearer ' + accessToken)
      });
    }
  }

  /**
   * Intercept every HTTP call to append the authentication token.
   *
   * Reference: https://blog.angular-university.io/angular-jwt-authentication/
   */
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    return next.handle(AuthInterceptor.addAuthenticationToken(req))
      .pipe(catchError(error => {  // Only attach token when error occurs.
        // Don't attach token for authentication related request.
        if (req.url.includes('accounts/token')) {

          // Logout if refresh failed.
          if (req.url.includes('accounts/token/refresh')) {
            this.accountService.logout();
          }

          return throwError(error);
        }

        // If not an authorization error, skip
        if (error.status !== 401) {
          return throwError(error);
        }

        if (this.refreshTokenInProgress) {  // Wait for refresh finished and retry
          return this.refreshTokenSub
            .pipe(
              filter(result => result !== null),
              take(1),
              switchMap(() => next.handle(AuthInterceptor.addAuthenticationToken(req))));
        } else {
          // Tell other unauthorized requests to wait
          this.refreshTokenInProgress = true;
          this.refreshTokenSub.next(null);

          return this.accountService.refreshToken()
            .pipe(
              switchMap(token => {
                this.refreshTokenInProgress = false;
                this.refreshTokenSub.next(token);

                return next.handle(AuthInterceptor.addAuthenticationToken(req));
              }),
              catchError(err => {
                this.refreshTokenInProgress = false;
                this.accountService.logout();
                return throwError(err);
              })
            );
        }
      }));
  }
}
