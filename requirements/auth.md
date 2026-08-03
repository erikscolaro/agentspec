# Module: Auth

<!-- EXAMPLE MODULE: shows the methodology applied. Adapt it to your project
     or delete it. It is the cross-cutting module par excellence: other modules
     reference it via depends_on and auth_required instead of repeating behavior. -->

```yaml
module: auth
status: draft
owner_dir: src/auth/
depends_on_modules: []
```

## Purpose

Manages authentication and authorization: token issuance and verification, roles, uniform behavior of protected routes. Every other module declares its required level with `auth_required` and references this module's REQs via `depends_on`, without repeating their behavior.

## Exposed routes

| Method | Path | Handler | REQ | Auth |
|---|---|---|---|---|
| POST | /auth/login | auth::handler::login | REQ-AUTH-001 | none |
| POST | /auth/refresh | auth::handler::refresh | REQ-AUTH-002 | none |

## Out of scope

- User registry management (creation, profile editing) → `users` module
- Access auditing → `security` module

## Domain entities

- `Session`: access_token, refresh_token, role, expiry
- `Role`: closed enumeration of application roles (e.g. tenant_admin, end_client)

## Invariant rules

- The access token is a signed, short-lived JWT; the refresh token is opaque and revocable
- No route distinguishes "unknown user" from "wrong password" in its response

## Module NFR constraints

- Token verification on protected routes adds no perceptible latency (no external service calls in the verification path)

## Local glossary

| Term | Definition |
|---|---|
| Protected route | Route whose REQ declares `auth_required` other than `none` |

---

## Requirements

### REQ-AUTH-001 - Login issues an access/refresh token pair

```yaml
id: REQ-AUTH-001
module: auth
type: functional
status: draft
priority: high
auth_required: none
aliases: [login, token-issuance]
```

**Description**

A registered user obtains an access token + refresh token pair by providing valid credentials.

**Acceptance criteria**

> **Scenario: login_returns_tokens_for_valid_credentials**
> - Given a registered, active user
> - When they send correct credentials to POST /auth/login
> - Then they receive 200 with an access token (JWT) and a refresh token, and the user's role is included in the claims

> **Scenario: login_rejects_bad_credentials_with_generic_401**
> - Given wrong credentials or a non-existent user
> - When they send the login request
> - Then they receive 401 with a generic message, identical in both cases

**Edge cases**

Deactivated user → 403, no token issued. Rate limiting on failed attempts (threshold defined at infrastructure level, not application level).

**Changelog**

- 2026-08-02: created (draft)

### REQ-AUTH-002 - Refresh token rotation

```yaml
id: REQ-AUTH-002
module: auth
type: functional
status: draft
priority: medium
auth_required: none
aliases: [refresh, token-renewal]
depends_on: [REQ-AUTH-001]
```

**Description**

A client with a valid refresh token obtains a new access token without re-entering credentials.

**Acceptance criteria**

> **Scenario: refresh_rotates_token_for_valid_refresh_token**
> - Given a valid, non-revoked refresh token
> - When it is sent to POST /auth/refresh
> - Then the client receives 200 with a new access token; the previous refresh token is invalidated (rotation)

> **Scenario: refresh_revokes_all_sessions_on_reused_token**
> - Given a revoked or already-used refresh token
> - When it is sent to POST /auth/refresh
> - Then the client receives 401 and all associated sessions are revoked

**Edge cases**

Expired refresh token → 401 without cascading revocation. Malformed token → 400.

**Changelog**

- 2026-08-02: created (draft)

### REQ-AUTH-003 - Protected routes require a valid JWT

```yaml
id: REQ-AUTH-003
module: auth
type: invariant
status: draft
priority: high
auth_required: none
aliases: [expired-token, 401-check, protected-route]
```

**Description**

Every route with `auth_required` other than `none` verifies the JWT in the Authorization header. This is the REQ that all modules reference via `depends_on` for protected-route behavior.

**Acceptance criteria**

> **Scenario: protected_route_rejects_missing_or_invalid_token**
> - Given a protected route and a request without a token, or with an expired/invalid token
> - When the request reaches the server
> - Then it responds 401 before executing any application logic

> **Scenario: protected_route_rejects_insufficient_role**
> - Given a valid token whose role is insufficient for the route
> - When the request reaches the server
> - Then it responds 403 without revealing details about the resource

**Edge cases**

Authorization header present but malformed (scheme other than Bearer) → 401, same behavior as a missing token.

**Changelog**

- 2026-08-02: created (draft)
