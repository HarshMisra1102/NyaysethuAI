import asyncio

from google import genai

from app.core.config import get_settings


class AIProviderUnavailableError(RuntimeError):
    """The configured AI provider cannot serve a generation request."""


class GeminiClient:
    """
    Central Gemini generation client for NyayaSetu AI.

    Features:
    - Automatically discovers available models
    - Prefers Flash models
    - Caches the selected model
    - Automatically falls back to another model
      when a selected model is temporarily unavailable
    """

    PREFERRED_MODELS = [
        "gemini-3.8-flash",
        "gemini-3.7-flash",
        "gemini-3.6-flash",
        "gemini-3.5-flash",
    ]

    def __init__(self):
        settings = get_settings()

        if not settings.gemini_api_key:
            raise RuntimeError(
                "GEMINI_API_KEY is not configured."
            )

        self.client = genai.Client(
            api_key=settings.gemini_api_key
        )

        self.model = None
        self.available_models = []

    async def discover_models(self) -> list[str]:
        """
        Discover models available to the current API key
        that support generateContent.
        """

        models = []

        for model in self.client.models.list():

            if not model.name:
                continue

            model_name = model.name.removeprefix(
                "models/"
            )

            supported_actions = (
                model.supported_actions or []
            )

            if (
                "generateContent"
                in supported_actions
            ):
                models.append(model_name)

        if not models:
            raise RuntimeError(
                "No Gemini models supporting "
                "generateContent are available."
            )

        self.available_models = models

        return models

    async def _get_model(self) -> str:
        """
        Return the best available model.
        """

        if self.model:
            return self.model

        available = await self.discover_models()

        # First preference: explicitly preferred models.
        for preferred in self.PREFERRED_MODELS:

            if preferred in available:

                self.model = preferred

                print(
                    f"[Gemini] Selected model: "
                    f"{self.model}"
                )

                return self.model

        # Second preference: any Flash model.
        flash_models = [
            model
            for model in available
            if "flash" in model.lower()
        ]

        if flash_models:

            flash_models.sort(
                reverse=True
            )

            self.model = flash_models[0]

            print(
                f"[Gemini] Fallback model: "
                f"{self.model}"
            )

            return self.model

        # Final fallback.
        self.model = available[0]

        print(
            f"[Gemini] Final fallback model: "
            f"{self.model}"
        )

        return self.model

    async def _select_fallback_models(
        self,
        failed_model: str,
    ) -> list[str]:
        """
        List alternatives after a temporary generation failure.

        Stable, explicitly preferred models are tried before generic
        Flash models and preview releases.
        """

        available = await self.discover_models()

        candidates = [
            model
            for model in available
            if model != failed_model
        ]

        preferred_candidates = [
            model
            for model in self.PREFERRED_MODELS
            if model in candidates
        ]

        stable_flash_candidates = [
            model
            for model in candidates
            if (
                "flash" in model.lower()
                and "preview" not in model.lower()
                and model not in preferred_candidates
            )
        ]

        preview_flash_candidates = [
            model
            for model in candidates
            if "flash" in model.lower() and "preview" in model.lower()
        ]

        remaining_candidates = [
            model
            for model in candidates
            if (
                model not in preferred_candidates
                and model not in stable_flash_candidates
                and model not in preview_flash_candidates
            )
        ]

        stable_flash_candidates.sort(reverse=True)
        preview_flash_candidates.sort()
        remaining_candidates.sort()

        return (
            preferred_candidates
            + stable_flash_candidates
            + preview_flash_candidates
            + remaining_candidates
        )

    async def generate(
        self,
        prompt: str,
        temperature: float = 0.2,
    ) -> str:

        if not prompt or not prompt.strip():
            raise ValueError(
                "Prompt cannot be empty."
            )

        model = await self._get_model()

        try:

            response = (
                await self.client.aio.models.generate_content(
                    model=model,
                    contents=prompt,
                    config={
                        "temperature": temperature,
                    },
                )
            )

            if not response.text:
                raise RuntimeError(
                    "Gemini returned an empty response."
                )

            return response.text.strip()

        except Exception as first_error:

            error_message = str(
                first_error
            ).lower()

            temporary_failure = (
                "503" in error_message
                or "unavailable" in error_message
                or "high demand" in error_message
                or "overloaded" in error_message
            )

            if not temporary_failure:
                raise AIProviderUnavailableError(
                    "Gemini could not process the request."
                ) from first_error

            print(
                f"[Gemini] Model {model} "
                f"is temporarily unavailable."
            )

            fallback_models = await self._select_fallback_models(
                failed_model=model
            )

            if not fallback_models:
                raise AIProviderUnavailableError(
                    "Gemini is temporarily unavailable."
                ) from first_error

            last_error: Exception = first_error

            for fallback_model in fallback_models:
                print(
                    f"[Gemini] Trying fallback model: "
                    f"{fallback_model}"
                )

                # Small delay to avoid immediately hammering the API again.
                await asyncio.sleep(1)

                try:
                    response = (
                        await self.client.aio.models.generate_content(
                            model=fallback_model,
                            contents=prompt,
                            config={
                                "temperature": temperature,
                            },
                        )
                    )
                    if not response.text:
                        raise RuntimeError("Gemini returned an empty response.")
                except Exception as fallback_error:
                    last_error = fallback_error
                    continue

                self.model = fallback_model

                print(
                    f"[Gemini] Successfully switched to: "
                    f"{fallback_model}"
                )

                return response.text.strip()

            raise AIProviderUnavailableError(
                "Gemini is temporarily unavailable or its quota "
                "has been exhausted. Please try again later."
            ) from last_error
