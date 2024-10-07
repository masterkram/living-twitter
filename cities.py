import streamlit as st
import json
import pandas as pd
import numpy as np
import pydeck as pdk


jsonData = open("cities.json", "r").read()
data = json.loads(jsonData)

st.warning(":construction_worker: Article Is Currently Work In Progress :construction:")
st.header("Best Places To Live According To Twitter :palm_tree:")

st.logo("X-Logo.png")

with st.container(border=True):
    st.markdown("“What’s the best place in the world to live right now?”")
    st.markdown(
        "More than 700 replies streamed in, everyone pitched their city or region as the ideal destination."
    )
    st.markdown(
        "From tropical paradises :tropical_fish: to bustling metropolises :city_sunrise:"
    )
    st.markdown(
        "In this post we take on the task of understanding this data, by using our python skills, data science knowledge and critical thinking."
    )
    st.markdown(
        "Whether you’re looking for a new base of operations or just daydreaming, here’s where people say you should go next. 👇"
    )


st.markdown(
    "Back in April [@levelsio](https://x.com/levelsio) asked in a [tweet](https://x.com/levelsio/status/1774172506384994644): what is the best place in the world to live in, right now?"
)

with st.container(border=True):
    st.image("tweet17.png")

st.markdown("This tweet got over 700 replies.")

st.markdown(
    "In the next few days levelsio tweeted again, this time asking for help from someone to scrape the data."
)

st.markdown(
    "\> Be me with nothing to do, **I decide to scrape the data in exchange for internet points.**"
)
st.markdown("\> I write javascript, scrape all of the replies, and sub replies.")

st.markdown("\> I publish this under a github gist.")

st.markdown("\> The answer is... **London**? really...")

st.markdown("\> This cannot be, time to analyze deeper :black_nib:")

st.markdown("Let's go over the process:")

st.subheader("Scraping Twitter")
st.markdown(
    "Spent an hour writing the scraping code by hand, the most interesting part of it is using a Set to make sure we don't get duplicate html nodes in the list."
)

expand = st.expander("Tweet Scraping Code", icon=":material/robot:")
expand.markdown(
    "Voilá the code. It's rustic scraping code that relies on the user scrolling to load new tweets and running the `getTweetsOnPage` function"
)

expand.code(
    """let uniqueNodes = [];
let isReply = false;

function addParentNode(text) {
  if (!uniqueNodes.map(e => e.parent).includes(text)) {
    return uniqueNodes.push({parent: text, replies: new Set()})
  }
}

function gg() {
  let tweetsOnPage = document.querySelectorAll('[data-testid="tweetText"]');
  let indexOfParent = -1;

  for (let i = 0; i < tweetsOnPage.length; i++) {
    const node = tweetsOnPage[i];
    if (isReply) {
      if (i < 2) {
        continue;
      }
      if (i === 2) {
        indexOfParent = uniqueNodes.map(e => e.parent).indexOf(node.innerText);
        console.log(`reply to ${node.innerText} index of parent ${indexOfParent}`);
      }
        console.log(node.innerText);
        uniqueNodes[indexOfParent].replies.add(node.innerText);
      } else {
        addParentNode(node.innerText);
    }
  }
}

function downloadTweets() {
  uniqueNodes.forEach(e => { e.replies = Array.from(e.replies)});
  const result = JSON.stringify(uniqueNodes);
  const fileToSave = new Blob([result], { type: 'application/json;charset=utf-8"'});
  const fileUrl = URL.createObjectURL(fileToSave);
  const link = document.createElement('a');
  link.href = fileUrl;
  link.download = 'city_tweets.json';
  link.click();
}

gg(); // ran this a bunch.
downloadTweets(); // run this when done
"""
)

st.markdown("Cool :sunglasses:, now we have the data.")

st.json(data)

st.markdown("---")

st.subheader("Cleaning The Data :soap:")

st.markdown(
    """
    It turns out that many people **fail to following directions**. This means we need to somehow attribute all replies to a location if possible, drop anything unrelated and decide if countries and regions are fair as a response.
    
    The easiest thing to do in this situation is to make the bug a feature.
    
    This means that we allow regions, countries and cities to be answered.
    
    We then convert any location to a coordinate with the OpenMap api.

    With coordinates we can just plot them on a map. Or get the place where the coordinates are the most concentrated.
    """
)

