# Normalize Responses API Content Before Validation

Responses-style model clients may return structured content blocks instead of a plain string. Calling `str(reply.content)` serializes the block representation, which can make downstream prose validation reject a valid response and silently use a fallback.

Normalize every response through one shared text extractor before validation. The extractor should accept plain strings, text blocks, and provider-specific structured content, then return only the assistant's text.
