# Remote-Access Testing Concepts

## Purpose and claim boundary

This document records the remote-access risks represented in WorkBoard, the local checks that were actually executed, and the scenarios that remain test design only. The project does not provision Remote Desktop, virtual desktop, VPN, browser-streaming, or other remote-access infrastructure.

The executed evidence supports refresh, simulated request interruption, reconnection, false-success prevention, and authorization consistency in the local application. It does not establish behavior over a genuine remote session, a production network, or a managed identity environment.

## Risks considered

| Risk | User or system effect | Intended observation |
|---|---|---|
| Refresh repeats the last mutation | Duplicate tasks or unintended changes | Session remains valid and the recorded mutation appears once |
| Connection fails during a mutation | False success or uncertain persisted state | A clear error appears and no unconfirmed record is stored |
| Reconnection changes identity or role | Authorization exposure | The same member role and ownership rules remain in force |
| Token expires during a remote session | Stale or misleading workspace | Session data is cleared and sign-in recovery is understandable |
| Latency encourages repeated activation | Duplicate requests or confusing feedback | Controls and feedback prevent ambiguous repeated work |
| Remote display or shared endpoint exposes data | Credential or task disclosure | Secrets are masked, logs are sanitized, and endpoint policy is followed |

## Executed local checks

| Case | Execution | Verified result | Evidence boundary |
|---|---|---|---|
| `TC-REMOTE-001` | Create one uniquely named task, record the task count, refresh the browser, and recheck identity and task state | The valid session remained available, the task count was unchanged, and the mutation appeared exactly once | Local browser refresh; no remote transport or network shaping |
| `TC-REMOTE-002` | Block local API requests through the browser debugging interface, attempt a task creation, restore requests, and refresh | Error feedback replaced false success, the unconfirmed task was absent, and the member role remained unchanged after recovery | Local simulated interruption; not a stopped remote host, VPN, or physical network loss |
| Invalid-session recovery | Replace the local token with an invalid value and refresh | The stale session was removed and the user received the sign-in recovery message | Simulated invalid token; the natural token lifetime was not awaited |
| Simulated UAT refresh | Refresh an authenticated workspace containing a uniquely named task | The participant-facing scenario retained the session and displayed exactly one matching task | Disclosed local UAT simulation, not real-client or remote-session evidence |

The automated checks are implemented in [tests/ui/test_phase3_catalog.py](../tests/ui/test_phase3_catalog.py). Managed cases and recorded executions are stored in [test-management/TEST_CASES.csv](../test-management/TEST_CASES.csv) and [test-management/TEST_EXECUTIONS.csv](../test-management/TEST_EXECUTIONS.csv). The requirement and acceptance links are summarized in [TRACEABILITY_MATRIX.md](../TRACEABILITY_MATRIX.md).

## Design-only scenarios

The following scenarios have not been executed and must not be reported as passing results.

| Proposed scenario | Test design | Expected result | Why it remains design only |
|---|---|---|---|
| Login over a genuine remote session | Connect through an approved remote-session platform, enter a synthetic account, sign in, sign out, reconnect, and repeat using keyboard-only input | Authentication feedback, masking, focus, and role behavior match the local baseline; reconnect does not restore a signed-out workspace | No remote platform or separate endpoint is provisioned |
| Natural session timeout | Sign in, remain inactive through the configured token lifetime, then request protected data and attempt one mutation | The expired session is rejected, stale state is cleared, and no mutation occurs until reauthentication | Invalid-token behavior was simulated, but elapsed expiry was not awaited |
| Controlled latency | Apply approved local network shaping at representative delay levels, then exercise login, search, and one task mutation without repeated clicks | Pending/error feedback remains understandable, no duplicate mutation occurs, and the final persisted state is unambiguous | No controlled latency profile was executed |
| Disconnect during login response | Interrupt connectivity after submitting valid synthetic credentials and restore it before retry | The interface does not claim success without a confirmed response and a retry creates only one usable session state | Existing interruption coverage targets task creation, not login |
| Remote reconnect after endpoint sleep | Disconnect the remote display while leaving the application session active, reconnect, and verify identity, data, focus, and authorization | Reconnect does not change role, expose another desktop session, repeat an action, or lose confirmed data | No remote display/session host exists in the project |
| Shared-endpoint security review | Review clipboard, screen capture, local token storage, saved credentials, session locking, logs, and sign-out behavior under the selected platform policy | Credentials and tokens are not exposed beyond the approved endpoint/session boundary, and sign-out or lock behavior follows policy | Requires an organization-specific platform and security baseline |

