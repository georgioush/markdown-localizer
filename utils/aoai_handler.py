import os
from openai import AzureOpenAI

class AOAIHandler:
    def __init__(self):
        self.api_key = os.getenv("AZURE_OPENAI_API_KEY")
        self.azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
        self.deployment_name = os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME")
        self.api_version = os.getenv("AZURE_OPENAI_API_VERSION")
        
        self.client = AzureOpenAI(
            api_key=self.api_key,
            azure_endpoint=self.azure_endpoint,
            api_version=self.api_version
        )

    def execute(self, messages):
        response = self.client.chat.completions.create(
            model=self.deployment_name,
            messages=messages,
            temperature=0.2,
            top_p=0.2,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
        
        if response.choices[0].message.content is not None:
            return response.choices[0].message.content + "\n"
        else:
            pass