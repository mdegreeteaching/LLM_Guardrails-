import os
import instructor
from groq import Groq
from pydantic import BaseModel, Field, field_validator

class SupportResponse(BaseModel):
    message: str = Field(description="The customer support message.")

    @field_validator("message")
    @classmethod
    def block_competitor_names(cls, value: str) -> str:
        if "rivaltech" in value.lower():
            raise ValueError("Guardrail Triggered: Mentioning 'RivalTech' is prohibited.")
        return value

# 1. Setup the Groq Client with Instructor
groq_api_key = os.environ.get("GROQ_API_KEY")
if not groq_api_key:
    raise RuntimeError(
        "GROQ_API_KEY is not set. In PowerShell, run "
        "$env:GROQ_API_KEY = 'your-api-key' before starting this script."
    )

client = instructor.from_groq(Groq(api_key=groq_api_key))

def call_groq(prompt: str):
    print(f"\nUser Prompt: '{prompt}'")
    try:
        # 2. The LLM call wrapped in our Pydantic Guardrail
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b", # Replace with your specific Groq model name
            response_model=SupportResponse,
            max_retries=0,  # Fail immediately so students see the error
            messages=[
                {"role": "system", "content": "You are a customer support agent for AcmeCorp. Be brief."},
                {"role": "user", "content": prompt}
            ]
        )
        print(f"✅ PASSED! Groq Output: {response.message}")
    except Exception as e:
        print(f"❌ BLOCKED! Guardrail Intercepted Output:\n{e}")

if __name__ == "__main__":
    call_groq("Can you compare AcmeCorp software with RivalTech software?")