If these scenarios are executed later, each requires an approved requirement or case version, a recorded environment and latency profile, synthetic data, actual results, and retained evidence before its status changes from design only.

## Timeout and persistence distinction

WorkBoard issues time-limited access tokens and handles invalid or expired tokens through the same recovery path. Current testing verifies an invalid-token response and session cleanup, but it does not wait through the configured lifetime to prove natural expiration timing.

A browser refresh and a remote-session reconnect are also different events. Refresh reloads the application in the same browser profile. Reconnecting to a remote desktop can introduce platform-specific session locking, display restoration, clipboard, process-lifetime, and network behavior. The local refresh result must not be used as evidence that those platform behaviors passed.

## Latency-sensitive behavior

Future latency testing should use an isolated local environment and record the exact delay, jitter, loss, browser, endpoint, and test-data identifiers. At minimum it should observe:

- whether sign-in and task controls communicate pending or failed work clearly;
- whether repeated activation can create duplicate records;
- whether search and filtering display a consistent final state;
- whether a timed-out request can later appear successful without reconciliation;
- whether keyboard focus and error announcements remain usable while feedback is delayed.

Delay thresholds should come from an approved service or user-experience requirement. Inventing a target after observing results would not create meaningful acceptance evidence.

## Authentication and authorization checks

Remote-session testing does not replace backend security testing. A future execution should confirm:

1. valid and invalid credentials receive the same approved behavior as local execution;
2. protected requests without a valid token return the expected denial;
3. reconnecting does not elevate a member to administrator or change task ownership;
4. interrupted mutations leave database state consistent with the response shown to the user;
5. sign-out clears the application session and refresh or reconnect does not reopen the workspace;
6. evidence contains no password, reusable token, customer data, or unrestricted screen capture.

The implemented API and database authorization controls are documented in [TEST_STRATEGY.md](../TEST_STRATEGY.md), with current results in [TEST_SUMMARY_REPORT.md](../TEST_SUMMARY_REPORT.md).

## Security considerations

- Use synthetic identities and temporary credentials only.
- Do not test through an unapproved public relay, production VPN, customer environment, or shared account.
- Apply transport encryption, endpoint locking, clipboard, file-transfer, screen-capture, and credential-storage rules from the selected remote platform before execution.
- Mask credentials and tokens in screenshots, video, logs, reports, and defect attachments.
- Verify authorization at the API and database layers; a visually restored screen is not proof that access remains correct.
- Record whether disconnect closes, locks, or merely hides the remote session because each behavior changes the security expectation.
- Treat remote-platform outages separately from product defects unless WorkBoard violates an approved recovery requirement.

Local WorkBoard uses loopback HTTP and is not exposed as a secured remote service. No transport-security or remote-endpoint hardening claim is made.

## Future execution record

Before converting a design-only scenario into execution evidence, record:

- remote platform and version;
- client and host operating systems;
- browser and version;
- connection path and approved security controls;
- latency, jitter, and loss settings when applicable;
- token/session configuration;
- synthetic test data and cleanup method;
- expected and actual results;
- screenshots or logs with secrets removed;
- defect, retest, and regression links when applicable.

Until those fields and observed results exist, the final supported statement remains: local WorkBoard checks passed for refresh, simulated interruption, reconnection, false-success prevention, and authorization consistency only.
