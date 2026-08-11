# Web-Services Testing: REST and SOAP

## Scope

WorkBoard implements and tests a REST API. SOAP is included only as a bounded design comparison so the repository demonstrates how request construction, authentication, validation, faults, and automation would differ. There is no SOAP endpoint and no SOAP result is reported as executed.

## Implemented REST approach

The reusable client in [`framework/clients/workboard_api.py`](../framework/clients/workboard_api.py) owns the base URL, resource paths, JSON requests, bearer-token headers, timeouts, and normalized service-error inspection. Tests in [`tests/api/test_workboard_api.py`](../tests/api/test_workboard_api.py) retain the raw response so each case can assert the exact contract.

The executed suite covers:

- `GET` health, profile, personal-task, and administrator-task reads;
- `POST` registration, login, and task creation;
- `PATCH` profile and task updates;
- `DELETE` task removal;
- bearer authentication and missing or invalid tokens;
- member ownership and administrator read-only boundaries;
- missing fields, invalid values, incorrect types, duplicate values, and unknown records;
- expected 2xx and 4xx responses plus a controlled 503 client-handling case;
- strict response structure and content through independent Pydantic contracts; and
- single-request local timing observations that are not load or production-capacity evidence.

Example REST request shape:

```http
POST /api/tasks HTTP/1.1
Host: 127.0.0.1:8000
Authorization: Bearer <temporary-token>
Content-Type: application/json

{
  "title": "Review release evidence",
  "description": "Confirm the selected quality gates passed."
}
```

A REST test validates the HTTP status, JSON content type, response object fields and types, values, authorization outcome, and expected database state. Error cases inspect the 4xx or controlled 5xx status and structured error content.

## REST and SOAP comparison

| Concern | WorkBoard REST test | Conceptual SOAP-style test |
|---|---|---|
| Operation address | HTTP method plus resource path | Service endpoint plus operation/action |
| Request construction | JSON body and query parameters | XML envelope with required namespaces and body element |
| Authentication | Bearer token in the HTTP `Authorization` header | Service-specific HTTP auth, certificate, or WS-Security header |
| Contract | HTTP status and independent JSON response model | WSDL operation plus XML Schema types and namespaces |
| Content validation | Parsed JSON keys, types, and values | Namespace-aware XML element, attribute, type, and value assertions |
| Success | Appropriate 2xx status and response representation | Valid response envelope and operation result |
| Error handling | 4xx/5xx status with structured error content | Transport error or a SOAP Fault with code, reason, and detail |
| Automation | Reusable HTTP client and pytest assertions | Reusable SOAP client or HTTP/XML helper and pytest assertions |

## Conceptual SOAP-style example

A comparable task-read request could look like this if a service contract defined a `GetTask` operation:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<soap:Envelope
  xmlns:soap="http://www.w3.org/2003/05/soap-envelope"
  xmlns:work="https://example.test/workboard/v1">
  <soap:Header>
    <work:SessionToken>temporary-synthetic-token</work:SessionToken>
  </soap:Header>
  <soap:Body>
    <work:GetTaskRequest>
      <work:TaskId>42</work:TaskId>
    </work:GetTaskRequest>
  </soap:Body>
</soap:Envelope>
```

The conceptual automated check would:

1. build the envelope with namespace-aware XML tools rather than string concatenation;
2. add the contract-required content type, action, and authentication material;
3. send the request with an explicit timeout;
4. separate HTTP transport failure from a returned SOAP Fault;
5. parse XML without unsafe external-entity processing;
6. validate the response against the service's XML Schema or generated contract types;
7. assert the expected namespace, operation element, task identifier, and values; and
8. sanitize credentials and message content before retaining evidence.

Conceptual pytest-style pseudocode:

```python
response = soap_client.call(
    action="GetTask",
    envelope=get_task_envelope(task_id=42),
    credentials=temporary_credentials,
)

assert response.transport_status == 200
assert response.fault is None
assert response.schema_valid
assert response.value("work:TaskId") == "42"
```

An error case would expect a contract-defined fault instead of assuming every service error is represented only by an HTTP status:

```python
assert response.fault.code == "work:TaskNotFound"
assert response.fault.reason == "The requested task does not exist."
```

The snippets describe test structure only. They are not connected to WorkBoard, were not executed, and are not included in any pass count.

## Why a SOAP service was not added

Adding an unused SOAP application would increase maintenance and create misleading breadth without improving the risks of the REST-based system under test. The portfolio instead demonstrates the implemented REST work in depth and documents the transferable SOAP testing model with a clear execution boundary.

The release evidence and counts remain limited to the REST suite recorded in [TEST_SUMMARY_REPORT.md](../TEST_SUMMARY_REPORT.md).
