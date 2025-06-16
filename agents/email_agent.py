from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib
import os
import logging
from collections import Counter

# Topic-specific recommendations
TOPIC_RECOMMENDATIONS = {
    "HACCP": "Review the principles of HACCP, especially hazard analysis and critical control points.",
    "Personal Hygiene": "Brush up on proper handwashing techniques and personal cleanliness guidelines.",
    "Sanitation": "Revisit the steps involved in cleaning and sanitizing surfaces and equipment.",
    "Food Handling": "Make sure you're confident with safe temperature zones and cross-contamination prevention.",
    "Pathogens": "Learn about common foodborne pathogens and how they spread.",
    "Bodily Fluid Cleanup": "Understand safe and compliant methods for cleaning bodily fluid incidents.",
    "General": "Review the key concepts of safe food practices and procedures."
}

# Logging setup
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Generate feedback
def generate_recommendation(score, total_questions, wrong_questions):
    percentage = (score / total_questions) * 100

    # General score-based recommendation
    if percentage < 40:
        general = "You may want to revisit all foundational food safety topics to improve your understanding."
    elif percentage < 70:
        general = "Good effort! Focus on the topics listed below to strengthen your knowledge."
    else:
        general = "Great work! You did well — here are a few areas to review for mastery."

    # Count mistakes by topic
    topic_counter = Counter(q.get("topic", "General") for q in wrong_questions)

    # Topic-wise summary
    topic_summary = [f"- {topic}: {count} question(s) wrong" for topic, count in topic_counter.items()]

    # Unique topic-specific tips
    tips = []
    seen_topics = set()
    for topic in topic_counter:
        if topic not in seen_topics:
            seen_topics.add(topic)
            tip = TOPIC_RECOMMENDATIONS.get(topic, "Review this topic for better understanding.")
            tips.append(f"- {tip}")

    # Question review
    question_review = []
    for i, q in enumerate(wrong_questions, 1):
        question_review.append(
            f"{i}. Q: {q['question']}\n   Your Answer: {q['user_answer']}\n   Correct Answer: {q['correct_answer']}"
        )

    return general, topic_summary, tips, question_review

# Email construction
def create_email(sender, recipients, subject, body, html_body=None):
    message = MIMEMultipart()
    message["From"] = sender
    message["To"] = ", ".join(recipients)
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))
    if html_body:
        message.attach(MIMEText(html_body, "html"))

    return message

# Email sending
def send_email(smtp_server, port, sender, password, recipients, message):
    try:
        with smtplib.SMTP_SSL(smtp_server, port) as server:
            server.login(sender, password)
            server.sendmail(sender, recipients, message.as_string())
            logging.info("Email sent successfully.")
    except Exception as e:
        logging.error(f"Error sending email: {e}")

# Test block (dynamic)
if __name__ == "__main__":
    smtp_server = "smtp.gmail.com"
    port = 465
    sender_email = "safechef8@gmail.com"
    password = "xefc edqs sqiw rllf"
    recipients = ["swaragreddy07@gmail.com"]
    subject = "Your SafeChef Quiz Feedback"

    # Simulate a user's quiz result
    wrong_questions = [
        {
            "topic": "HACCP",
            "question": "What is the first principle of HACCP?",
            "user_answer": "Determine CCPs",
            "correct_answer": "Conduct a hazard analysis"
        },
        {
            "topic": "Personal Hygiene",
            "question": "When should food handlers wash their hands?",
            "user_answer": "Once per hour",
            "correct_answer": "After any activity that could contaminate hands"
        },
        {
            "topic": "Food Handling",
            "question": "What is the minimum hot-hold temperature?",
            "user_answer": "100°F",
            "correct_answer": "135°F"
        },
        {
            "topic": "HACCP",
            "question": "What is the final step in HACCP?",
            "user_answer": "Determine CCPs",
            "correct_answer": "Establish record-keeping procedures"
        }
    ]

    score = 6
    total_questions = 10

    general, topic_summary, tips, question_review = generate_recommendation(score, total_questions, wrong_questions)

    # Plain text email
    body = f"""Hello,

Thank you for completing the SafeChef food safety quiz.

Your score: {score}/{total_questions} ({(score / total_questions) * 100:.2f}%)

General Recommendation:
{general}

Topic Summary:
{chr(10).join(topic_summary)}

Topic-Specific Tips:
{chr(10).join(tips)}

Review Your Incorrect Answers:
{chr(10).join(question_review)}

Stay safe and keep learning!

– The SafeChef Team
"""

    # HTML email
    html_body = f"""
    <html>
    <body>
        <h2>SafeChef Quiz Results</h2>
        <p><strong>Your score:</strong> {score}/{total_questions} ({(score / total_questions) * 100:.2f}%)</p>
        <h3>General Recommendation:</h3>
        <p>{general}</p>
        <h3>Topic Summary:</h3>
        <ul>
            {''.join(f"<li>{line}</li>" for line in topic_summary)}
        </ul>
        <h3>Topic-Specific Tips:</h3>
        <ul>
            {''.join(f"<li>{tip[2:]}</li>" for tip in tips)}
        </ul>
        <h3>Review Your Incorrect Answers:</h3>
        <ol>
            {''.join(f"<li><strong>Q:</strong> {q['question']}<br><strong>Your Answer:</strong> {q['user_answer']}<br><strong>Correct Answer:</strong> {q['correct_answer']}</li>" for q in wrong_questions)}
        </ol>
        <p>Stay safe and keep learning!<br>– The SafeChef Team</p>
    </body>
    </html>
    """

    # Send
    email_msg = create_email(sender_email, recipients, subject, body, html_body)
    send_email(smtp_server, port, sender_email, password, recipients, email_msg)
