import streamlit as st
import pandas as pd
import re
from langchain_community.llms import Cohere
import cohere
import random

# Load sentiment data
sentiment_data = pd.read_csv("mobile_sentiment_analysis_with_scores.csv")

# Initialize Cohere (Replace with your Cohere API Key)
cohere_api_key = 'zrrSpU2jhiLroTQqMSzyC1oaqerIX7JcJ6B8BXvd'
co = cohere.Client(cohere_api_key)

# Function to recommend products based on user query
def recommend_products(query, sentiment_data):
    # Analyze the user's input using Cohere
    response = co.generate(prompt=f"Extract keywords from this query: '{query}'", model='command-xlarge-nightly')
    
    # Process response
    search_keywords = response.generations[0].text.strip().split()
    # st.write("Generated Keywords:", search_keywords)  # Removed logging of generated keywords

    # Escape special characters in the search keywords
    escaped_keywords = [re.escape(keyword) for keyword in search_keywords]
    
    # Filter sentiment data based on query analysis
    recommendations = sentiment_data[sentiment_data['Review'].str.contains('|'.join(escaped_keywords), regex=True, na=False)]

    # If not enough recommendations, try matching against product names
    if recommendations.empty:
        recommendations = sentiment_data[sentiment_data['Product Name'].str.contains('|'.join(escaped_keywords), regex=True, na=False)]
    
    # If still empty, try a fallback with alternative keywords
    if recommendations.empty:
        alternative_keywords = ["gaming", "camera", "battery", "lightweight", "budget", "premium"]
        additional_escaped = [re.escape(word) for word in alternative_keywords]

        recommendations = sentiment_data[
            sentiment_data['Review'].str.contains('|'.join(additional_escaped), regex=True, na=False) |
            sentiment_data['Product Name'].str.contains('|'.join(additional_escaped), regex=True, na=False)
        ]
    
    # Sort products by sentiment score if available
    if 'Sentiment' in recommendations.columns:
        recommendations = recommendations.sort_values(by='Sentiment', ascending=False)

    # Return top 5 products (Name and Price only), adding randomness for variety
    if not recommendations.empty:
        return recommendations[['Product Name', 'Price']].sample(n=min(5, len(recommendations)), random_state=random.randint(0, 100)).reset_index(drop=True)
    
    return pd.DataFrame(columns=['Product Name', 'Price'])  # Return an empty DataFrame if no recommendations

# Set page config
st.set_page_config(page_title="Flipkart Product Recommendation", layout="centered")

# Streamlit App Interface
st.markdown("<h1 style='text-align: center; color: #00BFFF;'>📱 Flipkart Product Recommendation Engine</h1>", unsafe_allow_html=True)
st.markdown("<h3 style='text-align: center; color: #FFFFFF;'>Find the best-rated phones based on user reviews and sentiment analysis!</h3>", unsafe_allow_html=True)

# Add a relevant phone banner image for better UI
st.image("https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQ9RuSjn-p_tJL17pk9npRB0jEqzMug66UNsGhOYZ3HtU0rscRb1iA5ZqnGDUAvdd-P3Xo&usqp=CAU", use_column_width=True)

# User input section with styled markdown
st.markdown("<h4 style='color: #800000;'>🎯 Enter your preferences to get the best phone recommendations:</h4>", unsafe_allow_html=True)  # Maroon color
st.markdown("<p style='color: #FAEBD7;'>For example: <b>best camera phone</b>, <b>lightweight</b>, <b>long battery life</b>, etc.</p>", unsafe_allow_html=True)  # Linen color

# Add disclaimer about input length
st.markdown("<p style='color: #FF4500;'>⚠️ Disclaimer: Please limit your input to 100 words or less.</p>", unsafe_allow_html=True)

# Create a container for input elements
with st.container():
    query = st.text_area("Describe your ideal phone features or type:", height=100)
    recommend_button = st.button("🔍 Recommend")

# Show recommendations when the button is clicked
if recommend_button and query:
    recommended_products = recommend_products(query, sentiment_data)
    
    if not recommended_products.empty:
        st.markdown("<h3 style='color: #32CD32;'>🎉 Top Recommended Phones:</h3>", unsafe_allow_html=True)
        
        # Display product name and price with colored text in a structured format
        for idx, row in recommended_products.iterrows():
            st.markdown(f"<div style='border: 1px solid #00BFFF; border-radius: 10px; padding: 10px; margin: 10px 0; background-color: #1E1E1E;'><p style='font-size:18px; color:#FFFFFF;'><b>{row['Product Name']}</b> - <span style='color:#FF4500;'>₹{row['Price']}</span></p></div>", unsafe_allow_html=True)
    else:
        st.warning("No matching products found. Please try a different query.")

# Add the new footer with your name
st.markdown("<p style='text-align: center; font-size:14px; color:gray;'>Flipkart Product Recommendation Engine by <b>dhina</b></p>", unsafe_allow_html=True)
