"""
Student-Centered Parent Feedback Web App
---------------------------------------
A single-file Streamlit app that collects quick classroom context and
produces warm, informative, and student-centered messages for parents/guardians.

How to run locally:
1) Install requirements:
   pip install streamlit
2) Save this file as `parent_feedback_app.py`
3) Start the app:
   streamlit run parent_feedback_app.py

No external services required.
"""

from datetime import date
from textwrap import dedent
import streamlit as st

st.set_page_config(page_title="Parent Feedback Builder", page_icon="📝", layout="centered")

# ----------------------------
# Helper utilities
# ----------------------------

def pluralize(word_singular: str, count: int, word_plural: str | None = None) -> str:
    if count == 1:
        return word_singular
    return word_plural if word_plural else f"{word_singular}s"


def safe_strip(text: str | None) -> str:
    return (text or "").strip()


def join_if_any(parts: list[str], sep: str = " ") -> str:
    return sep.join([p for p in parts if p])


def sentence(text: str) -> str:
    text = safe_strip(text)
    if not text:
        return ""
    return text if text.endswith(('.', '!', '?')) else text + "."


def list_as_clause(label: str, content: str) -> str:
    content = safe_strip(content)
    if not content:
        return ""
    return f"{label}: {content}."


def build_feedback(
    student_name: str,
    minutes_late: int,
    lesson_covered: str,
    behavior: str,
    mood: str,
    homework: str,
    outstanding: str,
    strengths: str,
    supports_today: str,
    next_steps: str,
    tone: str,
    teacher: str,
    course: str,
    contact_pref: str,
    meeting_offer: bool,
) -> dict:
    """Return email-style and SMS-style parent messages.
    """
    name = student_name.strip() if student_name else "your student"

    # Tone presets
    openings = {
        "Warm": f"Hi there — just a quick update about {name} from today.",
        "Neutral": f"Hello, sharing a brief update about {name} from today.",
        "Formal": f"Good day. I'm writing to share an update regarding {name}.",
    }
    closings = {
        "Warm": "Thanks for partnering with me!",
        "Neutral": "Thank you for your attention.",
        "Formal": "Thank you for your continued partnership.",
    }

    # Attendance/arrival clause
    arrival_clause = ""
    if minutes_late is not None and minutes_late > 0:
        arrival_clause = sentence(
            f"{name} arrived {minutes_late} {pluralize('minute', minutes_late)} late. I helped them get settled and connected to the task"
        )

    # Lesson summary
    lesson_clause = sentence(
        join_if_any([
            f"In {course.strip()}" if course else "In class",
            f"we worked on {lesson_covered.strip()}" if lesson_covered else "we continued building core skills",
        ])
    )

    # Behavior & mood phrasing (asset-based, specific)
    behavior = safe_strip(behavior)
    mood = safe_strip(mood)
    behavior_clause = sentence(
        join_if_any([
            f"Behavior noted: {behavior}" if behavior else "",
            f"Mood observed: {mood}" if mood else "",
        ], sep=" ")
    )

    # Strengths, supports, next steps
    strengths_clause = list_as_clause("Strengths I noticed", strengths)
    supports_clause = list_as_clause("Supports provided", supports_today)
    nextsteps_clause = list_as_clause("Next steps", next_steps)

    # Work summary
    homework_clause = list_as_clause("Homework assigned today", homework)
    outstanding_clause = list_as_clause("Outstanding/late work", outstanding)

    # Contact / partnership
    contact_line = sentence(
        join_if_any([
            f"If helpful, I'm happy to connect via {contact_pref.lower()}" if contact_pref else "I'm happy to connect if you have questions",
            "to keep momentum going",
        ])
    )
    if meeting_offer:
        contact_line = join_if_any([contact_line, "I can also set a quick check-in with the student and counselor if needed."])
        contact_line = sentence(contact_line)

    # Compose email-style message
    body_lines = [
        openings.get(tone, openings["Neutral"]),
        arrival_clause,
        lesson_clause,
        behavior_clause,
        strengths_clause,
        supports_clause,
        homework_clause,
        outstanding_clause,
        nextsteps_clause,
        contact_line,
        closings.get(tone, closings["Neutral"]),
        f"— {teacher}" if teacher else "",
    ]

    email_message = "\n\n".join([l for l in body_lines if safe_strip(l)])

    # SMS-style concise message (<= 320 chars target)
    sms_bits = [
        f"Update on {name}:",
        f"{minutes_late} min late." if minutes_late and minutes_late > 0 else "On time.",
        f"Lesson: {lesson_covered.strip()}" if lesson_covered else "Lesson continued.",
        f"Behavior: {behavior}" if behavior else "",
        f"Mood: {mood}" if mood else "",
        f"HW: {homework.strip()}" if homework else "",
        f"Due: {outstanding.strip()}" if outstanding else "",
    ]
    sms_message = " ".join([b for b in sms_bits if safe_strip(b)])
    if len(sms_message) > 320:
        sms_message = sms_message[:317] + "..."

    return {
        "email": email_message,
        "sms": sms_message,
    }


