class KeywordPromptComposer:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt_template": ("STRING", {
                    "multiline": True,
                    "default": "A beautiful portrait of a person wearing <clothing>."
                }),
                "keyword_data": ("STRING", {"forceInput": True}),
            }
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("composed_prompt",)
    FUNCTION = "compose_prompt"
    CATEGORY = "Pipemind/Text"

    def compose_prompt(self, prompt_template, keyword_data):
        """
        Replaces a placeholder in the template with a value from keyword_data.

        Args:
            prompt_template (str): The text containing a placeholder, e.g., "wearing <clothing>".
            keyword_data (str): A string in "key=value" format, e.g., "clothing=red shirt".
        """
        # If keyword_data does not contain '=', we cannot find a key-value pair.
        if "=" not in keyword_data:
            # Return the template unmodified to avoid breaking the workflow.
            return (prompt_template,)

        # Split the data into key and value.
        key, value = keyword_data.split("=", 1)
        key = key.strip()
        value = value.strip()

        # Create the placeholder string to search for, e.g., "<clothing>".
        placeholder = f"<{key}>"

        # Replace the placeholder in the template with the value.
        composed_prompt = prompt_template.replace(placeholder, value)

        return (composed_prompt,)

