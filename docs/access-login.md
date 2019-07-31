# Users

There is this application `users` for extending the basic `User` class
from `django.contrib.auth` for the purpose of including extra attribute 
for the use from different applications in this site.

Whenever you need to access user attributes from your application, you
should import the model from the `users` application, instead extending
the `User` class in your own application. 

Checkout [Django official documentation for extending the `User` model](https://docs.djangoproject.com/en/2.2/topics/auth/customizing/#extending-the-existing-user-model)
for more information.

# ANU LDAP Server information

```
url:  ldap.anu.edu.au
port: 636
```