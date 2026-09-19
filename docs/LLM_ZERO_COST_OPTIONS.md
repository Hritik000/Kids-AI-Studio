# KidsAI Studio: Zero-Cost / Low-Cost LLM Options Audit

## Executive Summary
This audit evaluates zero-cost and low-cost options for running a **Real LLM** in KidsAI Studio during personal development without requiring paid OpenAI subscriptions. 

The backend architecture uses a clean `LLMProvider` abstraction (`app/core/llm.py`). Because `OpenAILLMProvider` communicates via standard REST calls using Python's built-in `httpx.AsyncClient`, the existing architecture can seamlessly integrate zero-cost cloud or local LLM providers without adding bloated dependencies or destabilizing the codebase.

---

## Architecture Compatibility
- **`app/core/llm.py`**: Defines abstract `LLMProvider` with `generate_json()` and `generate_text()`.
- **`OpenAILLMProvider`**: Built on generic HTTP/REST endpoints (`base_url`, `api_key`, `model`).
- **`MediaDownloader` & Async Pipeline**: Unaffected; LLM layer only produces validated JSON for Story and Storyboard agents.

---

## Detailed Provider Audit

### 1. Google Gemini API (Google AI Studio - Free Tier)

* **Code already exists**: No direct `GeminiLLMProvider` class in `llm.py`, but Google AI Studio exposes an **OpenAI-compatible REST endpoint** (`https://generativelanguage.googleapis.com/v1beta/openai/`) that works directly with `OpenAILLMProvider`.
* **Required environment variables**: `GEMINI_API_KEY`, `LLM_PROVIDER=gemini`, `GEMINI_MODEL=gemini-2.5-flash`.
* **API Key required**: Yes (`GEMINI_API_KEY` - free at [aistudio.google.com](https://aistudio.google.com)).
* **Uses GCP $300 credit**: No (uses Google AI Studio Free Tier, which is independent of GCP credits).
* **Zero ongoing cost for dev**: **YES, 100% $0 cost.** Free tier allows 15 Requests Per Minute (RPM), 1 Million Tokens Per Minute (TPM), and 1,500 Requests Per Day (RPD).
* **Model options**: `gemini-2.5-flash` (Recommended - ultra-fast, frontier-grade reasoning), `gemini-1.5-flash`, `gemini-1.5-pro`.
* **Required Python packages**: **None** (uses existing `httpx` package).
* **Required code changes**: 
  - Minimal update to `app/core/llm.py` to route `LLM_PROVIDER=gemini` to `OpenAILLMProvider(api_key=GEMINI_API_KEY, base_url="https://generativelanguage.googleapis.com/v1beta/openai/", model="gemini-2.5-flash")`.
* **Structured JSON support**: **Excellent.** Native support for `response_format={"type": "json_object"}`.
* **Integration difficulty**: **Very Low (Easy / < 15 mins).**

---

### 2. Google Cloud Vertex AI (Using GCP $300 Credit)

* **Code already exists**: No.
* **Required environment variables**: `GCP_PROJECT_ID`, `GCP_LOCATION` (e.g. `us-central1`), `GOOGLE_APPLICATION_CREDENTIALS` (or active Application Default Credentials).
* **API Key required**: No (uses GCP Service Account JSON or OAuth2 ADC credentials).
* **Uses GCP $300 credit**: **YES, 100%.** Charges draw directly from your active $300 GCP credit balance.
* **Zero ongoing cost for dev**: Yes, while within the $300 credit window. Afterwards, standard Vertex AI pay-per-token pricing applies.
* **Model options**: `gemini-2.5-flash`, `gemini-1.5-flash`, `gemini-1.5-pro`.
* **Required Python packages**: `google-genai` or `google-cloud-aiplatform` + `google-auth`.
* **Required code changes**: 
  - Add `VertexAILLMProvider` in `app/core/llm.py` handling OAuth2 token generation or Vertex REST endpoints (`https://{location}-aiplatform.googleapis.com/v1/...`).
* **Structured JSON support**: **Excellent.** Native `responseSchema` support.
* **Integration difficulty**: **Medium.** Requires GCP authentication, project permissions, and SDK setup.

---

### 3. Local Ollama (100% Offline & $0 Cost)

* **Code already exists**: No.
* **Required environment variables**: `OLLAMA_BASE_URL` (default: `http://localhost:11434`), `OLLAMA_MODEL` (e.g. `llama3.2`, `qwen2.5`), `LLM_PROVIDER=ollama`.
* **API Key required**: **NO.**
* **Uses GCP $300 credit**: No (runs locally on your machine).
* **Zero ongoing cost for dev**: **YES, 100% $0 cost indefinitely.**
* **Model options**: `llama3.2` (3B params), `qwen2.5` (7B/3B params), `mistral` (7B params).
* **Required Python packages**: **None** (Ollama exposes an OpenAI-compatible REST endpoint at `http://localhost:11434/v1/chat/completions`).
* **Required code changes**: 
  - Minimal update in `app/core/llm.py` to route `LLM_PROVIDER=ollama` to `OpenAILLMProvider(api_key="ollama", base_url="http://localhost:11434/v1", model="llama3.2")`.
* **Structured JSON support**: **Moderate to Good.** Supports JSON mode, but smaller 3B/7B open-weight models can occasionally omit nested keys compared to cloud models like Gemini Flash or GPT-4o-mini.
* **Integration difficulty**: **Low to Medium.** Requires installing Ollama on your local host Mac and running `ollama pull llama3.2`.

---

### 4. Groq Cloud API (Free Tier)

* **Code already exists**: No.
* **Required environment variables**: `GROQ_API_KEY`, `LLM_PROVIDER=groq`, `GROQ_MODEL=llama-3.3-70b-versatile`.
* **API Key required**: Yes (`GROQ_API_KEY` - free at [console.groq.com](https://console.groq.com)).
* **Uses GCP $300 credit**: No.
* **Zero ongoing cost for dev**: **YES, 100% $0 free tier** (30 RPM limit).
* **Model options**: `llama-3.3-70b-versatile`, `llama3-8b-8192`.
* **Required Python packages**: **None** (uses existing `httpx` via `https://api.groq.com/openai/v1`).
* **Required code changes**: Minimal routing in `llm.py`.
* **Structured JSON support**: **Good.**
* **Integration difficulty**: **Very Low.**

---

## Comparative Matrix

| Feature / Criteria | 1. Google Gemini API (AI Studio) | 2. GCP Vertex AI | 3. Local Ollama | 4. Groq Cloud API |
| :--- | :--- | :--- | :--- | :--- |
| **Existing Code** | Compatible REST | No | Compatible REST | Compatible REST |
| **Ongoing Cost** | **$0 (Free Tier)** | Consumes GCP $300 | **$0 (100% Local)** | **$0 (Free Tier)** |
| **GCP Credit Eligible**| No | **Yes ($300 Credit)** | No | No |
| **API Key Needed** | Yes (Free) | No (OAuth2/ADC) | **No** | Yes (Free) |
| **New PyPI Packages** | **None** | `google-genai` | **None** | **None** |
| **JSON Adherence** | **Superior** | **Superior** | Moderate | Good |
| **Setup Speed** | **< 15 Mins** | 30-45 Mins | 20 Mins (local run) | < 15 Mins |

---

## Recommendation for Personal Development Setup

### **RECOMMENDED: Option 1 — Google Gemini API (Google AI Studio Free Tier)**

**Why Option 1 is the best fit:**
1. **$0 Additional Cost**: Google AI Studio provides a free tier with 15 Requests Per Minute and 1,500 Requests Per Day for `gemini-2.5-flash`—more than enough for local development and testing.
2. **Zero Extra Dependencies**: Utilizes the Google AI Studio OpenAI-compatible endpoint (`https://generativelanguage.googleapis.com/v1beta/openai/`), so no new Python packages (`google-genai` or `google-cloud-aiplatform`) need to be installed.
3. **Superior Structured JSON Reliability**: Gemini 2.5 Flash / 1.5 Flash supports JSON mode natively with high adherence to complex story and storyboard schemas.
4. **Seamless Integration**: Directly plugs into our existing `LLMProvider` / `OpenAILLMProvider` in `app/core/llm.py`.

---

## Audit Status
Audit complete. No code changes, installations, or credential creation performed.