st.markdown(
    """
    The only problem with this approach was that the **API is not so reliable**:

    Panama City? Yes, Panama City Florida...
            
    Muenster ? Ye, heard of that one it's in north Texas
    
    """
)

pyExpander = st.expander("Data Cleaning Code", icon=":material/soap:")
pyExpander.markdown("The code for the data cleaning.")
pyExpander.code(
    """
from geopy.geocoders import Nominatim
import spacy
import json
import pandas as pd
import time
from tqdm import tqdm

data = json.loads(open("cities.json", "r").read())


class TweetData:
    tweet: str
    location: str
    coordinates: tuple
    replies: list[str]

    def __init__(self, tweet, location, coordinates, replies):
        self.tweet = tweet
        self.location = location
        self.coordinates = coordinates
        self.replies = replies


# Function to extract cities/places
def extract_locations(text):
    # Process the text with spaCy
    doc = nlp(text)

    # Extract location entities (GPE - Geo-Political Entity)
    locations = [ent.text for ent in doc.ents if ent.label_ == "GPE"]

    return locations


def convertTweets(tweets: list[dict]) -> list[TweetData]:
    myResult = []
    for tweet in tqdm(tweets):
        print(f"analyzing: {tweet}")
        locations: list[str] = extract_locations(tweet["parent"])
        myLocation: str = locations[0] if len(locations) > 0 else ""
        print(f"found location == {myLocation}")
        if tweet["parent"] != None and tweet["replies"] != None and myLocation != "":
            coords = get_coordinates(myLocation)
            print(f"coords == {coords}")
            myTweetData = TweetData(
                tweet["parent"], myLocation, coords, tweet["replies"]
            )
            myResult.append(myTweetData)
            print("sleep because we used api")
            time.sleep(7)

    return myResult


nlp = spacy.load("en_core_web_sm")

# Initialize geocoder
geolocator = Nominatim(user_agent="cityLocator")


# Function to get coordinates from location name
def get_coordinates(location_name) -> tuple:
    try:
        location = geolocator.geocode(location_name)
        if location:
            return (location.latitude, location.longitude)
        else:
            return (None, None)
    except Exception as e:
        print(f"Error: {e}")
        return (None, None)


myTweetData = convertTweets(data)
"""
)

st.subheader("Understanding The Data :city_sunset:")

tweet_df = pd.read_csv("my_data.csv")

ICON_URL = open("icon.txt").read()

icon_data = {
    # Icon from Wikimedia, used the Creative Commons Attribution-Share Alike 3.0
    # Unported, 2.5 Generic, 2.0 Generic and 1.0 Generic licenses
    "url": ICON_URL,
    "width": 242,
    "height": 242,
    "anchorY": 242,
}

import random


def jitter(x, jitter_amount=0.0010):
    return x + random.uniform(-jitter_amount, jitter_amount)


tweet_df = tweet_df.drop(tweet_df.columns[[0, 1]], axis=1)
tweet_df["icon_data"] = [icon_data for _ in range(len(tweet_df))]

preview_df = tweet_df.drop(tweet_df.columns[[-1]], axis=1)
st.dataframe(preview_df)

tweet_df["lat"] = tweet_df["lat"].apply(jitter)
tweet_df["lon"] = tweet_df["lon"].apply(jitter)

st.markdown("Now we can visualize the results on a map:")

show_heatmap = st.checkbox("Show Heatmap Layer", value=True)
show_individual = st.checkbox("Show Individual Tweets", value=True)

icon_layer = (
    pdk.Layer(
        type="IconLayer",
        get_icon="icon_data",
        get_size=4,
        size_scale=15,
        data=tweet_df,
        get_position="[lon, lat]",
        pickable=True,
    ),
)

heatmap_layer = pdk.Layer(
    "HeatmapLayer",
    data=tweet_df,
    get_position=["lon", "lat"],
    radius=100,
    elevation_scale=1,
)

layers = []

# Optional Heatmap Layer
if show_heatmap:
    layers.append(heatmap_layer)

if show_individual:
    layers.append(icon_layer)

st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=37.76,
            longitude=-122.4,
            zoom=4,
        ),
        layers=layers,
        tooltip={"text": "{tweet}"},
    )
)

st.markdown("Looks like North Europe, California, Miami and Japan")

st.link_button(
    "discuss on  𝕏",
    url="https://twitter.com/intent/tweet?text=@mark_bruderer+https://living.streamlit.app/",
    type="secondary",
)
