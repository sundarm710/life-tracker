import streamlit as st
from openai import OpenAI
import openai
from PIL import Image
import os
from dotenv import load_dotenv
import random

# Load environment variables from .env file
load_dotenv()

# Initialize the OpenAI client with the API key from the environment variable
client = OpenAI(
    api_key=os.environ.get("OPENAI_API_KEY"),
)

# Function to read and process topics from the OBSIDIAN_KVIZZING_PATH file
def load_topics_from_file(file_path):
    print("Processing topics from file:", file_path)
    topics = []
    try:
        with open(file_path, 'r') as file:
            in_properties_section = False
            for line in file:
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
                        
    except FileNotFoundError:
        print(f"Error: The file {file_path} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

    st.session_state.topics = topics

    return topics

# Load topics from the OBSIDIAN_KVIZZING_PATH file
kvizzing_path = os.path.join(os.environ.get("OBSIDIAN_BASE_PATH"), os.environ.get("OBSIDIAN_KVIZZING_PATH"))
st.session_state.topics = load_topics_from_file(kvizzing_path)


system_prompt = """
        You are a helpful assistant that can answer questions and provide information.
"""
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
    else:
        st.session_state.messages.append({"role": "assistant", "content": system_prompt})

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
        Use bullet points if necessary. 
        Include tables while making comparisons.
        Divide into sections.
        Do not list information like in Wikipedia.
    """

    print(prompt)
    
    chat_response = get_chat_response(prompt)
    print(chat_response)

    return chat_response

# Function to display the carousel of topics
def display_carousel():
    st.title("Kvizzing Topics Carousel")
    if 'topics' not in st.session_state:
        st.session_state.topics = load_topics_from_file(kvizzing_path)
    
    topics = st.session_state.topics
    selected_topic = topics[random.randint(0, len(topics) - 1)]

    if st.button("Generate Trivia"):
        st.session_state.messages = []
        print(f"Selected topic: {selected_topic}")
        trivia = fetch_trivia(selected_topic)
        
        st.session_state.last_trivia = trivia  # Store the trivia in session state

# Function to display the chat interface
def display_chat_interface():
    st.subheader("Chat with the Trivia Bot")
    if 'messages' not in st.session_state:
        st.session_state.messages = []

    # Display chat messages
    for msg in st.session_state.messages:
        if msg['role'] == 'user':
            st.markdown(f"**You:** \n {msg['content']}")
        else:
            st.markdown(f"**Bot:** \n {msg['content']}")

    # User input for chat
    user_input = st.text_input("Type your message here:", key="chat_input", placeholder="")
    
    if st.button("Send"):
        if user_input:
            fetch_trivia(user_input)

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
