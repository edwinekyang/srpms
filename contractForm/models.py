from django import forms
from django.db import models

# Create your models here.


class Contract(models.Model):
    contract_id = models.AutoField(primary_key=True)
    course_number = models.CharField(max_length=20)
    semester = models.CharField(max_length=20)
    student_id = models.CharField(max_length=10)
    student_name = models.CharField(max_length=100)
    title = models.CharField(max_length=100)
    report = models.IntegerField(default=45)
    artefact = models.IntegerField(default=45)
    supervisor = models.CharField(max_length=100)
    examinor = models.CharField(max_length=100)
    notes = models.CharField(max_length=500)

    def __str__(self):
        return self.student_id + " " + self.student_name


class Courses(models.Model):
    course_number = models.CharField(max_length=20)
    course_name = models.CharField(max_length=50)

    def __str__(self):
        return self.course_number + " " + self.course_name
