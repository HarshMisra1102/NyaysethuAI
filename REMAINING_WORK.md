# NyayaSetu-AI — Remaining Work Report

## Current baseline

The project has a Next.js 15 frontend and a FastAPI backend. Working backend capabilities currently include JWT registration/login, authenticated case CRUD, case-bound AI chat, rights analysis, RTI draft generation, scheme eligibility guidance, and PDF/TXT ingestion.

The frontend contains routes for these capabilities and uses a centralized API client. It also includes clear UI messaging where an expected API is not available.

## Priority 1 — Backend work

### Document library and document operations

The backend only provides `POST /api/v1/documents/upload`. Add authenticated, user-scoped endpoints for:

- Listing documents, including processing status and pagination.
- Fetching a document's metadata and analysis status.
- Downloading a document only when the requesting user has access.
- Deleting documents and their associated chunks/storage safely.
- Optional document preview or extracted-text endpoint, with authorization checks.

This unlocks a real Documents library, filtering, search, processing-state recovery, document management, and document-specific UI flows.

### Chat history and conversation controls

`POST /api/v1/chat/query` creates or reuses a case conversation but no read APIs exist. Add user-scoped endpoints for:

- Listing conversations, with case context, title, and last activity.
- Fetching paginated messages for a conversation.
- Starting a new conversation for a case, if multiple conversations per case are supported.
- Renaming, clearing, and deleting conversations.
- Optional conversation search.

Also consider server-sent events or another streaming mechanism for AI responses. The current chat UI can only show a waiting state until a single final response arrives.

### User profile and account security

The API supports `GET /api/v1/auth/me` only. Add:

- Authenticated profile update endpoint for name, state, and district.
- Change-password flow with current-password verification.
- Token refresh and token revocation/logout strategy.
- Optional active-session list and session revocation.
- Email verification and password reset flows if required by the product.

Do not store long-lived sensitive tokens in browser local storage if a secure HTTP-only cookie/session design is adopted.

### Dashboard data

There is no aggregated dashboard endpoint. If product metrics are needed, provide a user-scoped summary endpoint containing only real data, for example case counts and recent cases. Do not add fabricated AI-usage statistics.

### Document analysis contract

Document ingestion succeeds, but no dedicated document analysis or question-answering endpoint is exposed. Define an explicit contract if document-specific analysis is a product feature:

- Request must identify a document or permitted document collection.
- Response should return summary, findings, relevant passages, citations, and processing state.
- Ensure the retrieval layer enforces document ownership/visibility.

### Reliability and operations

- Replace direct filesystem upload storage with configured persistent/object storage for deployments.
- Run ingestion asynchronously and expose durable `queued`, `processing`, `completed`, and `failed` status values.
- Avoid returning raw internal exception text in document-upload errors.
- Add rate limiting, request correlation IDs, structured production logging, and monitoring.
- Add endpoint integration tests for authorization boundaries, ownership, invalid input, and AI service failure paths.
- Complete project operational files: root `README.md`, `LICENSE`, and `docker-compose.yml` are currently empty.

## Priority 1 — Frontend work after API support

### Documents

Once document APIs exist, implement:

- Document list with loading, empty, error, pagination, and processing states.
- Search/filter by title, type, and status.
- Document details, safe preview/download, delete confirmation, and retry for failed processing.
- Document analysis results and cited passages.

### AI assistant

Once conversation APIs exist, implement:

- Conversation sidebar and history search.
- Restore messages after refresh and switch between conversations.
- New, clear, rename, and delete conversation actions.
- Streaming-response rendering when supported.
- Copy-answer action and regenerate action, only when an API supports regeneration.

### Profile and settings

Once account APIs exist, replace read-only notices with validated forms for profile, password, sessions, and account preferences.

## Priority 2 — Frontend quality improvements

- Add component-level or end-to-end tests for registration, login, protected-route behavior, case creation, AI chat errors, and upload validation.
- Add an accessible confirmation dialog component to replace native `confirm()` in case deletion.
- Add toast notifications for successful case creation, uploads, and logout.
- Add error boundaries for route-level unexpected errors.
- Add client-side API request cancellation where navigation can interrupt long AI/upload operations.
- Split currently compressed page components into reusable form/result components as the application grows.
- Use a local/self-hosted font strategy for production environments that cannot rely on Google Fonts.
- Add visual regression and mobile-browser checks.

## Priority 2 — UX/content work

- Review all AI-facing wording with a legal domain expert.
- Establish citation-quality rules and a source-link policy.
- Define supported languages and implement localization only after backend/content support is agreed.
- Conduct accessibility testing with keyboard-only and screen-reader user flows.
- Conduct privacy, retention, consent, and legal-disclaimer review before production release.

## Suggested delivery order

1. Complete backend document list/detail/delete/status APIs and authorization tests.
2. Complete backend conversation-history APIs and message pagination.
3. Add profile/security APIs and decide token/session architecture.
4. Build frontend document library and persisted conversation UX against those contracts.
5. Add tests, observability, documentation, and deployment configuration.
6. Perform legal, privacy, accessibility, and security reviews before launch.

## Not required until product decisions are made

- Real-time streaming chat.
- Multi-language support.
- Advanced search suggestions.
- Analytics/AI usage metrics.
- Collaborative workspaces or case sharing.

These should be designed from explicit product requirements rather than added as placeholder functionality.
