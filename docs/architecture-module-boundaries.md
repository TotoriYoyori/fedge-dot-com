# Module boundaries for non-CRUD logic (FastAPI)

This note proposes concrete boundaries for your current structure (`router`, `dependencies`, `service`, `security`, `schemas`) as your codebase grows beyond CRUD.

## 1) Proposed layering

Use this dependency direction:

`router -> application/use_case -> domain services/parsers/policies -> infrastructure adapters`

Supporting modules:

- `schemas`: API I/O contracts (request/response DTOs).
- `dependencies`: composition + request-scope wiring + auth gates.
- `settings`: environment-backed configuration.
- `exceptions`: app-level errors.

### Rule of thumb

- Upper layers may import lower layers.
- Lower layers should **not** import upper layers.
- `router` should never contain branching business rules.

## 2) `service` is too dense: split by role

When non-CRUD logic grows, split `service.py` into role-focused units:

- `application/` (or `use_cases/`): orchestration workflows.
  - Example: `initiate_google_oauth2`, `send_notification_email`.
- `domain/`:
  - `parsers/`: pure transforms (e.g., Gmail payload -> internal model).
  - `policies/`: business decisions (eligibility, retry, throttling rules).
- `infra/`:
  - adapters around external SDK/API clients and persistence.

This keeps orchestration visible while preventing a mega-service file.

## 3) Rename `security`? yes, with intent

Your instinct is good. If this module handles sensitive integration concerns (JWT, OAuth2, SDK signatures), use explicit naming.

Recommended split:

- `auth/security.py`: crypto/JWT primitives only.
- `google/gateway.py` or `google/client.py`: Google SDK calls.
- `google/oauth.py`: OAuth state/token flow logic.
- `settings.py`: only source of env values.

Do **not** make every module read env directly. Inject settings or adapters via dependency wiring.

## 4) Clear boundary for `dependencies`

Treat `dependencies` as **composition boundary**, not business logic storage.

Good in `dependencies`:

- `Depends()` providers (db/session/user/settings).
- authN/authZ guards (`require_role`).
- request-scoped object assembly.

Avoid in `dependencies`:

- multi-step business workflows.
- parser logic.
- external side-effects except object construction needed for DI.

If a dependency needs logic, call a use-case/policy function from there; keep the dependency itself thin.

## 5) How thin should routers be?

Your `oauth2` route example is correct in spirit.

Router responsibilities:

- endpoint metadata/docs/status codes.
- input extraction/validation.
- invoke one use-case (orchestrator).
- map domain/app exceptions to HTTP responses.

So a wrapper like `initiate_oauth2(...)` is not weird; it is desirable **if** it lives in an application/use-case module, not a random utility.

## 6) Where should internal schemas live?

Use two schema buckets:

- **API schemas** (`schemas.py`): request/response models exposed at HTTP boundary.
- **Internal models** (`domain/models.py` or `contracts.py`): non-IO structures used between parser/service/use-case layers.

For external SDK abstraction, define internal DTOs (e.g., `ParsedEmail`, `OAuthGrant`) and map SDK-specific types at the infra adapter boundary. This prevents SDK types from leaking across the app.

## 7) Practical target structure

Example for `google` module:

- `google/router.py` (HTTP only)
- `google/dependencies.py` (Depends providers + guards)
- `google/application/oauth_use_cases.py` (initiate/callback workflows)
- `google/domain/email_parser.py` (pure parse logic)
- `google/infra/google_client.py` (SDK adapter)
- `google/infra/oauth_state_repo.py` (persistence adapter)
- `google/schemas.py` (API schemas)
- `google/domain/models.py` (internal DTOs)
- `google/settings.py` (module settings)

## 8) Refactor sequence (safe + incremental)

1. Introduce `application/` and move one orchestration function (`initiate_oauth2`) there.
2. Extract one pure parser from `service.py` into `domain/parsers`.
3. Extract one SDK call path into `infra/google_client.py`.
4. Add tests per layer:
   - router tests (status + contracts),
   - use-case tests (orchestration with fakes),
   - parser tests (pure unit),
   - adapter tests (integration/minimal contract).
5. Repeat endpoint by endpoint.

This gives architecture clarity without a large risky rewrite.
