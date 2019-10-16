import { Injectable } from '@angular/core';
import { HttpErrorResponse, HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Observable, throwError, BehaviorSubject } from 'rxjs';

import { ACC_SIG, AccountsService } from './accounts.service';
import { catchError, filter, switchMap, take } from 'rxjs/operators';
import { MatDialogConfig } from '@angular/material';

export interface APIErrorResponse extends HttpErrorResponse {
  error: {
    detail?: string
  };
}

/**
 * Intercept HTTP request to implement token authorization and token auto-refresh.
 *
 * @author Dajie Yang
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
              catchError((err: Error) => {
                this.refreshTokenInProgress = false;
                this.accountService.logout();

                const dialogConfig = new MatDialogConfig();
                if (err instanceof Error) {
                  if (err.message === ACC_SIG.TOK_REF_EXPIRE) {
                    dialogConfig.data = 'Session expired, authentication required';
                  }
                } else {
                  dialogConfig.data = 'Authentication required';
                }
                this.accountService.openLoginDialog(dialogConfig);
                return throwError(err);
              })
            );
        }
      }));
  }
}
