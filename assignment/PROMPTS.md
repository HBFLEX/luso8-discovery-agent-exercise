# Prompt Log

This document tracks the non-trivial AI interactions that significantly shaped the development of the Luso8 Lead Discovery Agent. 

### 1. LangGraph Workflow Boilerplate
* **Model/Tool:** Claude Opus 4.7 via Claude Code CLI
* **Goal:** Quickly scaffold the StateGraph setup and node definitions for a two-step agent (Filter -> Score).
* **Prompt Snippet:** `"Create a LangGraph workflow with two nodes: filter_candidates and score_lead. The state should contain job_id, business_description, target_market, buyer_types, candidates (list), and scored_leads (list). Use MemorySaver for checkpointing."`
* **Action Taken:** Heavily edited. I accepted the structural boilerplate but stripped out the AI-generated logic inside the nodes to manually implement the strict `leads_seed.json` filtering and the specific Pydantic output parser requirements.

### 2. Frontend UI Refinement (shadcn-like without libraries)
* **Model/Tool:** Gemini
* **Goal:** Elevate the Next.js UI to look professional, modern, and trustworthy without introducing heavy external UI libraries like shadcn/ui or Radix.
* **Prompt Snippet:** `"Can you check the current ui state, Improve the UI to look shadcn-like using the same tailwindcss style. It should follow modern and professional designs."`
* **Action Taken:** Accepted mostly as-is. The model did an excellent job replacing loud background colors. I only manually adjusted a few padding values for mobile responsiveness.

### 3. Fixing LLM Scoring Clustering & Hallucinations (Iterative Prompting)
* **Model/Tool:** Gemini
* **Goal:** The initial `SCORING_SYSTEM_PROMPT` was causing the model to output clustered scores (e.g., exactly 82% or 72% repeatedly) and redundant justifications that just repeated the filter criteria.
* **Prompt Snippet (Iteration 1):** `"I am building an agent for lead discovery... it is returning the same scoring results repetitively within 82, 92, and 72. Help me out with a prompt which can make the results stand out."`
* **Action Taken (Iteration 1):** The model suggested a strict 4-tier grading rubric (0.90-1.00, 0.70-0.89, etc.) and explicit instructions to use granular decimals (e.g., 0.88, 0.61). It also added rules to ban filler words like "matches target market". I applied this to `prompts.py`.
