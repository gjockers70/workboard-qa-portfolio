# UAT test data

All identities and records are synthetic and limited to the local environment.

| Data ID | Purpose | Safe representation | Lifecycle |
|---|---|---|---|
| UAT-MEMBER-A | Primary member persona | Unique runtime email matching `phase11.member.<token>@example.test` | Created for the session; disposable |
| UAT-MEMBER-B | Member whose task appears in team oversight | Unique runtime email matching `phase11.team-member.<token>@example.test` | Created for the session; disposable |
| UAT-ADMIN | Administrator persona | Synthetic local administrator supplied through temporary environment variables | Existing local record; password never stored in the repository |
| UAT-TASK-DAILY | Full task lifecycle | Unique title containing `Phase11 daily` | Deleted after the scenario |
| UAT-TASK-ACTIVE | Search and filter active item | Unique title containing the session search token | Deleted after evidence capture |
| UAT-TASK-COMPLETE | Search and filter completed item | Unique title containing the session search token | Deleted after evidence capture |
| UAT-TASK-OTHER | Nonmatching control item | Unique unrelated title | Deleted after evidence capture |
| UAT-TASK-REFRESH | Session-continuity item | Unique title created once before refresh | Deleted after evidence capture |
| UAT-TASK-TEAM | Member-owned team-view item | Unique title visible to the administrator | Deleted by its owning member after evidence capture |

Passwords are generated or supplied at runtime, remain local, and are never written into UAT evidence. No customer, employee, production, or personal information is used.