# ----------------------------
# UI
# ----------------------------

st.title("📝 Parent/Guardian Feedback Builder")
st.caption("Create warm, student-centered updates in seconds.")

with st.form("feedback-form", clear_on_submit=False):
    col1, col2 = st.columns(2)
    with col1:
        student_name = st.text_input("Student name*", placeholder="e.g., Jordan P.")
        minutes_late = st.number_input("Minutes late (0 if on time)", min_value=0, max_value=120, value=0, step=1)
        course = st.text_input("Course/Period", placeholder="e.g., Algebra II, Period 3")
        mood = st.selectbox("Observed mood (optional)", ["", "Positive", "Focused", "Calm", "Tired", "Frustrated", "Anxious", "Excited", "Quiet", "Talkative"])        
    with col2:
        teacher = st.text_input("Your name", placeholder="e.g., Ms. Rivera")
        tone = st.select_slider("Tone", options=["Warm", "Neutral", "Formal"], value="Warm")
        contact_pref = st.selectbox("Preferred contact method", ["", "Email", "Phone", "Text", "In-person meeting"])        
        meeting_offer = st.checkbox("Offer to arrange a brief check-in meeting")

    lesson_covered = st.text_area("What did today's lesson cover?*", placeholder="e.g., Solving quadratic equations by factoring")

    behavior = st.text_area(
        "Student behavior (specific, objective notes)",
        placeholder="e.g., Asked for help appropriately; on-task during group work; needed a reminder to start the warm-up"
    )

    strengths = st.text_area(
        "Strengths you noticed (asset-based)",
        placeholder="e.g., Persists through challenging problems; helps peers; strong oral explanations"
    )

    supports_today = st.text_area(
        "Supports provided today",
        placeholder="e.g., Small-group check-in; sentence starters; extra time; visual example"
    )

    homework = st.text_area("Homework assigned today", placeholder="e.g., Textbook p. 128 #4–12 (even)")
    outstanding = st.text_area("Outstanding/late work to submit", placeholder="e.g., Unit 3 quiz retake; Lab report final draft")

    next_steps = st.text_area(
        "Next steps (student-facing, actionable)",
        placeholder="e.g., Finish exit ticket corrections; attend tutoring on Tuesday; check Google Classroom for answer key"
    )

    submitted = st.form_submit_button("Generate Feedback")

if submitted:
    if not safe_strip(student_name) or not safe_strip(lesson_covered):
        st.error("Please fill in at least the student's name and what the lesson covered.")
    else:
        messages = build_feedback(
            student_name=student_name,
            minutes_late=int(minutes_late),
            lesson_covered=lesson_covered,
            behavior=behavior,
            mood=mood,
            homework=homework,
            outstanding=outstanding,
            strengths=strengths,
            supports_today=supports_today,
            next_steps=next_steps,
            tone=tone,
            teacher=teacher,
            course=course,
            contact_pref=contact_pref,
            meeting_offer=meeting_offer,
        )

        st.success("Feedback generated!")

        st.subheader("📧 Email-ready message")
        st.text_area("", value=messages["email"], height=260)
        st.download_button("Download email text", data=messages["email"], file_name=f"{student_name.replace(' ', '_')}_email_feedback.txt")

        st.subheader("💬 SMS-sized summary")
        st.text_area("", value=messages["sms"], height=120)
        st.download_button("Download SMS text", data=messages["sms"], file_name=f"{student_name.replace(' ', '_')}_sms_feedback.txt")

        # Light guidance
        with st.expander("Style guide: Student-centered tips"):
            st.markdown(
                dedent(
                    """
                    - Lead with strengths and concrete observations.
                    - Be specific about supports you provided today.
                    - Keep next steps short, student-facing, and achievable.
                    - Use objective language (what you saw/heard) rather than labels.
                    - Invite partnership and offer a clear way to follow up.
                    """
                )
            )
else:
    st.info("Fill in the form above and click **Generate Feedback** to create parent/guardian messages.")
