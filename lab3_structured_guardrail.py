# lab3_structured_guardrail.py
import os
import instructor
from groq import Groq
from pydantic import BaseModel, Field, field_validator

# Define a strict JSON schema with multiple data types
class CustomerSupportPayload(BaseModel):
    customer_message: str = Field(description="Response message to the user.")
    sentiment: str = Field(description="Customer sentiment: 'POSITIVE', 'NEUTRAL', or 'NEGATIVE'.")
    escalate_to_human: bool = Field(description="True if customer requires human support.")

    # 1. Topical Validator
    @field_validator("customer_message")
    @classmethod
    def block_competitor_names(cls, value: str) -> str:
        if "rivaltech" in value.lower():
            raise ValueError("Topical Guardrail Failure: Competitor name detected.")
        return value

    # 2. Structural Validator
    @field_validator("sentiment")
    @classmethod
    def validate_sentiment_enum(cls, value: str) -> str:
        allowed = ["POSITIVE", "NEUTRAL", "NEGATIVE"]
        if value.upper() not in allowed:
            raise ValueError(f"Structure Guardrail Failure: Sentiment must be one of {allowed}.")
        return value.upper()

client = instructor.from_groq(Groq(api_key=os.environ.get("GROQ_API_KEY")))

# Run a clean call to show the multi-field JSON output
print("\n--- Sending request to Groq ---")
response = client.chat.completions.create(
    model="openai/gpt-oss-120b",
    response_model=CustomerSupportPayload,
    messages=[
        {"role": "system", "content": "You are a helpful support agent for AcmeCorp."},
        {"role": "user", "content": "I am furious that my login isn't working! Fix it now!"}
    ]
)

print("✅ Structured JSON Response from Groq:")
print(response.model_dump_json(indent=2))

#question 2: compare the acmecorp software with rivaltech software