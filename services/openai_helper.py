class OpenAIHelper:
    @staticmethod
    def extract_output_text(response):
        for item in response.output:
            if hasattr(item, "content") and item.content:
                for c in item.content:
                    if hasattr(c, "text") and c.text:
                        return c.text
        raise ValueError("No valid text content found in response")
