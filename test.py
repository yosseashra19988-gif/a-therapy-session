import os
from dotenv import load_dotenv
from google import genai
from google.genai import types
from pydantic import BaseModel, Field
from time import sleep
from models import PatientMemory,PatientSubconscious, TherapistNotebook
def safe_generate(client, contents, config=None, max_retries=5):
    """Wraps the Gemini API call with an automatic retry loop for 503/429 errors."""
    for attempt in range(max_retries):
        try:
            # Try to hit the API
            response = client.models.generate_content(
                model="gemini-3.5-flash",
                contents=contents,
                config=config
            )
            return response
            
        except Exception as e:
            error_msg = str(e)
            # If it's a server overload (503) or rate limit (429), pause and retry
            if "503" in error_msg or "429" in error_msg:
                wait_time = (attempt + 1) * 5  # Backoff: waits 5s, then 10s, then 15s...
                print(f"[API OVERLOAD] Retrying in {wait_time} seconds... (Attempt {attempt+1}/{max_retries})")
                sleep(wait_time)
            else:
                # If it's a real bug (like a Pydantic schema error), crash so you can see it
                raise e 
                
    raise Exception("API failed after maximum retries. Please try again later.")

def aTherapySessions():
    load_dotenv()
    api_key = os.environ.get('GEMINI_API_KEY')
    client = genai.Client(api_key=api_key)
    chatContext = []
    day = 0
    session = 0
    last_message = ""
    chat_history = []
    time = 0
    Patient_memory =[]
    subconciousResponse = {}
    thyrapist_notebook ={}
    while time <= 60:
    
    
        #THE PROMPTS
        sessionrules = f""" session length = 1 hour
                            every messeage = 5 mins
                            u should try to finish the session on time 
        """
        patientPrompt = f"""Day {day}. Session {session}.
        You are a patient with GAD (Generalized Anxiety Disorder) in a therapy session.
        
        YOUR ESTABLISHED MEMORY & LORE (Do not contradict these facts):
        {Patient_memory}
        
        YOUR TRUE INTERNAL FEELINGS RIGHT NOW (Do not say this out loud):
        "{subconciousResponse.get('internal_monologue','')}"
        
        YOUR DIRECTIVE FOR THIS TURN:
        "{subconciousResponse.get('behavioral_directive','')}"
        
        The therapist just said: "{last_message}"
        
        INSTRUCTIONS:
        1. Write ONLY your spoken dialogue and brief physical actions (e.g., *looks away*).
        2. Act out your DIRECTIVE perfectly. Be messy, Sometimes emotional (only when needed), and realistically human.
        3. your directive tells you your internal feelings and your self monolouge (what we speak to ourselfs inside not always show it). 
        """
        therapistPrompt = f"""
        Day {day}. Session {session}.
        You are Dr. Aris, a seasoned clinical psychologist conducting a live therapy session.
        
        YOUR PRIVATE CLINICAL STRATEGY FOR THIS TURN:
        "{thyrapist_notebook}"
        
        The patient just said: "{last_message}"
        
        INSTRUCTIONS:
        1. Write ONLY your spoken dialogue. DO NOT write big paragraphs.
        2. Keep responses conversational, short (1 to 3 sentences maximum), and natural.
        3. Dont Get stuck in the same point u need to start questioning and evolve the conversation
        4. Execute your clinical strategy perfectly based on what the patient just said.
                """
        chatPrompt=f"""
                past chat{chatContext}
                """
                
        thyrapist_notebook=thyrapistNotebook(client,Patient_memory,last_message)
                #therapist messeage
        therapistresponse = safe_generate(
                    client=client,
                    contents=[therapistPrompt,sessionrules,chatPrompt],
                        
                    )
        last_message = therapistresponse.text
        chat_history.append(last_message)
        time += 5
        
        yield f"**[Therapist] ({time} min):** {last_message}"
        sleep(40)
        
        subconciousResponse=patientSubconcious(client, Patient_memory, last_message)
        # patient message
        patientresponse = safe_generate(
                        client=client,
                        contents=[patientPrompt,sessionrules,chatPrompt],
                        )
        last_message = patientresponse.text
        yield f"**[Patient] ({time} min):** {last_message}"
        chat_history.append(last_message)
        time += 5
        sleep(40)
        Patient_memory=patientMemory(client, last_message, Patient_memory)
        
    session+=1
    day+=1
    
    
    
    # AI 2 - THE MEMORY OF PATIENT
def patientMemory(client, latest_message, current_memory):
    patient_memory = f"""
You are the Memory Archivist for a clinical therapy simulation. 
    Your strict responsibility is to update the patient's permanent psychological file based ONLY on what they just said.
    
    CURRENT FILE: 
    {current_memory}
    
    Thyrapist JUST SAID: 
    "{latest_message}"
    
    RULES FOR UPDATING:
    1. CORE FACTS: If the patient mentions their name, age, hometown, family members, or background, add or update it in `core_facts` with a clear key.
    2. STORIES & LORE: If the patient tells a new story, recalls a memory, or adds details to a previous trauma, create a descriptive key in `established_stories` and summarize the facts.
    3. MERGE, DON'T OVERWRITE: Carry over all existing data from the Current File. Only update a key if the patient added new details or corrected a past lie.
    4. NO EMOTION, ONLY FACTS: Do not record how the patient feels. Only record concrete lore, actions, and biographical data.
    """

    
    response = safe_generate(
        client=client,
        contents=patient_memory,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PatientMemory,
            temperature=0.0 
        ),
    )
    
    # Returns the dynamically generated dictionary (e.g., {"Robbery_Incident": "...", "Family": "..."})
    return response.parsed.model_dump()



    # AI 3 - THE Subconcious OF PATIENT
def patientSubconcious(client, living_memory, last_therapist_message):
    subconscious_prompt = f"""
You are the subconscious mind and clinical behavioral predictor for a patient with Generalized Anxiety Disorder and acute trauma.

ESTABLISHED LORE & MEMORY: {living_memory}

The PATIENT just said: "{last_therapist_message}"

TASK:
Calculate exactly how this specific patient will react to the therapist's statement. 
Do they feel attacked? Validated? Cornered? or normal (not every question need to evoke emotions, emotions are not EASY TO GET EVOKED)
Output their true internal monologue and a strict behavioral prediction for how they will act next. 
"""

    
    response = safe_generate(
        client=client,
        contents=subconscious_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=PatientSubconscious,
            temperature=0.0 
        ),
    )
    subconciousResponse = response.parsed.model_dump()
    # Returns the dynamically generated dictionary (e.g., {"Robbery_Incident": "...", "Family": "..."})
    return subconciousResponse

def thyrapistNotebook(client, living_memory, last_patient_message):
    notebook_prompt = f"""
    You are Dr. Aris, a seasoned clinical psychologist. You are writing your private, mid-session clinical notes.

    PATIENT'S FILE: {living_memory}
    THE PATIENT JUST SAID: "{last_patient_message}"

    TASK:
    Analyze the patient's statement. 
    1. Note their underlying emotions.
    2. Note your clinical understanding of what they are struggling with right now.
    3. Formulate a strict strategy for what you will say or ask next, and explain why.
    """
    
    response = safe_generate(
        client=client,
        contents=notebook_prompt,
        config=types.GenerateContentConfig(
            response_mime_type="application/json",
            response_schema=TherapistNotebook, # Uses the new schema
            temperature=0.0 # Keep it 0.0 for strict, logical clinical reasoning
        )
    )
    return response.parsed.model_dump()
 
aTherapySessions()