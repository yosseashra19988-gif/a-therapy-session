from pydantic import BaseModel, Field
from typing import List, Optional

    
class PatientMemory(BaseModel):
    core_facts: list[str] = Field(
        description="Hard demographic details explicitly stated by the patient (e.g., 'Name', 'Age', 'Birthplace', 'Family_Members', 'Occupation')."
    )
    established_stories: list[str] = Field(
        description="Summaries of specific events, memories, or traumas the patient has described (e.g., 'Gas_Station_Robbery', 'Childhood_Incident')."
    )

class PatientSubconscious(BaseModel):
    
    internal_monologue: str = Field(
        description="The patient's true, uncensored, hidden thoughts in this exact moment. What they are actually feeling, but will not say out loud."
    )
    behavioral_directive: str = Field(
        description="Strict instructions for the Actor AI on how to respond. Must specify the emotional tone (e.g., defensive, avoidant, hostile, superficially cheerful) and the strategy (e.g., lie about a detail, attack the therapist, shut down). DO NOT write spoken dialogue."
    )

class TherapistNotebook(BaseModel):
    patient_emotions: str = Field(
        description="The therapist's observation of the patient's current emotional state."
    )
    clinical_understanding: str = Field(
        description="What the therapist understands about the patient's core struggle right now."
    )
    strategy: str = Field(
        description="The clinical plan for the next response: what specific question should be asked and why."
    )