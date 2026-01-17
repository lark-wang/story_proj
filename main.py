import os
import openai
import re

"""
Before submitting the assignment, describe here in a few sentences what you would have built next if you spent 2 more hours on this project:

A natural next step would be to collect user feedback to learn preferences. Bedtime stories have a lot 
of flexibility in terms of themes, story arc, style, etc., so learning what users like to better adapt the prompts and output would 
be helpful in generating a story more suited to the user's thematic or aesthetic taste. 
"""

def call_model(prompt: str, max_tokens=3000, temperature=0.1) -> str:
    openai.api_key = os.getenv("OPENAI_API_KEY") # please use your own openai api key here.
    resp = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[{"role": "user", "content": prompt}],
        stream=False,
        max_tokens=max_tokens,
        temperature=temperature,
    )
    return resp.choices[0].message["content"]  # type: ignore

example_requests = "A story about a girl named Alice and her best friend Bob, who happens to be a cat."


# --------------------------------------------------
# Preliminary story planning step
# --------------------------------------------------
def outline_story(user_request: str) -> str:
    """
    Generate an outline for the story (to help with story structure).
    """
    prompt = f"""
You are a children's storyteller preparing to write a bedtime story for ages 5–10.

Based on this request:
"{user_request}"

Create a short internal outline for the story that fully satisfies this request. 
Include:
- A main character and one clear, age-appropriate goal or desire
- One primary meaningful challenge or obstacle to their goal that creates mild tension 
- One or more minor missteps, small setbacks, or surprises
- Decisions or actions the character takes to address each challenge, building to a gentle climax
- How the character grows or learns through these experiences
- A resolution that feels natural and concise 

Constraints:
- Keep bullets brief (1–2 sentences each)
- Do NOT write the full story
- Keep it age-appropriate 
- Fully satisfy the request
- No violence or frightening themes

Return only the plan as bullet points.
"""
    return call_model(prompt, temperature=0.3)


# --------------------------------------------------
# Generate story using outline
# --------------------------------------------------
def generate_story(user_request: str, plan: str = None) -> str:
    """
    Generate a bedtime story, optionally guided by an outline.
    """
    plan_text = f"Follow this internal outline to guide the story:\n{plan}\n" if plan else ""

    prompt = f"""
You are a warm, imaginative storyteller telling a bedtime story to a child aged 5–10.

Tell a bedtime story inspired by the following request:
"{user_request}"

{plan_text}

Story requirements:
- Fully satisfies the story request 
- One clear main character with a simple, age-appropriate desire or goal
- One primary meaningful challenge and one or more minor obstacles that requires problem-solving by the main character
- Key decisions and actions the main character takes to overcome challenges
- A satisfying resolution where the character grows or changes in a small, positive way
- The final sentences should feel like the story has completed, not like it is sending the reader off to bed.
- Make sure the main character actively drives the story through choices and actions

General guidance:
- Story should be around 400 words
- Write as if telling the story aloud to a child
- Structure clearly with a beginning, middle, and very brief ending
- Keep language simple, natural, and age-appropriate (5–10 years); No violence or frightening themes
- Keep the tone warm, comforting, and safe
- Show rather than tell, using sensory details and/or meaningful dialogue
- Avoid signposting
- Prefer natural tension and small setbacks over overly neat problem-solving

Guidance on story ending:
- Keep the ending brief and natural 
- Avoid telling the reader lessons, morals, or what to feel
- Do not include any bedtime references including to sleep, dreams, wishing good night

Return only the story text.
"""
    return call_model(prompt, temperature=0.6)


# --------------------------------------------------
# LLM Judge 
# --------------------------------------------------
def judge_story(story: str, user_request: str) -> str:
    prompt = f"""
You are a judge evaluating a bedtime story for children aged 5–10.

Here is the user's request:
---
{user_request}
---

Here is the story:
---
{story}
---

Evaluate the story using the following criteria.
For each category, give a score from 1 (poor) to 5 (excellent) AND a brief explanation.

Categories:
1. Age appropriateness
2. Narrative structure (objective, obstacle, conflict, resolution)
3. Engagement and imagination
4. Satisfaction of user request. For this category only, give a 1 if it doesn't satisfy any part of the request. 
5. Clarity, coherence, and natural storytelling

Then provide:
- An Overall Score (1–5)
- A short bullet-point list of specific suggestions for improvement

Format the response clearly so scores are easy to identify.
Do NOT rewrite the story.
"""
    return call_model(prompt, temperature=0.2)


