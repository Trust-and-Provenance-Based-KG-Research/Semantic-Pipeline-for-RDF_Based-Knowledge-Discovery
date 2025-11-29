"""
LLM service for description generation based on retrieved context.
Uses Groq LLaMA to summarize top-k context and updates metadata JSON.
"""

import requests
from datetime import datetime
from app.config.core_config import GROQ_API_KEY, GROQ_MODEL_NAME
from app.services.metadata_service import MetadataService


class LLMService:
    def __init__(self):
        self.metadata_service = MetadataService()
        # Groq’s OpenAI-compatible Chat Completions endpoint
        self.groq_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model_name = GROQ_MODEL_NAME

    def generate_description(self, metadata_path: str, retrieval_result: dict, top_k: int = 1):
        """
        Generate a 150–200 word description using retrieved context (no re-querying Chroma).

        Steps:
          1. Extract namespace and context from retrieval_result.
          2. Generate description via Groq LLaMA.
          3. Update metadata JSON with description.
        """
        namespace = retrieval_result.get("namespace")
        context = retrieval_result.get("context", "").strip()

        if not namespace:
            raise ValueError("Missing 'namespace' in retrieval_result.")
        if not context:
            raise ValueError("Missing 'context' text for description generation.")

        # Generate the description text
        description = self.generate_summary_from_context(context)

        # Update metadata JSON with description
        self.metadata_service.update_metadata_field(metadata_path, "description", description)

        return {
            "namespace": namespace,
            "description": description,
            "updated_at": datetime.utcnow().isoformat() + "Z",
        }

    def generate_summary_from_context(
        self,
        context: str,
        target_word_min: int = 150,
        target_word_max: int = 200,
    ) -> str:
        """
        Given retrieved context, call Groq LLaMA API to produce a 150–200 word summary.
        Returns the plain description text.
        """
        if not context.strip():
            raise ValueError("Empty context received for summarization.")

        prompt = (
            f"Using the content below, write a clear, neutral {target_word_min}–{target_word_max}-word "
            "description of the resource. Focus on its main ideas, purpose, and key points.\n\n"
            "CONTENT START\n"
            f"{context}\n"
            "CONTENT END\n\n"
            "Provide only the description text as your answer (no headings, bullets, or JSON)."
        )

        headers = {
            "Authorization": f"Bearer {GROQ_API_KEY}",
            "Content-Type": "application/json",
        }

        # Payload structure per Groq documentation
        payload = {
            "model": self.model_name,
            "messages": [
                {"role": "system", "content": "You are a helpful summarization assistant."},
                {"role": "user", "content": prompt},
            ],
            "temperature": 0.2,
            "max_tokens": 800,
            "stream": False,
        }

        # Send request to Groq API
        resp = requests.post(self.groq_url, json=payload, headers=headers, timeout=120)

        # Debugging in case of bad request or key/model mismatch
        if resp.status_code != 200:
            print("\n--- Groq API Error ---")
            print("Status Code:", resp.status_code)
            print("Response:", resp.text)
            print("----------------------\n")

        resp.raise_for_status()
        out = resp.json()

        try:
            return out["choices"][0]["message"]["content"].strip()
        except Exception as e:
            raise RuntimeError(f"Unexpected Groq API response format: {out}") from e
