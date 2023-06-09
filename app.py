import streamlit as st
from PIL import Image
import numpy as np
import nltk
nltk.download('stopwords')
nltk.download('punkt')
import pandas as pd
import random
import easyocr
import re
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from transformers import AutoTokenizer, VisionEncoderDecoderModel, ViTFeatureExtractor

# Directory path to the saved model on Google Drive
model = VisionEncoderDecoderModel.from_pretrained("nlpconnect/vit-gpt2-image-captioning")

# Load the feature extractor and tokenizer
feature_extractor = ViTFeatureExtractor.from_pretrained("nlpconnect/vit-gpt2-image-captioning")
tokenizer = AutoTokenizer.from_pretrained("nlpconnect/vit-gpt2-image-captioning")


def generate_captions(image):
    image = Image.open(image).convert("RGB")
    generated_caption = tokenizer.decode(model.generate(feature_extractor(image, return_tensors="pt").pixel_values.to("cpu"))[0])
    sentence = generated_caption
    text_to_remove = "<|endoftext|>"
    generated_caption = sentence.replace(text_to_remove, "")
    return generated_caption

# use easyocr to extract text from the image
def image_text(image):
    img_np = np.array(image)
    reader = easyocr.Reader(['en'])
    text = reader.readtext(img_np)
    detected_text = " ".join([item[1] for item in text])

    # Extract individual words, convert to lowercase, and add "#" symbol
    detected_text= ['#' + entry[1].strip().lower().replace(" ", "_") for entry in text]
    return detected_text

# Load NLTK stopwords for filtering
stop_words = set(stopwords.words('english'))

# Add hashtags to keywords, which have been generated from image captioing
def add_hashtags(keywords):
    hashtags = []
    
    for keyword in keywords:
        # Generate hashtag from the keyword (you can modify this part as per your requirements)
        hashtag = '#' + keyword.lower()
        
        hashtags.append(hashtag)
    
    return hashtags

def trending_hashtags(caption):
  # Read trending hashtags from a file separated by commas
  with open("hashies.txt", "r") as file:
      hashtags_string = file.read()

  # Split the hashtags by commas and remove any leading/trailing spaces
  trending_hashtags = [hashtag.strip() for hashtag in hashtags_string.split(',')]

  # Create a DataFrame from the hashtags
  df = pd.DataFrame(trending_hashtags, columns=["Hashtags"])

  # Function to extract keywords from a given text
  def extract_keywords(caption):
      tokens = word_tokenize(caption)
      keywords = [token.lower() for token in tokens if token.lower() not in stop_words]
      return keywords

  # Extract keywords from caption and trending hashtags
  caption_keywords = extract_keywords(caption)
  hashtag_keywords = [extract_keywords(hashtag) for hashtag in df["Hashtags"]]

  # Function to calculate cosine similarity between two strings
  def calculate_similarity(text1, text2):
      tfidf_vectorizer = TfidfVectorizer()
      tfidf_matrix = tfidf_vectorizer.fit_transform([text1, text2])
      similarity_matrix = cosine_similarity(tfidf_matrix[0], tfidf_matrix[1])
      return similarity_matrix[0][0]

  # Calculate similarity between caption and each trending hashtag
  similarities = [calculate_similarity(' '.join(caption_keywords), ' '.join(keywords)) for keywords in hashtag_keywords]

  # Sort trending hashtags based on similarity in descending order
  sorted_hashtags = [hashtag for _, hashtag in sorted(zip(similarities, df["Hashtags"]), reverse=True)]

  # Select top k relevant hashtags (e.g., top 5) without duplicates
  selected_hashtags = list(set(sorted_hashtags[:5]))

  selected_hashtag = [word.strip("'") for word in selected_hashtags]

  return selected_hashtag

# create the Streamlit app
def app():
    st.title('Image from your Side, Trending Hashtags from our Side')

    st.write('Upload an image to see what we have in store.')

    # create file uploader
    uploaded_file = st.file_uploader("Got You Covered, Upload your wish!, magic on the Way! ", type=["jpg", "jpeg", "png"])

    # check if file has been uploaded
    if uploaded_file is not None:
        # load the image
        image = Image.open(uploaded_file).convert("RGB")

        # Image Captions
        string = generate_captions(uploaded_file)
        tokens = word_tokenize(string)
        keywords = [token.lower() for token in tokens if token.lower() not in stop_words]
        hashtags = add_hashtags(keywords)

        # Text Captions from image
        extracted_text = image_text(image)

        #Final Hashtags Generation
        web_hashtags = trending_hashtags(string)

        combined_hashtags = hashtags + extracted_text + web_hashtags

        # Shuffle the list randomly
        random.shuffle(combined_hashtags)

        combined_hashtags = list(set(item for item in combined_hashtags[:15] if not re.search(r'\d$', item)))


        # display the image
        st.image(image, caption='The Uploaded File')
        st.write("First is first captions for your Photo : ", string)
        st.write("Magical hashies have arrived : ", combined_hashtags)

# run the app
if __name__ == '__main__':
    app()

