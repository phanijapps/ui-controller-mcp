from __future__ import annotations

import base64
import os
from typing import Any, Dict, List, Optional

from ollama import Client


class AIClient:
    """Client for interacting with Ollama models for vision and reasoning."""

    def __init__(self, vision_model: str = "llama3.2-vision", planning_model: str = "llama3.2"):
        self.vision_model = os.getenv("OLLAMA_VISION_MODEL", vision_model)
        self.planning_model = os.getenv("OLLAMA_PLANNING_MODEL", planning_model)
        self.client = Client(host=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"))

    def analyze_image(self, image_data: str, instruction: str = "") -> str:
        """
        Analyze an image using a vision model.

        Args:
            image_data: Base64 encoded image data.
            instruction: Optional instruction to focus the analysis.

        Returns:
            A text description of the image and UI elements.
        """
        prompt = (
            f"Analyze this UI screenshot. {instruction}\n"
            "Describe the visible interactive elements, their approximate locations, and the overall context. "
            "Be specific about buttons, input fields, and text."
        )

        try:
            response = self.client.chat(
                model=self.vision_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                        "images": [image_data],
                    }
                ],
            )
            return response["message"]["content"]
        except Exception as e:
            return f"Error analyzing image: {str(e)}"

    def plan_action(self, analysis: str, goal: str) -> str:
        """
        Plan the next action based on the UI analysis and the user's goal.

        Args:
            analysis: The analysis of the current UI state.
            goal: The user's ultimate goal.

        Returns:
            A plan describing the next step and coordinates.
        """
        prompt = (
            f"Current UI State Analysis:\n{analysis}\n\n"
            f"User Goal: {goal}\n\n"
            "Based on the UI state and the goal, determine the single next immediate action to take. "
            "Return the plan in a clear, step-by-step format. "
            "If you need to click something, specify the element and its approximate location if known. "
            "If you need to type something, specify the text."
        )

        try:
            response = self.client.chat(
                model=self.planning_model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    }
                ],
            )
            return response["message"]["content"]
        except Exception as e:
            return f"Error planning action: {str(e)}"
