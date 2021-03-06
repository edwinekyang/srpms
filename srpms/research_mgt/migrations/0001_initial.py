# Generated by Django 2.2.1 on 2019-10-09 11:39

from django.conf import settings
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('contenttypes', '0002_remove_content_type_name'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='AppPermission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='ActivityAction',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.SlugField(unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='AssessmentTemplate',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('description', models.CharField(blank=True, default='', max_length=200)),
                ('max_weight', models.IntegerField()),
                ('min_weight', models.IntegerField()),
                ('default_weight', models.IntegerField(blank=True, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Contract',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField(default=2019, validators=[django.core.validators.MinValueValidator(1, 'Year number should > 1'), django.core.validators.MaxValueValidator(9999, 'Year number should < 9999')])),
                ('semester', models.IntegerField(default=1, validators=[django.core.validators.MinValueValidator(1, 'Semester number should >= 1'), django.core.validators.MaxValueValidator(2, 'Semester number should <= 2')])),
                ('duration', models.IntegerField(default=2, validators=[django.core.validators.MinValueValidator(1, 'Duration semesters should >= 1'), django.core.validators.MaxValueValidator(8, 'Max duration supported is 8')])),
                ('resources', models.CharField(blank=True, default='', max_length=500)),
                ('convener_approval_date', models.DateTimeField(blank=True, null=True)),
                ('create_date', models.DateTimeField(auto_now_add=True)),
                ('submit_date', models.DateTimeField(blank=True, null=True)),
                ('was_submitted', models.BooleanField(blank=True, default=False)),
                ('convener', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name='convene', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Course',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('course_number', models.CharField(max_length=20, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('units', models.IntegerField(validators=[django.core.validators.MinValueValidator(0, 'Course unit should larger than zero'), django.core.validators.MaxValueValidator(24, 'Course unit larger than 24 is not current supported')])),
            ],
        ),
        migrations.CreateModel(
            name='IndividualProject',
            fields=[
                ('contract', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='individual_project', serialize=False, to='research_mgt.Contract')),
                ('title', models.CharField(default='Project title', max_length=100)),
                ('objectives', models.CharField(blank=True, default='', max_length=500)),
                ('description', models.CharField(blank=True, default='', max_length=1000)),
            ],
            bases=('research_mgt.contract',),
        ),
        migrations.CreateModel(
            name='SpecialTopic',
            fields=[
                ('contract', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, related_name='special_topic', serialize=False, to='research_mgt.Contract')),
                ('title', models.CharField(default='Topic title', max_length=100)),
                ('objectives', models.CharField(blank=True, default='', max_length=500)),
                ('description', models.CharField(blank=True, default='', max_length=1000)),
            ],
            bases=('research_mgt.contract',),
        ),
        migrations.CreateModel(
            name='Examine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='examine', to='research_mgt.Contract')),
                ('examiner', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='examine', to=settings.AUTH_USER_MODEL)),
                ('nominator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='examiner_nominate', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('contract', 'examiner')},
            },
        ),
        migrations.AddField(
            model_name='contract',
            name='course',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='contract', to='research_mgt.Course'),
        ),
        migrations.AddField(
            model_name='contract',
            name='owner',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='own', to=settings.AUTH_USER_MODEL),
        ),
        migrations.CreateModel(
            name='Assessment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('additional_description', models.CharField(blank=True, default='', max_length=200)),
                ('due', models.DateField(blank=True, null=True)),
                ('weight', models.IntegerField(blank=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment', to='research_mgt.Contract')),
                ('template', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='assessment', to='research_mgt.AssessmentTemplate')),
            ],
        ),
        migrations.CreateModel(
            name='ActivityLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('message', models.CharField(blank=True, default='', max_length=500)),
                ('object_id', models.PositiveIntegerField()),
                ('action', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='research_mgt.ActivityAction')),
                ('actor', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
                ('content_type', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='contenttypes.ContentType')),
            ],
        ),
        migrations.CreateModel(
            name='Supervise',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('is_formal', models.BooleanField()),
                ('supervisor_approval_date', models.DateTimeField(blank=True, null=True)),
                ('contract', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='supervise', to='research_mgt.Contract')),
                ('nominator', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='supervisor_nominate', to=settings.AUTH_USER_MODEL)),
                ('supervisor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='supervise', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'unique_together': {('supervisor', 'contract')},
            },
        ),
        migrations.CreateModel(
            name='AssessmentExamine',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('examiner_approval_date', models.DateTimeField(blank=True, null=True)),
                ('assessment', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_examine', to='research_mgt.Assessment')),
                ('contract', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='assessment_examine', to='research_mgt.Contract')),
                ('examine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='assessment_examine', to='research_mgt.Examine')),
            ],
            options={
                'unique_together': {('assessment', 'examine')},
            },
        ),
    ]
