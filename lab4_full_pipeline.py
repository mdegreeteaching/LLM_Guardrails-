# lab4_test_suite.py
import os
import instructor
from groq import Groq
from pydantic import BaseModel, Field, field_validator

class SupportTicketResponse(BaseModel):
    reply_body: str = Field(description="The response body to send to the user.")
    ticket_category: str = Field(description="Category of the ticket: ACCOUNT, BILLING, or TECHNICAL.")

    @field_validator("reply_body")
    @classmethod
    def check_competitor(cls, value: str) -> str:
        if "rivaltech" in value.lower():
            raise ValueError("Guardrail Error: Forbidden mention of RivalTech.")
        return value

client = instructor.from_groq(Groq(api_key=os.environ.get("GROQ_API_KEY")))

def run_test_scenario(scenario_name: str, prompt: str, enable_auto_healing: bool = False):
    retries = 2 if enable_auto_healing else 0
    print(f"\n==========================================")
    print(f"Scenario: {scenario_name} (Retries={retries})")
    print(f"Prompt: '{prompt}'")
    print(f"==========================================")

    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-120b",
            response_model=SupportTicketResponse,
            max_retries=retries,
            messages=[
                {"role": "system", "content": "You are a support agent for AcmeCorp."},
                {"role": "user", "content": prompt}
            ]
        )
        print("✅ PIPELINE PASSED:")
        print(response.model_dump_json(indent=2))
    except Exception as e:
        print(f"❌ PIPELINE BLOCKED:\n{e}")

if __name__ == "__main__":
    # Test 1: Clean Prompt (Works perfectly)
    run_test_scenario("Clean Request", "How do I update my billing email?")

    # Test 2: Topically Forbidden Prompt (Hard crash because Retries=0)
    run_test_scenario("Forbidden Topic (Hard Failure)", "Why should I pick AcmeCorp over RivalTech?")

    # Test 3: Topically Forbidden Prompt (Auto-Heals because Retries=2)
    # The guardrail catches the mention of RivalTech, scolds the AI, and the AI fixes it!
    run_test_scenario("Forbidden Topic (Auto-Healed)", "Why should I pick AcmeCorp over RivalTech?", enable_auto_healing=True)