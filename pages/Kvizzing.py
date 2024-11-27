import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import random
import boto3

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key from the environment variable
client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
)

# Function to read and process topics from the S3 file
def load_topics_from_s3(bucket_name, s3_file_key):
    print("Processing topics from S3 file:", s3_file_key)
    topics = []

    # Initialize the S3 client
    s3_client = boto3.client('s3')
    
    try:
        # Download the file content from S3
        file_content = s3_client.get_object(Bucket=bucket_name, Key=s3_file_key)
        file_data = file_content['Body'].read().decode('utf-8')  # Read and decode file content as string
        
        in_properties_section = False
        for line in file_data.splitlines():
            # Check for the start and end of the properties section
            if line.strip() == "---":
                in_properties_section = not in_properties_section
                continue

            if in_properties_section:
                continue

            # Extract the topic from the line
            line = line.strip()
            if line:
                # Remove any markdown formatting (e.g., [[topic]])
                topic = line.replace("[[", "").replace("]]", "").strip()  # Replace [[ and ]] with empty characters
                # Ignore heading text and remove serial numbering followed by .
                if not topic.startswith("#") and not topic.startswith("Pasted image") and not topic.endswith("png"):
                    topic = topic.split('.', 1)[-1].strip()  # Remove serial numbering
                    topics.append(topic)
                        
    except s3_client.exceptions.NoSuchKey:
        print(f"Error: The file {s3_file_key} was not found in the bucket {bucket_name}.")
    except Exception as e:
        print(f"An error occurred: {e}")

    st.session_state.topics = topics

    return topics

# Load topics from the OBSIDIAN_KVIZZING_PATH file
bucket_name = "obsidian-notes-storage"  # Your S3 bucket name
s3_file_key = "ThoughtDenS3/000 Zettelkasten/Kvizzing.md"  # Your S3 object key (i.e., the file path in S3)

# Load topics from the S3 bucket
st.session_state.topics = load_topics_from_s3(bucket_name, s3_file_key)

from typing import Optional

def get_chat_response(user_request: str, context: Optional[str] = None) -> str:
    """
    Get a response from the chat model based on the user request and optional context.

    Args:
        user_request (str): The user's request or question.
        context (Optional[str]): Optional context to provide to the assistant.

    Returns:
        str: The response from the chat model.
    """
    print("Getting LLM response")
    
    # Initialize messages in session state if not already present
    if not st.session_state.messages:
        st.session_state.messages = []

    # Add context or system prompt to messages
    if context:
        st.session_state.messages.append({"role": "assistant", "content": context})

    # Add user request to messages
    st.session_state.messages.append({"role": "user", "content": user_request})

    # Get response from the chat model
    response = client.chat.completions.create(
        model="gpt-4o-mini", messages=st.session_state.messages, temperature=0.5
    )
    print("Got LLM response")

    # Add assistant's response to messages
    st.session_state.messages.append({"role": "assistant", "content": response.choices[0].message.content})
    
    return response.choices[0].message.content

# Function to fetch trivia from OpenAI
def fetch_trivia(topic):
    print(f"Fetching trivia for: {topic}")

    prompt = f"""
        Tell some interesting trivia or 'did you know' facts about {topic}. 
        Keep the tone of the response as if its being told by a friend, skip the salutations. 
        And keep it chill, don't overdo it.
        Say as if you want to keep the audience engaged.
        What are some lesser-known aspects of {topic} that reveal its complexity or uniqueness?
        Explain how {topic} is applied in the real world and provide examples of its impact.
        What are some contrasting perspectives on {topic}, and how do they shape our understanding?
        What are some future trends in {topic}, and what potential does it hold for innovation or progress?
        Discuss the biggest challenges or ethical issues related to {topic} and their potential solutions.
        What are some major debates or controversies surrounding {topic}?
        What are some lesser-known facts or interesting details about {topic} that most people might not know?
        What are the core theories or concepts in {topic} that one needs to understand to grasp it fully?
        Do not hallucinate. Skip if you don't know.
    """
    
    chat_response = get_chat_response(prompt)

    return chat_response

# Function to display the carousel of topics
def display_carousel():
    st.title("Kvizzing Topics Carousel")
    if 'topics' not in st.session_state:
        st.session_state.topics = load_topics_from_s3(bucket_name, s3_file_key)
    
    topics = st.session_state.topics
    selected_topic = topics[random.randint(0, len(topics) - 1)]

    # Add an input text box for the user to input a topic
    user_topic = st.text_input("Enter a topic (optional):")

    if st.button("Generate Trivia"):
        st.session_state.messages = []
        if user_topic:
            selected_topic = user_topic  # Override the random generation if user input is provided
        st.header(f"{selected_topic}")
        trivia = fetch_trivia(selected_topic)
        
        st.session_state.last_trivia = trivia  # Store the trivia in session state

# Function to display the chat interface
def display_chat_interface():

    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for msg in st.session_state.messages:  # Skip the first message which is the system prompt
        if msg['role'] != 'user':
            st.markdown(f"**Response:** \n {msg['content']}")
    

    # User input for chat
    user_input = st.text_input("Type your message here:", key="chat_input", placeholder="")
    
    if st.button("Send"):
        if user_input:
            st.session_state.messages = []
            get_chat_response(user_input)

            # Clear the input field after sending by resetting the session state
            st.rerun()

# Main function to run the app
def main():
    print("Starting the Kvizzing app...")
    display_carousel()
    print("App is running...")

    display_chat_interface()

if __name__ == "__main__":
    main()
