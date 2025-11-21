class OpenAIHelper:
    @staticmethod
    def extract_output_text(response):
        for item in response.output:
            # Only pick message items that contain text
            if hasattr(item, "content") and item.content:
                # Extract first text block
                for c in item.content:
                    if hasattr(c, "text") and c.text:
                        return c.text

        raise ValueError("No valid text content found in response")
