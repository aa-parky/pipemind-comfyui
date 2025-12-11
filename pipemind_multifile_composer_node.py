import re
import random
from typing import Tuple, Dict


class MultiFileKeywordPromptComposer:
    """
    ComfyUI node for composing prompts with multiple keyword data sources.

    Supports:
    - Dynamic prompts: {option1|option2|option3}
    - Advanced syntax: {2$$ and $$option1|option2|option3}
    - Multiple keyword sources (up to 5 inputs)
    - Placeholder replacement: <key> with values from keyword_data
    """

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_template": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": (
                            "A <adjective> portrait of a <subject> "
                            "wearing <clothing> with {blue|green|brown} eyes."
                        ),
                    },
                ),
                "seed": (
                    "INT",
                    {"default": -1, "min": -1, "max": 2**31 - 1, "step": 1},
                ),
            },
            "optional": {
                "keyword_data_1": ("STRING", {"forceInput": True}),
                "keyword_data_2": ("STRING", {"forceInput": True}),
                "keyword_data_3": ("STRING", {"forceInput": True}),
                "keyword_data_4": ("STRING", {"forceInput": True}),
                "keyword_data_5": ("STRING", {"forceInput": True}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("composed_prompt",)
    FUNCTION = "compose_prompt"
    CATEGORY = "🧵 Pipemind"

    def __init__(self):
        self.dynamic_prompt_pattern = re.compile(r"\{([^{}]+)\}")

    def parse_dynamic_prompts(self, text: str, seed: int = -1) -> str:
        """
        Parse and replace dynamic prompt syntax with random selections.

        Args:
            text (str): Text containing dynamic prompt syntax
            seed (int): Random seed for deterministic selection (-1 for random)

        Returns:
            str: Text with dynamic prompts resolved
        """
        if seed != -1:
            random.seed(seed)

        def replace_dynamic_prompt(match):
            options_str = match.group(1)

            # Handle advanced syntax like {2$$ and $$option1|option2|option3}
            if "$$" in options_str:
                return self._handle_advanced_syntax(options_str)

            # Simple syntax: {option1|option2|option3}
            options = [opt.strip() for opt in options_str.split("|")]
            if options:
                return random.choice(options)
            return match.group(0)  # Return original if no options found

        # Replace all dynamic prompt patterns
        result = self.dynamic_prompt_pattern.sub(replace_dynamic_prompt, text)
        return result

    def _handle_advanced_syntax(self, options_str: str) -> str:
        """
        Handle advanced syntax like {2$$ and $$option1|option2|option3}

        Args:
            options_str (str): The content inside the curly braces

        Returns:
            str: Processed result
        """
        # Pattern for {N$$ separator $$option1|option2|option3}
        advanced_pattern = re.compile(r"(\d+)\$\$\s*(.+?)\s*\$\$(.+)")
        match = advanced_pattern.match(options_str)

        if match:
            count = int(match.group(1))
            separator = match.group(2)
            options_part = match.group(3)

            options = [opt.strip() for opt in options_part.split("|")]
            if len(options) >= count:
                selected = random.sample(options, min(count, len(options)))
                return separator.join(selected)

        # Fallback to simple syntax if advanced parsing fails
        options = [opt.strip() for opt in options_str.split("|")]
        if options:
            return random.choice(options)
        return f"{{{options_str}}}"  # Return original if parsing fails

    def _parse_keyword_data(self, data: str) -> Dict[str, str]:
        """
        Parse keyword data string into a dictionary.

        Supports both single-line "key=value" and multi-line formats:
        - Single: "key=value"
        - Multi: "key1=value1\nkey2=value2"

        Args:
            data (str): Keyword data string

        Returns:
            Dict[str, str]: Dictionary of key-value pairs
        """
        if not data or not isinstance(data, str):
            return {}

        keywords = {}
        lines = data.strip().split("\n")

        for line in lines:
            line = line.strip()
            if not line or "=" not in line:
                continue

            # Split on first '=' to allow values to contain '='
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip()

            if key:  # Only add if key is non-empty
                keywords[key] = value

        return keywords

    def _merge_keyword_dicts(self, *dicts: Dict[str, str]) -> Dict[str, str]:
        """
        Merge multiple keyword dictionaries.

        Later dictionaries override earlier ones for conflicting keys.

        Args:
            *dicts: Variable number of keyword dictionaries

        Returns:
            Dict[str, str]: Merged dictionary
        """
        merged = {}
        for d in dicts:
            if d:
                merged.update(d)
        return merged

    def _replace_placeholders(self, text: str, keywords: Dict[str, str]) -> str:
        """
        Replace all <key> placeholders in text with values from keywords.

        Args:
            text (str): Text containing placeholders
            keywords (Dict[str, str]): Key-value pairs for replacement

        Returns:
            str: Text with placeholders replaced
        """
        result = text
        for key, value in keywords.items():
            placeholder = f"<{key}>"
            result = result.replace(placeholder, value)
        return result

    def compose_prompt(
        self,
        prompt_template: str,
        seed: int = -1,
        keyword_data_1: str = "",
        keyword_data_2: str = "",
        keyword_data_3: str = "",
        keyword_data_4: str = "",
        keyword_data_5: str = "",
    ) -> Tuple[str]:
        """
        Compose a prompt by:
        1. Processing dynamic prompts {option1|option2|option3}
        2. Merging all keyword data sources
        3. Replacing placeholders <key> with values

        Args:
            prompt_template (str): Template with dynamic prompts/placeholders
            seed (int): Random seed for deterministic selection
            keyword_data_1-5 (str): Keyword data in "key=value" format

        Returns:
            Tuple[str]: The composed prompt
        """
        # Step 1: Process dynamic prompts first
        processed_template = self.parse_dynamic_prompts(prompt_template, seed)

        # Step 2: Parse all keyword data inputs
        keyword_dicts = [
            self._parse_keyword_data(keyword_data_1),
            self._parse_keyword_data(keyword_data_2),
            self._parse_keyword_data(keyword_data_3),
            self._parse_keyword_data(keyword_data_4),
            self._parse_keyword_data(keyword_data_5),
        ]

        # Step 3: Merge all keyword dictionaries (later ones override earlier)
        merged_keywords = self._merge_keyword_dicts(*keyword_dicts)

        # Step 4: Replace placeholders
        if merged_keywords:
            composed_prompt = self._replace_placeholders(
                processed_template, merged_keywords
            )
        else:
            composed_prompt = processed_template

        return (composed_prompt,)


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "MultiFileKeywordPromptComposer": MultiFileKeywordPromptComposer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "MultiFileKeywordPromptComposer": "🧵 Multi-File Keyword Composer",
}
