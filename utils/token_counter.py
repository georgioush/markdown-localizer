import os
import tiktoken

class TokenCounter:
    def __init__(self, model_name=None):
        if model_name is None:
            self.model_name = os.getenv("AZURE_OPENAI_MODEL_NAME", "gpt-4o")
        else:
            self.model_name = model_name
        
        self.encoding = tiktoken.encoding_for_model(self.model_name)

    def count_tokens(self, text):
        return len(self.encoding.encode(text))

    def human_readable_size(self, byte_size):
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if byte_size < 1024:
                return f"{byte_size:.2f} {unit}"
            byte_size /= 1024

if __name__ == "__main__":
    # Example usage
    text = "Hello, this is a test."
    counter = TokenCounter()
    count = counter.count_tokens(text)
    print(f"Token count: {count}")
    print(f"Token count: {counter.human_readable_size(count)}")