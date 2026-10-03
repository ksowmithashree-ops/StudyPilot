import json
import logging

from config import GEMINI_API_KEY, GEMINI_MODEL, GEMINI_TIMEOUT_SECONDS

logger = logging.getLogger(__name__)


def gemini_available():
    return bool(GEMINI_API_KEY)


def _extract_json(text):
    text = (text or "").strip()
    if text.startswith("```"):
        text = text.strip("`")
        if text.startswith("json"):
            text = text[4:]
        text = text.strip()
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1:
        start = text.find("[")
        end = text.rfind("]")
    if start == -1 or end == -1:
        raise ValueError("No JSON in Gemini response")
    return json.loads(text[start : end + 1])


def generate_text(prompt, json_mode=False):
    if not gemini_available():
        return None
    try:
        import google.generativeai as genai

        genai.configure(api_key=GEMINI_API_KEY)
        model = genai.GenerativeModel(GEMINI_MODEL)
        response = model.generate_content(
            prompt,
            request_options={"timeout": GEMINI_TIMEOUT_SECONDS},
        )
        text = (response.text or "").strip()
        if json_mode:
            return _extract_json(text)
        return text
    except Exception as exc:
        logger.warning("Gemini failed, using fallback: %s", exc)
        return None
