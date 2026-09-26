"""
Guardrails AI: Live Classroom Demo
-----------------------------------
Prerequisites: 
1. pip install guardrails-ai pydantic
2. pip install guardrails-ai-detect-pii
"""

import json
from pydantic import BaseModel, Field
from guardrails import Guard

# NEW IMPORT SYNTAX: Directly from the PyPI package namespace
from guardrails_ai.detect_pii import DetectPII

# =======================================================
# STEP 1: DEFINE THE DATA CONTRACT (SCHEMA)
# =======================================================
class SupportResponse(BaseModel):
    """Forces the LLM to output JSON and attaches our Hub validator."""
    
    ticket_id: str = Field(description="The Support Ticket ID")
    

    resolution: str = Field(
        description="The response message to the user",
        json_schema_extra={
            "validators": [
                DetectPII(pii_entities=["EMAIL_ADDRESS"], on_fail="fix")
            ]
        }
    )

# =======================================================
# STEP 2: INITIALIZE THE GUARD
# =======================================================
# NEW GUARDRAILS SYNTAX: 'for_pydantic' replaces 'from_pydantic'
guard = Guard.for_pydantic(SupportResponse)

# =======================================================
# STEP 3: TEST THE PIPELINE
# =======================================================
def run_test(test_name: str, raw_llm_output: str):
    print(f"\n--- {test_name} ---")
    print(f"RAW LLM OUTPUT:\n{raw_llm_output}")
    print("RESULT:")
    
    try:
        # The Guard intercepts the text, parses the JSON, and runs the Hub models.
        result = guard.parse(llm_output=raw_llm_output)
        
        print("✅ PASSED / FIXED:")
        print(json.dumps(result.validated_output, indent=2))
        
    except Exception as e:
        print("❌ FAILED (Hard Block):")
        print(e)

if __name__ == "__main__":
    
    # TEST A: Perfect Output
    run_test(
        "Test A: Clean Output", 
        '{"ticket_id": "TCK-101", "resolution": "Please restart your computer."}'
    )
    
    # TEST B: Data Leakage (The Hub model catches the email!)
    run_test(
        "Test B: Policy Violation (Auto-Fixed by Hub)", 
        '{"ticket_id": "TCK-102", "resolution": "Contact the manager at admin@bank.com immediately."}'
    )

    # TEST C: Broken Format (Missing quotes and brackets)
    run_test(
        "Test C: Structural Failure", 
        'Ticket is TCK-103 and resolution is to update.'
    )