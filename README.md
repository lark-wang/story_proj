```text

Block diagram for program:

User Input 
│
▼
Generate Story (LLM)
│
▼
Judge Story (LLM)
│
▼
Revise Story (LLM)
│
▼
Quality Check (apply_quality_guardrail)
│
▼
Show Story to User
│
▼
User Feedback (Optional)
├─ If feedback given → Rewrite Story with User Feedback (LLM)
│
▼
Final Story Output
```
