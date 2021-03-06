# How agile works

**DISCLAIMER: Agile works in many different way, this (i.e. Scrum) is just the way we chose for this project**

- Requirement modeling in Agile
  - **Epic**: the category (or theme) of a bunch of requirements, e.g. Email Notification, Website Access
  - **Story**: usually belongs to a epic, is how requirement being presented in Agile.
    - Define in the way 
      `As a <stakeholder>, I want <some function> [, so that <business value>]`
    - Story does not directly reflect the exact functionality that would be implemented, but a small goal one (or a set) of functionality would achieve.
    - When doing it in the right way, every story's actual workload is similar (for the purpose of agile planning). Big story should be further breakdown to have small stories with appropriate workload.
- Agile in action (Scrum)
  - **Sprint**: sprint defines a fix time of period the team chose to finish one (or more) story.
    - The length of a sprint is related to the time the team need to finish each story
  - Before every sprint, the team would hold a *sprint meeting* to evaluate what story should be finished in this sprint, based on story's priority.
  - For each selected story for the current sprint, functionality included in this story would be defined. Also, assignee would be decided for each story (or functionality).
  - The team then try their best to finish stories in the current sprint
  - At the end of the sprint, a sprint meeting would be held to discuss the progress of the sprint, finished functionality would be reviewed and merge into master branch. If a story is not finished, the team would try to find out the reason, and see if the story should be breakdown or redefined. 

# Agile over Plan-driven

- As of today, plan-driven only used in projects that does not allow easy change of implementation, or life critical
  - For example, hardware design, embedded system, space program
  - Large scale project would use agile-plan-driven hybrid method to collaborate with remote teams
- For most software projects, people find that plan-driven often does not deliver the thing they actually want
- Agile then emerge, on the purpose of reflecting user's need rather than the implementation more accurately

## Why not document requirements

- Requirement is changing all the time, especially for software
  - While document is usually structured, the change of requirement often means its structure is likely to change, at the end the document of requirement would be very hard to maintain or keep track of.
  - User story on the other hand is very flexible, it does not detail the exact functionality that would be implemented until the start of a sprint. 
- Documentation does not reflect directly on user's need
  - Documentation focus more on the function that would be implemented, but does not specify very clear which stakeholder would benefit, or the business value of a functionality
  - User story is quite the opposite, it takes stakeholder and their business value as the top priority, so as to best benefit user's need
- Documentation is a one-way communication
  - Collecting feedback from the receiver is not as easy as user story.
  - User story may looks like more casual sometimes, but it is available publicly for internal team, and categories by stakeholder to allow them easily give feedback. 
- User stories are the new requirements document
  - User stories have emerged as the best and most popular form of product backlog items.
  - A use case is a series of interactions by the user with the system and the response of the system.
- Agile doesn't mean no documentation
  - usually a hybrid way would be used, and design & implementation & deployment would still be documented for maintenance purpose

# Resources

- [12 Advantages of Agile SoftwareDevelopment](https://cs.anu.edu.au/courses/comp3120/public_docs/WP_PM_AdvantagesofAgile.pdf), Alan Koch, Global Knowledge Training, 2011
- [The Benefits You Get by Doing Agile Project Management](https://apiumhub.com/tech-blog-barcelona/benefits-of-agile-project-management/), Ekaterina Novoseltseva, Apiumhub, 2019
- [Agile Development: User stories are the new requirements document](https://medium.com/@LazaroIbanez/agile-development-user-stories-are-the-new-requirements-document-c105947c9291), Lazaro Ibanez, 2018

