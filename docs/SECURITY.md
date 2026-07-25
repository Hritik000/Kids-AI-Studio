# Security Architecture & COPPA Compliance — KidsAI Studio v2.0

## 1. Authentication & Bearer Tokens
- All API routes are protected using Supabase Auth JWT Bearer Token validation.
- Request headers require `Authorization: Bearer <token>`.

## 2. COPPA & Child Safety Verification
- **Safety First**: The KidsAI Studio platform strictly enforces Children's Online Privacy Protection Act (COPPA) guidelines.
- **Safety Audit**: SEO & Publishing Agent automatically verifies `coppa_compliant: True` before rendering or releasing any video content.
- **No Personal Data Collection**: No personal information or tracking identifiers are embedded in exported kids videos or publishing assets.

## 3. Developer API Key Security
- API keys are hashed and generated using secure cryptographic signatures (`kAI_live_...`).
- Scopes (`read`, `write`) enforce fine-grained access control.
