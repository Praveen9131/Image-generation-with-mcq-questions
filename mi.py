import os
from flask import Flask, request, jsonify
import openai
from dotenv import load_dotenv

load_dotenv()

openai_api_key = os.getenv("OPENAI_API_KEY")
openai.api_key = openai_api_key

app = Flask(__name__)

# Function to generate an image using DALL-E 3
def generate_image(prompt: str):
    response = openai.Image.create(
        model="dall-e-3",
        prompt=prompt,
        n=1,
        size="1024x1024"
    )
    return response['data'][0]['url']

# Function to generate a question from an image URL using GPT-4 Vision
def generate_mcq_from_image(image_url: str):
    prompt = {
        "role": "user",
        "content": [
            {"type": "text", "text": "You are expert in ,Describe the image and generate a multiple-choice question on important segments based on the description with 4 options and provide the correct answer."},
            {"type": "image_url", "image_url": {"url": image_url, "detail": "high"}}
        ],
    }
    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[prompt],
        max_tokens=1000,
        n=1,
        stop="",  # Set stop to an empty string or a specific stop sequence
        temperature=0.5
    )
    return response.choices[0].message['content']

@app.route('/generate_content', methods=['GET'])
def generate_content():
    topic = request.args.get('topic')
    num_questions = int(request.args.get('num_questions'))

    images_and_questions = []
    for _ in range(num_questions):
        # Generate image
        image_prompt = f"An illustration representing the topic: {topic}"
        image_url = generate_image(image_prompt)
        
        # Generate MCQ based on the image
        mcq_text = generate_mcq_from_image(image_url)
        
        images_and_questions.append({
            'image_url': image_url,
            'mcq': mcq_text
        })

    return jsonify(images_and_questions)

