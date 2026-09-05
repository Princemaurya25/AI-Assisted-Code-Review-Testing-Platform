import re


def sanitize_code_input(code: str) -> str:
    """
    Sanitizes user submitted code to prevent prompt injection attacks.
    Removes system prompt overrides or delimiter escape sequences.
    """
    # Remove system prompt override attempts inside code comments
    sanitized = re.sub(
        r'(?i)(ignore previous instructions|reveal system prompt|system prompt:|you are now in system mode)',
        '[PROMPT_INJECTION_ATTEMPT_REMOVED]',
        code
    )
    return sanitized


def format_code_data_block(code: str, language: str, context: str = "") -> str:
    """
    Wraps code in explicit XML data tags so LLM treats it strictly as passive DATA.
    """
    clean_code = sanitize_code_input(code)
    clean_context = sanitize_code_input(context) if context else "None provided."

    data_block = f"""
<code_analysis_payload>
  <target_language>{language}</target_language>
  <additional_context>{clean_context}</additional_context>
  <user_source_code>
<![CDATA[
{clean_code}
]]>
  </user_source_code>
</code_analysis_payload>
"""
    return data_block
