# lab1_validator.py
from pydantic import BaseModel, Field, field_validator

class TopicalGuardrail(BaseModel):
    response_text: str = Field(description="The response content.")

    @field_validator("response_text")
    @classmethod
    def reject_competitors(cls, value: str) -> str:
        forbidden_terms = ["RivalTech", "MegaCorp"]
        
        for term in forbidden_terms:
            if term.lower() in value.lower():
                raise ValueError(f"BLOCKED: Output contains forbidden competitor '{term}'.")
        
        return value

# --- Testing the validator independently ---
if __name__ == "__main__":
    print("Testing clean text...")
    clean_sample = TopicalGuardrail(response_text="AcmeCorp is happy to help you today!")
    print(f"✅ Passed: {clean_sample.response_text}")

    print("\nTesting forbidden text...")
    try:
        dirty_sample = TopicalGuardrail(response_text="You should really check out RivalTech instead.")
    except Exception as e:
        print(f"❌ {e}")