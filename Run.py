import openai
import newspaper
import praw
import pandas as pd
import streamlit as st

# Set up Reddit API credentials
reddit = praw.Reddit(
    client_id='ZKNlVEWehWVYhQ',
    client_secret='pkDHFAuGylXJp-XukM9rrnGX_c0',
    user_agent='redditscrape2',
)

# Define a function to generate potential titles using the OpenAI API
def generate_titles(article_text, subreddit_name):
    prompt = f'You are an expert at Reddit and deeply understand each subreddit community. Their likes, dislikes, what they find compelling, what they find controversial, etc. Your goal is to generate a Reddit post title for an article about {article_text} that would perform well on {subreddit_name}. Make sure the title is highly customized to fit the tone/style/voice of the given subreddit to make it as interesting as possible to that specific audience and adheres to that subreddits rules. The titles should be varied and highly customized for the audience of the subreddit. \n Title:'
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=120,
        n=5,
        stop=None,
        temperature=0.7,
    )
    title = response.choices[0].text.strip()
    return title

def generate_summary(article_text):
    prompt = f'Generate a long and comprehensive summary for an article about the following article that highlights the parts that are most interesting, newsworthy or shocking. Also provide a readout of 20 specific audiences that would be most likely to find the article compelling and vote it up on Reddit. \n Article Text: {article_text} \n Summary: '
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=1500,
        n=1,
        stop=None,
        temperature=0.7,
    )
    summary = response.choices[0].text.strip()
    return summary

st.title("Reddit Article Submission Helper")
st.write("Enter the article URL and your OpenAI API key:")

article_url = st.text_input("Article URL:")
api_key = st.text_input("OpenAI API Key:", type="password")

if st.button("Generate"):
    # Set up OpenAI API credentials
    openai.api_key = api_key

    # Scrape the article text using newspaper3k
    article = newspaper.Article(article_url)
    article.download()
    article.parse()
    article_text = article.text

    # Truncate the article if it's longer than 4,096 tokens
    if len(article.text) > 3096:
        article.text = article.text[:3096]

    # Generate a summary for the article using the OpenAI API
    article_summary = generate_summary(article.text)
    st.write(f"Article Summary: {article_summary}")

    # Use the OpenAI API to generate a sorted list of potential subreddits for the article
    prompt = f'You are an all knowing AI Reddit power user and an expert at understanding subreddit audiences.  Given this article summary and associated list of the most appropriate audiences that would be likely to upvote the article, provide a list of 25 real and well targeted subreddits sorted by most popular first. Consider all subreddits where it might find success. Only suggest subreddits that accept link submissions. Think step by step. Before answering, think deeply about what an audience might like. Please provide as wide a variety of results as possible and prioritize high volume subreddits. Do not suggest image, gif, or video only subreddits unless the article contains this content. \n Article Summary and Audience Readout: \n ### {article_summary} ###  \n Suggested Subreddits for Submission: \n'
    response = openai.Completion.create(
        engine='text-davinci-003',
        prompt=prompt,
        max_tokens=2000,
        n=5,
        stop=None,
        temperature=0.5,
    )
    potential_subreddits = response.choices[0].text.strip().split('\n')

    # Generate potential titles for the article tailored to each recommended subreddit
    potential_titles = {subreddit_name: generate_titles(article_summary, subreddit_name) for subreddit_name in potential_subreddits}

    # Create a Pandas DataFrame to store the results
    df = pd.DataFrame({
        'Subreddit': potential_subreddits,
        'Title': list(potential_titles.values()),
    })

    st.write(df)
