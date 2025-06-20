# pipemind_show_text_find.py
class PipemindShowTextFind:
    @classmethod
    def INPUT_TYPES(s):
        return {
            "required": {
                "text": ("STRING", {"forceInput": True}),
                "search_term": ("STRING", {
                    "default": "",
                    "multiline": False,
                    "placeholder": "Enter search term..."
                }),
                "case_sensitive": ("BOOLEAN", {"default": False}),
                "whole_word": ("BOOLEAN", {"default": False}),
            },
            "hidden": {
                "unique_id": "UNIQUE_ID",
                "extra_pnginfo": "EXTRA_PNGINFO",
            },
        }

    INPUT_IS_LIST = True
    RETURN_TYPES = ("STRING", "STRING",)
    RETURN_NAMES = ("text", "search_results",)
    FUNCTION = "show_and_find"
    OUTPUT_NODE = True
    OUTPUT_IS_LIST = (True, True,)
    CATEGORY = "Pipemind"

    def show_and_find(self, text, search_term, case_sensitive, whole_word, unique_id=None, extra_pnginfo=None):
        # Debug input
        print(f"Raw text input: {repr(text)}")
        print(f"Raw search term: {repr(search_term)}")

        # Handle text input
        if isinstance(text, list):
            text_to_search = text[0]
        else:
            text_to_search = text

        # Handle search term
        if isinstance(search_term, list):
            term = search_term[0]
        else:
            term = search_term

        term = str(term).strip()

        print(f"Processed search term: {repr(term)}")

        if not term:
            return (text, ["No search term provided"])

        # Split text into lines
        lines = text_to_search.split('\n')
        search_results = []

        print("\nSearching through lines:")
        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Extract just the value after '=' if it exists
            parts = line.split('=')
            if len(parts) > 1:
                search_in = parts[1].rstrip(',').strip()
            else:
                search_in = line

            # Prepare strings for comparison
            search_in = search_in.lower() if not case_sensitive else search_in
            search_for = term.lower() if not case_sensitive else term

            print(f"\nChecking line: {repr(line)}")
            print(f"Extracted value: {repr(search_in)}")
            print(f"Comparing with: {repr(search_for)}")

            if whole_word:
                words = search_in.split()
                if search_for in words:
                    print("Found match (whole word)!")
                    search_results.append(line)
            else:
                if search_for == search_in:  # Using exact match for the value
                    print("Found match!")
                    search_results.append(line)

        # Prepare results
        if search_results:
            final_results = [f"Found {len(search_results)} matches:\n" + "\n".join(search_results)]
        else:
            final_results = ["No matches found"]

        print(f"\nFinal search results: {repr(final_results)}")

        return (text, final_results)