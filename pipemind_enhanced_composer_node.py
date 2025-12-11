import re
import random
from typing import Tuple


class EnhancedKeywordPromptComposer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_template": (
                    "STRING",
                    {
                        "multiline": True,
                        "default": "A beautiful portrait of a person wearing <clothing> with {blue|red|green} eyes.",
                    },
                ),
                "keyword_data": ("STRING", {"forceInput": True}),
                "seed": (
                    "INT",
                    {"default": -1, "min": -1, "max": 2**31 - 1, "step": 1},
                ),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("composed_prompt",)
    FUNCTION = "compose_prompt"
    CATEGORY = "Pipemind/Text"

    def __init__(self):
        self.dynamic_prompt_pattern = re.compile(r"\{([^{}]+)\}")

    def parse_dynamic_prompts(self, text: str, seed: int = -1) -> str:
        """
        Parse and replace dynamic prompt syntax {option1|option2|option3} with random selections.

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

    def compose_prompt(
        self, prompt_template: str, keyword_data: str, seed: int = -1
    ) -> Tuple[str]:
        """
        Compose a prompt by:
        1. Processing dynamic prompts {option1|option2|option3}
        2. Replacing placeholders <key> with values from keyword_data

        Args:
            prompt_template (str): Template with dynamic prompts and placeholders
            keyword_data (str): Key-value pairs in "key=value" format
            seed (int): Random seed for deterministic selection

        Returns:
            Tuple[str]: The composed prompt
        """
        # Step 1: Process dynamic prompts first
        processed_template = self.parse_dynamic_prompts(prompt_template, seed)

        # Step 2: Handle traditional placeholder replacement
        if "=" not in keyword_data:
            # Return the template with dynamic prompts processed but placeholders unmodified
            return (processed_template,)

        # Split the data into key and value
        key, value = keyword_data.split("=", 1)
        key = key.strip()
        value = value.strip()

        # Create the placeholder string to search for, e.g., "<clothing>"
        placeholder = f"<{key}>"

        # Replace the placeholder in the template with the value
        composed_prompt = processed_template.replace(placeholder, value)

        return (composed_prompt,)


# Alternative implementation using the dynamicprompts library
# Uncomment this if you want to use the full dynamicprompts library instead

"""
try:
    from dynamicprompts.generators import RandomPromptGenerator
    from dynamicprompts.wildcards import WildcardManager
    
    class AdvancedKeywordPromptComposer:
        @classmethod
        def INPUT_TYPES(cls):
            return {
                "required": {
                    "prompt_template": ("STRING", {
                        "multiline": True,
                        "default": "A beautiful portrait of a person wearing <clothing> with {blue|red|green} eyes."
                    }),
                    "keyword_data": ("STRING", {"forceInput": True}),
                    "seed": ("INT", {
                        "default": -1,
                        "min": -1,
                        "max": 2**31 - 1,
                        "step": 1
                    }),
                }
            }

        RETURN_TYPES = ("STRING",)
        RETURN_NAMES = ("composed_prompt",)
        FUNCTION = "compose_prompt"
        CATEGORY = "Pipemind/Text"

        def __init__(self):
            self.wildcard_manager = WildcardManager()
            self.generator = RandomPromptGenerator(wildcard_manager=self.wildcard_manager)

        def compose_prompt(self, prompt_template: str, keyword_data: str, seed: int = -1) -> Tuple[str]:
            # Process dynamic prompts using the dynamicprompts library
            if seed != -1:
                import random
                random.seed(seed)
            
            # Generate dynamic prompt
            prompts = self.generator.generate(prompt_template, num_images=1)
            processed_template = prompts[0] if prompts else prompt_template
            
            # Handle traditional placeholder replacement
            if "=" not in keyword_data:
                return (processed_template,)

            key, value = keyword_data.split("=", 1)
            key = key.strip()
            value = value.strip()
            placeholder = f"<{key}>"
            composed_prompt = processed_template.replace(placeholder, value)

            return (composed_prompt,)

except ImportError:
    # Fallback to the simple implementation if dynamicprompts is not available
    AdvancedKeywordPromptComposer = EnhancedKeywordPromptComposer
"""


# Node mappings for ComfyUI
NODE_CLASS_MAPPINGS = {
    "EnhancedKeywordPromptComposer": EnhancedKeywordPromptComposer,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "EnhancedKeywordPromptComposer": "Enhanced Keyword Prompt Composer",
}
