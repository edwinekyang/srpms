##  CSRF verification error, ..., not in trusted origin

Reasons:

- Starting in ~Djagno 1.9, the CSRF check requires that the `Referer` and `Host` match unless you specify a [`CSRF_TRUSTED_ORIGINS`](https://docs.djangoproject.com/en/2.0/ref/settings/#csrf-trusted-origins) (see the code around `REASON_BAD_REFERER` [here](https://docs.djangoproject.com/en/2.0/_modules/django/middleware/csrf/))
- If you don't specify `CSRF_TRUSTED_ORIGINS`, the system falls back on `request.get_host()`
- `request.get_host()` uses `request._get_raw_host()`
- `request._get_raw_host()` checks sequentially `HTTP_X_FORWARDED_HOST` (if `USE_X_FORWARDED_HOST` is set), `HTTP_HOST`, and `SERVER_NAME`
- Most recommended Nginx configurations suggest an entry like `proxy_set_header X-Forwarded-Host $host:$server_port;`
- Eventually, the referrer (e.g. `<host>`) is compared to `X-Forwarded-Host` (e.g. `<host>:<port>`). These do not match so CSRF fails.

Two solutions:

- include host and port in `CSRF_TRUSTED_ORIGINS`
  - Not recommended as it would hard code things
- remove `port` from `X-Forwarded-Host` in nginx configuration (on the assumption that the non-spec `X-Forwarded-Host` follows the same semantics as `Host`)

# Accounts

There is this application `accounts` for extending the basic `User` class from `django.contrib.auth` for the purpose of including extra attribute for the use from different applications in this site.

Whenever you need to access user attributes from your application, you should import the model from the `accounts` application, instead extending the `User` class in your own application. 

Checkout [Django official documentation for extending the `User` model](https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#extending-the-existing-user-model) for more information.

## SRPMS_USER

- To approve a supervisor, 

# ANU LDAP Server

- Server address
  ```
  url:  ldap.anu.edu.au
  port: 389
  ```
- For remote development purpose, use ssh tunneling to access the ldap server through the VM:
  
  `ssh -L 389:ldap.anu.edu.au:389 <UniID>@srpms.cecs.anu.edu.au`

  Note that you need `sudo` privilege for mapping ports below 1024

## Access user information

The following command would give the information regarding the given uid

`ldapsearch -h localhost -x -b ou=People,o=anu.edu.au -LLL "(uid=uXXXXXXX)"`

`-b` specifies the base directory that we are going to do the search

Search result:
- For students, it would return: `affiliation: student`
- For staff, it would return `affiliation: staff`
- An account may have multiple affiliation, for example, tutors would usually
  have both `affiliation: student` and `affiliation: staff`

Caveats:
- It appears that ANU does not distinguish very detail position of a given
  account, for example, both tutor and course convenor have the `staff` affiliation.
- However, course convenor does not have other affiliation to indicate that he/she
  has higher privilege. 
  
## LDAP authentication backend in SRPMS

We use the [django-auth-ldap](https://github.com/django-auth-ldap/django-auth-ldap) module
for configuring the LDAP authentication backend to use ANU's authentication service.

In the current development, only staff can be assigned as supervisor or examinor.

TODO:
- SRPMS would update account information on every success login, however what's the case that
  the student graduate? Does ANU still keep the LDAP entry for the student? What about the
  case that a professor make some career change?

# Reference

[Logout Django Rest Framework JWT](https://stackoverflow.com/questions/52431850/logout-django-rest-framework-jwt)

[JavaScript JSON Date Parsing and real Dates](https://weblog.west-wind.com/posts/2014/Jan/06/JavaScript-JSON-Date-Parsing-and-real-Dates)

[Property 'subscribe' does not exist on type 'OperatorFunction'](https://stackoverflow.com/questions/50398107/property-subscribe-does-not-exist-on-type-operatorfunctionresponse-recipe)

[Angular Security - Authentication With JSON Web Tokens (JWT): The Complete Guide](https://blog.angular-university.io/angular-jwt-authentication/)

[Angular Material Dialog: A Complete Example](https://blog.angular-university.io/angular-material-dialog/)

[Watch for changes in LocalStorage angular2](https://stackoverflow.com/questions/46078714/watch-for-changes-in-localstorage-angular2)

[Angular Tutorial — Implement Refresh Token with HttpInterceptor](https://itnext.io/angular-tutorial-implement-refresh-token-with-httpinterceptor-bfa27b966f57)