# Requirements Traceability Matrix

This readable matrix shows one end-to-end path for every product story. The CSV register expands the same links into machine-readable records; individual cases may cover additional criteria.

| Requirement ID | User Story ID | Acceptance Criteria ID | Test Case ID | Automated Test | Test Cycle ID | Execution Status | Defect ID | Retest Status | Final Status |
|---|---|---|---|---|---|---|---|---|---|
| FR-AUTH-001 | US-001 | AC-US001-01 | TC-AUTH-001 | `tests/ui/test_functional_regression.py::test_member_can_register_and_sign_out` | CYCLE-PH3-20260810 | Pass | - | Not required | Covered |
| FR-AUTH-003 | US-002 | AC-US002-02 | TC-API-AUTH-001 | `tests/api/test_workboard_api.py::test_protected_endpoint_rejects_missing_or_invalid_token` | CYCLE-PH6-API-20260810 | Pass | - | Not required | Covered |
| FR-TASK-001 | US-003 | AC-US003-01 | TC-TASK-001 | `tests/ui/test_functional_regression.py::test_member_task_lifecycle` | CYCLE-PH3-20260810 | Pass | - | Not required | Covered |
| FR-TASK-006 | US-004 | AC-US004-05 | TC-SEARCH-006 | `tests/ui/test_functional_regression.py::test_search_and_status_filter_apply_together` | CYCLE-PH5-REGRESSION-20260810 | Pass | - | Not required | Covered |
| FR-PROFILE-001 | US-005 | AC-US005-03 | TC-PROFILE-001 | `tests/ui/test_functional_regression.py::test_profile_name_persists_across_sessions` | CYCLE-PH5-REGRESSION-20260810 | Pass | - | Not required | Covered |
| FR-ADMIN-002 | US-006 | AC-US006-02 | TC-ADMIN-002 | `tests/ui/test_functional_regression.py::test_administrator_team_view_is_read_only_for_member_task` | CYCLE-PH5-REGRESSION-20260810 | Pass | - | Not required | Covered |
| FR-AUTHZ-001 | US-007 | AC-US007-05 | TC-DB-AUTHZ-001 | `tests/database/test_workboard_database.py::test_unauthorized_update_and_delete_leave_database_unchanged` | CYCLE-PH7-DATABASE-20260810 | Pass | - | Not required | Covered |
| NFR-ACC-004 | US-008 | AC-US008-06 | TC-ACCESS-003 | `tests/ui/test_phase3_catalog.py::test_component_and_text_contrast` | CYCLE-PH3-20260810 | Pass after retest | DEF-P3-001 | Passed | Covered; defect closed |
| NFR-REMOTE-001 | US-009 | AC-US009-03 | TC-REMOTE-002 | `tests/ui/test_phase3_catalog.py::test_connection_interruption_has_no_false_success` | CYCLE-PH3-20260810 | Pass | - | Not required | Covered |
| BR-004 | US-010 | AC-US010-01 | TC-RELEASE-001 | `tests/test_management/test_agile_artifacts.py` | CYCLE-PH9-MANAGEMENT-20260810 | Pass | - | Not required | Covered at Phase 9 checkpoint |
| NFR-PERF-001 | US-010 | AC-US010-05 | TC-RELEASE-005 | `performance/locustfile.py` | CYCLE-PH10-PERFORMANCE | Pass | - | Not required | Covered at Phase 10 checkpoint |

The US-008 chain demonstrates the complete lifecycle: story -> acceptance criterion -> test case -> automated check -> failed execution -> DEF-P3-001 -> correction -> passing retest -> closed final status.
