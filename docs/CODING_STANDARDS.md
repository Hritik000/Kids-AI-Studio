# Coding Standards & Best Practices — KidsAI Studio

## General Principles
1. **Strict Typing**: Use TypeScript strict mode in Next.js and Pydantic validation in FastAPI.
2. **Provider Decoupling**: AI model calls must go through `LLMAdapter`, `ImageAdapter`, and `TTSAdapter`.
3. **No Blocking Calls**: Use async/await (`asyncio.sleep`) in Python event loops. Never use synchronous `time.sleep()`.
4. **Standardized Responses**: All REST APIs must return `APIResponse[T]` schema.
5. **No Hardcoded Prompts**: Prompts belong in `/packages/prompts/*.md`.
6. **No Swallow Errors**: Log all exceptions with traceback and return standardized error envelopes.
