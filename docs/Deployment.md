# Disable the REST browsable API on production

Simple add the following to the `settings.py`
```python
REST_FRAMEWORK = {
    'DEFAULT_RENDERER_CLASSES': (
        'rest_framework.renderers.JSONRenderer',
    )
}
```

[Refer to here](http://masnun.com/2016/04/20/django-rest-framework-remember-to-disable-web-browsable-api-in-production.html)
for the reason of doing so.