# Autonomous Multi-Agent Therapy Simulation

An enterprise-grade, multi-agent AI architecture simulating a live, 60-minute clinical therapy session. 

Most AI chat applications simply pass a growing chat history back and forth between two endpoints until the context window explodes. This project solves that by using a deterministic, cyclical state machine (a "Code Sandwich" architecture) with **five distinct AI agents**. 

Instead of just generating dialogue, the agents analyze subtext, formulate clinical strategies, trigger psychological defense mechanisms, and compress their own memory *before* speaking a single word.

## The AI Pipeline

The simulation runs in a continuous time-stepped loop, powered by 5 specialized agents:

1. **Therapist Notebook (Reasoning Agent):** Analyzes the patient's emotional subtext and generates a hidden, structured clinical strategy for the next turn.
2. **Therapist Actor (Execution Agent):** Reads the Notebook's hidden strategy and outputs strict, conversational dialogue (1-3 sentences maximum).
3. **Patient Subconscious (Reasoning Agent):** Calculates how a patient with trauma/anxiety will react to the therapist, outputting a hidden internal monologue and a strict behavioral directive (e.g., "deflect by talking about physical pain").
4. **Patient Actor (Execution Agent):** Reads the Subconscious directive and acts it out, complete with physical tics and emotional deflections.
5. **Memory Archivist (State Manager):** Solves the infinite context-window problem. It extracts core clinical facts and lore from the dialogue, compressing it into a persistent JSON database (`Patient_memory`). The reasoning agents only read this compressed file, keeping token costs near zero.

## Tech Stack & Engineering Features
* **Language:** Python 3.11
* **AI Integration:** Google GenAI SDK (`google.genai`)
* **Data Validation:** Pydantic v2 (Strict JSON Schema adherence)
* **Frontend:** Streamlit (`testUi.py`)
* **LLM Model Routing:** 
  * `gemini-3.7-flash` handles heavy clinical reasoning and strategy (Notebook/Subconscious).
  * `gemini-3.5-flash-lite` handles fast, low-cost dialogue generation (Actors/Archivist).

### Enterprise Resilience (`safe_generate`)
Running 60 consecutive API calls in a loop guarantees network drops. This project implements a custom `safe_generate` API wrapper that automatically catches and resolves:
* `503 Service Unavailable` (Server Overload)
* `429 Too Many Requests` (Rate Limits)
* `RemoteDisconnected` / `Connection aborted` (TCP Drops)

The wrapper uses an exponential backoff algorithm to ensure the simulation runs completely unattended without crashing or losing application state.
