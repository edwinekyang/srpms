# Relational Model
## Contract
```
Contract(id, year, semester, duration, resource, convener_approval_date, convener, create_date, owner, course  
PK: {id}
FK: [convener] -> SRPMS_USER, [owner] -> SRPMS_USER, [course] -> Course
```
## Supervise
```
Supervise(supervisor, contract, is_formal, approval_date)
FK: supervisor -> SRPMS_USER, contract -> CONTRACT
```
- Since we might have more than 1 supervisor

## Individual Project
```
Individual_Project(contract, title, objectives, description)
Special_Topics(contract, title, objectives, description)
PK: {contract}
FK: [contract] -> CONTRACT
```

## Course
```
Course(id, course_number, name)
PK: {id}
```

## Assessment Method
```
Assessment_Method(id, template, contract, additional_description, due, max_mark, examiner, examiner_approval_date)
PK: {id}
unique_together(assessment, contract, examiner)
FK: [template] -> ASSESSMENT_TEMPLATE, [examiner] -> SRPMS_USER, [contract] -> CONTRACT
```
- Since we might have multiple examiner woking on the same assessment

## Assessment Template
```
Assessment_Template(id, name, description, min_mark, max_mark)
PK: {id}
```
