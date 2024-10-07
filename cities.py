import streamlit as st
import json
import pandas as pd
import numpy as np
import pydeck as pdk


data = json.loads(open("cities.json", "r").read())

st.header("Twitter Votes Best City To Live :palm_tree:")

st.logo("X-Logo.png")

st.markdown(
    "Back in April [@levelsio](https://x.com/levelsio) asked in a [tweet](https://x.com/levelsio/status/1774172506384994644): what is the best place in the world to live in, right now?"
)

with st.container(border=True):
    st.image("tweet17.png")

st.markdown(
    "In the next few days he tweeted again, this time asking for help from someone to scrape the data."
)

st.markdown(
    "\> Be me with nothing to do, I decide to scrape the data in exchange for internet points."
)
st.markdown(
    "\> Wrote javascript code to gather the tweets as json, including the nested replies. The replies often either support the original vote or are against the city that's proposed"
)

st.subheader("Scraping Twitter")
st.markdown(
    "Spent an hour writing the scraping code by hand, the most interesting part of it is using a Set to make sure we don't get duplicate html nodes in the list :wink:"
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

getTweetsOnPage();
downloadTweets();
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
    """
)

st.markdown(
    "Panama City? yep Panama City Florida... Muenster ? yep heard of that it's in north Texas"
)

pyExpander = st.expander("Data Cleaning Code", icon=":material/soap:")
pyExpander.markdown(
    "Voilá the code. It's rustic scraping code that relies on the user scrolling to load new tweets and running the `getTweetsOnPage` function"
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


tweet_df["icon_data"] = [icon_data for _ in range(len(tweet_df))]

st.dataframe(tweet_df)

tweet_df["lat"] = tweet_df["lat"].apply(jitter)
tweet_df["lon"] = tweet_df["lon"].apply(jitter)

st.pydeck_chart(
    pdk.Deck(
        map_style=None,
        initial_view_state=pdk.ViewState(
            latitude=37.76,
            longitude=-122.4,
            zoom=4,
        ),
        layers=[
            pdk.Layer(
                type="IconLayer",
                get_icon="icon_data",
                get_size=4,
                size_scale=15,
                data=tweet_df,
                get_position="[lon, lat]",
                pickable=True,
            ),
        ],
        tooltip={"text": "{tweet}"},
    )
)

st.button(
    "discuss on  𝕏",
    type="secondary",
)
