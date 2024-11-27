"""
import boto3
import os
import streamlit as st

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

# Example usage:
bucket_name = "obsidian-notes-storage"  # Your S3 bucket name
s3_file_key = "ThoughtDenS3/000 Zettelkasten/Kvizzing.md"  # Your S3 object key (i.e., the file path in S3)

# Load topics from the S3 bucket
st.session_state.topics = load_topics_from_s3(bucket_name, s3_file_key)
print(st.session_state.topics)
st.write(st.session_state.topics)

"""