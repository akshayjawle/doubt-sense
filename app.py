from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS

import os
from dotenv import load_dotenv
from openai import OpenAI

from database import get_connection, create_table


# -----------------------------
# Load environment variables
# -----------------------------

load_dotenv()

NVIDIA_API_KEY = os.getenv("NVIDIA_API_KEY")

if not NVIDIA_API_KEY:
    print("WARNING: NVIDIA_API_KEY was not found in .env")


# -----------------------------
# NVIDIA AI Client
# -----------------------------

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=NVIDIA_API_KEY
)


# -----------------------------
# Flask App
# -----------------------------

app = Flask(__name__)
CORS(app)

create_table()


# -----------------------------
# Home Route
# -----------------------------

@app.route("/")
def home():
    return send_from_directory(".", "index.html")


@app.route("/teacher")
def teacher():
    return send_from_directory(".", "teacher.html")


# -----------------------------
# Get Questions
# -----------------------------

@app.route("/api/questions", methods=["GET"])
def get_questions():

    connection = get_connection()

    questions = connection.execute(
        """
        SELECT *
        FROM questions
        ORDER BY id DESC
        """
    ).fetchall()

    connection.close()

    return jsonify([
        dict(question)
        for question in questions
    ])


# -----------------------------
# Add Question
# -----------------------------

@app.route("/questions", methods=["POST"])
def add_question():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400

    subject = data.get("subject")
    question = data.get("question")

    if not subject or not question:
        return jsonify({
            "error": "Subject and question are required"
        }), 400

    connection = get_connection()

    # Count existing questions from the same subject
    cursor = connection.execute(
        """
        SELECT COUNT(*)
        FROM questions
        WHERE subject = ?
        """,
        (subject,)
    )

    similar_count = cursor.fetchone()[0]

    # Calculate priority
    if similar_count >= 5:
        priority = "high"

    elif similar_count >= 2:
        priority = "medium"

    else:
        priority = "low"

    # Save question
    cursor = connection.execute(
        """
        INSERT INTO questions
        (
            subject,
            question,
            votes,
            priority
        )
        VALUES (?, ?, 0, ?)
        """,
        (
            subject,
            question,
            priority
        )
    )

    connection.commit()

    question_id = cursor.lastrowid

    connection.close()

    return jsonify({
        "message": "Question submitted successfully",
        "question_id": question_id,
        "priority": priority
    }), 201


# -----------------------------
# Teacher Answer
# -----------------------------

@app.route("/questions/<int:question_id>/answer", methods=["POST"])
def answer_question(question_id):

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400

    answer = data.get("answer")

    if not answer:
        return jsonify({
            "error": "Answer is required"
        }), 400

    connection = get_connection()

    question = connection.execute(
        """
        SELECT id
        FROM questions
        WHERE id = ?
        """,
        (question_id,)
    ).fetchone()

    if not question:
        connection.close()

        return jsonify({
            "error": "Question not found"
        }), 404

    connection.execute(
        """
        UPDATE questions
        SET answer = ?,
            status = 'answered'
        WHERE id = ?
        """,
        (answer, question_id)
    )

    connection.commit()
    connection.close()

    return jsonify({
        "message": "Answer submitted successfully",
        "question_id": question_id
    }), 200
# -----------------------------
# AI Doubt Solver
# -----------------------------

@app.route("/ask", methods=["POST"])
def ask_ai():

    data = request.get_json()

    if not data:
        return jsonify({
            "error": "JSON data is required"
        }), 400

    question = data.get("question")

    if not question:
        return jsonify({
            "error": "Question is required"
        }), 400

    if not NVIDIA_API_KEY:
        return jsonify({
            "error": "NVIDIA_API_KEY is missing. Check your .env file."
        }), 500

    try:

        response = client.chat.completions.create(

            model="nvidia/nemotron-3-super-120b-a12b",

            messages=[
                {
                    "role": "system",
                    "content": """
You are DoubtSense AI, an educational assistant.

Your job is to help students understand their doubts.

Give explanations that are:

* Simple
* Clear
* Accurate
* Beginner-friendly

When appropriate, include:

1. Simple explanation
2. Example
3. Key points to remember

Do not unnecessarily make the answer complicated.
"""
                },
                {
                    "role": "user",
                    "content": question
                }
            ],

            temperature=0.6,
            max_tokens=500
        )

        answer = response.choices[0].message.content

        return jsonify({
            "question": question,
            "answer": answer
        }), 200

    except Exception as e:

        print("NVIDIA API ERROR:", e)

        return jsonify({
            "error": str(e)
        }), 500


# -----------------------------
# Start Flask Server
# -----------------------------

if __name__ == "__main__":
    app.run(debug=True)
            
       

   