# --------------------------------------------------
# Get overall score from judge feedback
# --------------------------------------------------
def get_overall_score(judge_feedback: str) -> int:
    match = re.search(r"Overall Score:\s*(\d)", judge_feedback)
    if match:
        return int(match.group(1))
    return 0  # default low if not found


# --------------------------------------------------
# Revision based on judge feedback 
# --------------------------------------------------
def revise_story(story: str, judge_feedback: str, user_request: str) -> str:
    prompt = f"""
You are a children's storyteller revising a bedtime story that is based on a user request.

Original story:
---
{story}
---

Evaluation and feedback from a story judge:
---
{judge_feedback}
---

User request:
---
{user_request}
---

Rewrite the entire story to address the judge's feedback, with special attention to:
- Fully satisfying the user's request
- Strengthening the character's goal, obstacle, conflict, and resolution
- Fixing any coherence or consistency issues
- Ensuring events logically follow from one another
- Keeping it appropriate for ages 5–10
- Maintaining a calm, comforting bedtime tone

Return only the revised story.
"""
    return call_model(prompt, temperature=0.6)


# --------------------------------------------------
# Revision based on user feedback
# --------------------------------------------------
def rewrite_with_user_feedback(story: str, user_feedback: str) -> str:
    prompt = f"""
You are a children's storyteller revising a bedtime story based on user feedback. 
You may change anything in the story (including character roles, events, and outcomes) 
to fully satisfy the feedback.

Current story:
---
{story}
---

User feedback:
---
{user_feedback}
---

Rewrite the entire story to incorporate the feedback while:
- Keeping it appropriate for ages 5–10
- Maintaining a calm, comforting bedtime tone
- Keeping the story cohesive and natural

Return only the rewritten story.
"""
    return call_model(prompt, temperature=0.7)


# --------------------------------------------------
# Ensure high quality final output
# --------------------------------------------------
def apply_quality_guardrail(story: str, user_request: str, max_passes: int = 2, show_feedback: bool = False) -> str:
    """
    Runs the judge and revises the story automatically until
    overall score >= 4 or max_passes is reached.
    """
    score = 0  

    for attempt in range(max_passes):
        judge_feedback = judge_story(story, user_request)

        if show_feedback:
            print("\n📝 Judge Feedback (after revision):\n")
            print(judge_feedback)

        score = get_overall_score(judge_feedback)

        if score >= 4:
            break

        print("Story quality below threshold. Revising again...\n")
        story = revise_story(story, judge_feedback, user_request)

    # Final check after all attempts
    if score < 4:
        print(f"Maximum revision attempts reached. Last Overall Score: {score}.")

    return story


# --------------------------------------------------
# Main program flow
# --------------------------------------------------
def main():
    user_input = input("What kind of story do you want to hear? ")

    # Ask user if they want to see judge feedback
    show_feedback_input = input("Do you want to see the judge feedback? (y/n): ").strip().lower()
    SHOW_JUDGE_FEEDBACK = show_feedback_input == "y"

    print("\n Writing your story...\n")
    story = generate_story(user_input)

    # First judge evaluation
    judge_feedback = judge_story(story, user_input)
    if SHOW_JUDGE_FEEDBACK:
        print("\n📝 Judge Feedback:\n")
        print(judge_feedback)

    # Automatically revise using judge feedback and quality guardrail
    story = revise_story(story, judge_feedback, user_input)
    story = apply_quality_guardrail(story, user_input, max_passes=2, show_feedback=SHOW_JUDGE_FEEDBACK)

    print("\n Here is your bedtime story:\n")
    print(story)

    # Optional user feedback step (kept as is)
    user_feedback = input(
        "\nWould you like to change anything? (Press Enter if you're happy): "
    )

    if user_feedback.strip():
        print("\n Updating the story based on your feedback...\n")
        final_story = rewrite_with_user_feedback(story, user_feedback)
        print("\n Here is the updated bedtime story:\n")
        print(final_story)
    else:
        print("\n Good night!")


if __name__ == "__main__":
    main()
