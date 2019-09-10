import { Injectable } from '@angular/core';
import { HttpEvent, HttpHandler, HttpInterceptor, HttpRequest } from '@angular/common/http';
import { Observable } from 'rxjs';

import { JWToken } from './accounts.service';

@Injectable({
  providedIn: 'root'
})
export class AuthInterceptor implements HttpInterceptor {

  constructor() {
  }

  /**
   * Intercept every HTTP call to append the authentication token.
   *
   * Reference: https://blog.angular-university.io/angular-jwt-authentication/
   */
  intercept(req: HttpRequest<any>, next: HttpHandler): Observable<HttpEvent<any>> {
    const jwToken: JWToken = JSON.parse(localStorage.getItem('srpmsToken'));

    if (jwToken) {
      const cloned = req.clone({
        headers: req.headers.set('Authorization', 'Bearer ' + jwToken.access)
      });
      return next.handle(cloned);
    } else {
      return next.handle(req);
    }
  }
}
