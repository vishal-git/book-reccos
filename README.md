# A Tutorial to create a simple book-search app using a vector database deplyed on Weaviate

This tutorial will walk you step-by-step to create a local app that can be used to search books (from a collection) based on a search phrase. We will use a vector database from Weaviate to store the vector embeddings for book descriptions and genres. We will also make a call to OpenAI API to convert the search query into an embedding before performing vector similarity search to identify the best matches.

Please note that this is a very detailed tutorial :) so feel free to skip over some sections if you are already familiar with those concepts/processes covered in those sections.

# Tools

Here's the list of all tools we will use for this project:

1. Vector database provided by Weaviate
2. OpenAI API for creating embeddings
3. Streamlit for the web-app frontend and backend

# Sources

* [The Books dataset](https://github.com/scostap/goodreads_bbe_dataset) contains details for more than 63,000 books.
* [A Movie Search Engine tutorial](https://towardsdatascience.com/recreating-andrej-karpathys-weekend-project-a-movie-search-engine-9b270d7a92e4)  by Leonie Monigatti
* [Weaviate documentation and guidelines for search](https://weaviate.io/developers/weaviate/search)
* [Streamlit API reference](https://docs.streamlit.io/library/api-reference)

# Step 1: Set up

## 1 (a): Clone this repo into your local directory.

No explanation needed for this step :)

## 1 (b): Install all Python dependencies.

All Python dependencies are listed in the `requirements.txt` file. Before installing all dependencies, let's create a Python virtual environment. I like to use the in-built `venv` functionality that comes with the base Python installation. But feel free to use any other tools such as `conda` or `poetry`.

Here are the commands you can run to (a) create a Python virtual environment, (b) activate it, and (c) install all dependencies:

```
python -m venv .venv
source . .venv/bin/activate
pip install -r requirements.txt
```

Please note that I am using Python 3.10 for this project. (You can check your Python version using the following command: `python --version`.)

## 1 (c): Create a free vector database on Weaviate.

Click on [this link](https://console.weaviate.cloud/) and follow instructions to create a free-tier account. Then follow the instructions below to create a free vector database. [Please note that these steps may change in the future. For the latest instructions, you can check out their official documentation [here](https://weaviate.io/developers/wcs/quickstart).

Once you create and account and login, you will a screen like this:

<img src='../misc/weaviate_home_screen.png' width=500>

Under _Free Sandbox_ tab, click on **Create cluster** button, provide a meaningful name to your cluster and then click on **Create**. Make sure the _Enable Authentication_ option is checked. Please note that the cluter will stay up only for 14 days for a free-tier account. If you would like to preserve the vector database beyond 2 weeks, you'd have to purchase a paid plan.

<img src='../misc/weaviate_create_cluster.png' width=500>

A few minutes after you are done with creating a new cluster, you will see it appear on your main page. There should be a green check-mark on it.

<img src='../misc/weaviate_cluster_created.png' width=500>

Now we need to create an API key to authenticate access. Click on the **Details** button (shown in the image above), and follow instructions to create an API key. Copy the API key. We will use the `.env_template` file to store this API key. This is the content of this template file:

<img src='../misc/env_template.png' width=400>

Rename the `.env_template` file to `.env`, and add the Weaviate URL (which can be found under the **Details** tab; see below) and the API key that you just copied.

<img src='../misc/weaviate_cluster_url.png' width=500>

> Suggested Reading: Familiarize yourself with some [Weaviate core concepts](https://weaviate.io/developers/weaviate/concepts)

## 1 (d): Check connectivity to the vector database.

Let's make sure that we are able to connect to the Weaviate cluster via Python. We can use the `check_client.py` script for this purpose. This script will read the information from the `.env` file and try to connect to the cluster. You can run the script using the following command:

```
python src/check_client.py
```

Note that you should run the command from the root directory of the project (i.e., `book-reccos`).

This script simply calls the `get_client()` function from the `utils.py` module. The function (see below) contains code to use the correct authentication keys and initializes a connection with the vector database. 

<img src='../misc/code_get_client.png' width=500>

**Note:** For now, we call this function with `openai=False` because we are just interested in ensuring connectivity with the cluster. Later on, we will initialize this connection _with_ the OpenAI API key because we will need it for creating text embeddings.

This should generate an output that contains the details of the vector database, including its properties like `class` and `description`. If this code throws out an error, there is an issue with the API key or the Weaviate URL provided in the `.env` file. Please double-check to make sure those values are correct.

Now that we have successfully created a Weaviate cluster (aka Weaviate Cloud Services (WCS) Instance), we are _almost_ ready to populate it with some vector embeddings! One last thing we need to take care of is the **API token** from OpenAI. 

If you already have an API token available, you can skip this part. Just make sure that you add this token to the `.env` file.

## 1 (e): Create an OpenAI API token.

Click on [this link](https://platform.openai.com/) to visit the OpenAI website and follow instructions to create an API token. You will have to provide your credit card information. The total cost of running all code in this tutorial should be minimal (under $5). 

If you would like to use a free option instead, you can use an open-source model from [HuggingFace](https://huggingface.co/blog/getting-started-with-embeddings). If you decide to do this, you will need to add the HuggingFace API key in `.env` and you will also need to change the way the client connection is invoked in `utils.py`.

# Step 2: Generate and store embeddings into the vector database. 

As mentioned earlier, we will use the Books dataset for this purpose. But feel free to use any other dataset that you might be interested in, such as movies, shows, products. All we really need is a text column that contains the description of those items. We will first convert these text descriptions into text embeddings and then store them into our vector database.

> Suggested Reading: Check out the [OpenAI documentation on embeddings](https://platform.openai.com/docs/guides/embeddings/what-are-embeddings).

We will use OpenAI's `text-embedding-ada-002` embedding model (which is the default model) to create text embeddings. 

## 2 (a): Read the Books dataset.

We will read the Books dataset from the `./data` directory and then clean the database just in case the **Books** class already exists. Note that if you are running this for the first time, you don't need to run this "clean-up" part because the database is empty. But you may need to run this code multiple times (e.g., if you get some errors), in which case it would be a good practice to perform a clean-up before populating/repopulating the database.

<img src='../misc/code_read_data.png' width=600>

Note that I am using "Books" as the name of the schema (see below); if you used a different name, you should change that in this code.

**Terminology alert**: Newer Weaviate documentation discuses "collections." Older Weaviate documentation refers to "classes" instead. Expect to see both terms throughout the documentation. For practical purposes, we can think of these as "schemas".

Now let's create a schema, called "Books" and provide some important details such as:

* `description`: Provide a short description of the schema
* `vectorizer`: We will use OpenAI's `text2vec-openai` vectorizer; check out [this link](https://weaviate.io/developers/weaviate/modules) link for more details
* `vectorIndexConfig`: We will use cosine similarity to compare the text embedding with the query embedding
* `moduleConfig`: Here we provide some more details about the vectorizer; check out [this link](https://weaviate.io/developers/weaviate/manage-data/collections#specify-vectorizer-settings) for more details

[This](https://weaviate.io/developers/weaviate/manage-data/collections) page provides more information about additional configurations, such as sharding. 

## 2 (b): Configure the schema.

<img src='../misc/code_books_schema.png' width=500>

Now let's set up some `properties` for this schema (see below). We will set `text2vec-openai[skip]` to `True` for both `bookId` and `title` because we are not going to convert them into text embeddings. We will set it to `False` for the `description` field. In addition, we will also set it to `False` for the `genres` field. This way, we will be creating text embeddings for both the `description` and `genres` field, both of which will be converted into text embedding before loading them into the database.

<img src='../misc/code_books_schema_properties.png' width=400>

## 2 (c): Create the schema.

The following line of code finally creates an empty schema in the database called "Books":

<img src='../misc/code_create_schema.png' width=300>

## 2 (d): Load data into that schema.

Now that an empty schema has been created, it's time to load it up with some embeddings! We will do this in batches. Our dataset is pretty small, so we will use a batch size of 10. You can read more about batch import on [this link](https://weaviate.io/developers/weaviate/manage-data/import). 

<img src='../misc/code_batch_import.png' width=420>

Note that I have added a `try` and `except` clause because some of the entries from the dataset were causing issues. I think this was due to some empty (null) values as well as some foreign language content in the description column. You may see some warnings as well, but as long as this doesn't error out, you should be fine.

If all worked well, you should now have a vector database deployed in the cloud! Congratulations!

Now if you go back to your Weaviate console, and click on the **Details** button, you will see that the database is now populated with some objects.

<img src='../misc/weaviate_database_objects.png' width=400>

Please note that due to some data quality and/or OpenAI API related issues, the total number of objects (aka embeddings) is only around sixteen thousand. This is happening due to the following JSON error: `An exception occurred: Out of range float values are not JSON compliant`. We will ignore this for now and continue to the next steps with these embeddings in the database.

# Step 3: Perform book search.

Now that we have a database full of vectors ready, we can perform search and retrieve relevant books.

> Suggested Reading: Familiarize yourself with various topics realted to search from [Weaviate documentation on Search](https://weaviate.io/developers/weaviate/search).

## 3(a): Keyword search.

In Weaviate, we can perform a keyword search using "BM25 (Best match 25)" algorithm. This algorithm has some limitations -- namely, it doesn't consider semantic meanings and its heavy reliance on term frequency -- but we will try it as our first shot at getting some book recommendations from the vector database.

> Suggested Reading: Check out [this article](https://medium.com/@evertongomede/understanding-the-bm25-ranking-algorithm-19f6d45c6ce) on BM25.

<img src='../misc/code_keyword_search.png' width=450>

You can run this script by using the following command:

```
python src/keyword_search.py
```

This code searched for the top three recommendations for the search word "magic". Here are the three results that I got:

```
{
  "data": {
    "Get": {
      "Books": [
        {
          "_additional": {
            "score": "2.7072732"
          },
          "description": "Xanth was the enchanted land where magic ruled - where every citizen had a special spell only he could cast. It was a land of centaurs and dragons and basilisks.For Bink of North Village, however, Xanth was no fairy tale. He alone had no magic. And unless he got some - and got some fast! - he would be exiled. Forever!But the Good Magician Humfrey was convinced that Bink did indeed have magic. In fact, both Beauregard the genie and the magic wall chart insisted that Bink had magic. Magic as powerful as any possessed by the King or by Good Magician Humfrey - or even by the Evil Magician TrentBe that as it may, no one could fathom the nature of Bink's very special magic. Bink was in despair. This was even worse than having no magic at all..and he would still be exiled!",
          "genres": "['Fantasy', 'Fiction', 'Humor', 'Science Fiction Fantasy', 'Young Adult', 'Magic', 'Adventure', 'Science Fiction', 'High Fantasy', 'Comedy']",
          "title": "A Spell for Chameleon"
        },
        {
          "_additional": {
            "score": "2.6994038"
          },
          "description": "The Last Herald-Mage contains Magic's Pawn, Magic's Promise and Magic's Price.",
          "genres": "['Fantasy', 'Fiction', 'Science Fiction Fantasy', 'Magic', 'Epic Fantasy', 'High Fantasy', 'LGBT', 'Romance', 'Young Adult', 'Gay']",
          "title": "The Last Herald-Mage"
        },
        {
          "_additional": {
            "score": "2.5713503"
          },
          "description": "Magic is all around. You just have to believe.Do you believe?\u201cLife is too short to be cynical. So smile, dare to believe and leave the door open for Magic.\u201dI live by those words. I\u2019ve searched the world for answers to questions that only seem to lead to more questions. Imagine my surprise when I discover Magic right across the hall... wearing nothing but an apron and a smile...I\u2019m Laney Evans, and I believe in Magic. \u201cThe secret ingredient is always Magic.\" I\u2019ve lived my whole life with Magic surrounded by a wacky, prank crazed, magical family. I thought I had the recipe for happiness all spelled out until I caught sight of Laney Evans, and now I know that the best is yet to come!I\u2019m Max Cross, and I believe in love at first sight. (I\u2019m not a creeper, damn it.)",
          "genres": "['Fantasy', 'Romance']",
          "title": "Cross the Hall Magic"
        }
      ]
    }
  }
}
```

We can see that, since this is a *literal* keyword search (and not a semantic one), we get three recommendations whose descriptions (or genres) contain the search word "magic".

Since we also requested the `score` in our query, we see that these scores are provided in an attribute called `_additional`. The higher the score, the better the match. Hence, the results are sorted from high to low scores.

## 3(b): Vector search.

Now let's move on to the main part of this tutorial: retrieval using vector similarity search. Here's how this works:

1. The user provides a search phrase, e.g., "adventure novel with some philosophy".
2. We call the OpenAI API to convert this search phrase into an embedding vector. Let's call it the search vector.
3. Now we calculate the cosine similarity between this search vector and all other book embedding vectors that we have stored in our vector database.
4. The top results, based on the similarity score, are returned to the user.

It's pretty simple!

> Suggested Reading: Here's a [brief introduction](https://www.pinecone.io/learn/what-is-similarity-search/) to how vector similarity search works (from Pinecone). And while you're at it, check out the amazing educational resources from Pinecone's [Learning Center](https://www.pinecone.io/learn/).

The function that performs this vector search is located in `src/vector_search.py` file:

<img src='../misc/code_vector_search.png' width=500>

We search in the **Books** schema, and ask for the following four fields in the search results: `bookId`, `title`, `genres`, and `description`. We provide the keyword with the `concepts` parameter inside `with_near_text()` option. This is the search phrase that will be converted into a query embedding and then compared against all text embeddings we have in the database using a similarity search. We restrict the search results to three, and as also ask the cosine similarity distance measure to be returned with the query results.

In line #18 above, we convert the response into JSON format. Since our database is not very large, the query may yield zero results. We capture that exception using `try` and `except` block. If no books are found that match with the search phrase, we print the following message: "No results found."

Finally, we convert the response into a Python list and apply a filter to discard any results that have a distance score higher than 0.2. This threshold value seems to be working well based on a few examples that I checked. Feel free to change it if needed -- especially if we decided to use a different dataset. You can remove this threshold first, increase the value for `with_limit()` (line #11) and check out the search results to find a more appropriate threshold.

You can perform some search by directly running the `src/vector_search.py` file and changing the search phrase in line #39 of this script. 

# Step 4: Create an app.

Okay, now let's create an web-app using **Streamlit**. The app can be launched locally in a brower where a user can perform a search and see the results.   

> Suggested Reading: You might want to familarize yourself with some basic Streamlit concepts on this [documentation page](https://docs.streamlit.io/library/get-started). 

Our app is very light. It will have a single web page, with a text input area where the user can enter a search phrase. Once the vector search is complete, we will display the results on the same page. Let's take a look at the code step by step.

First, we need a title and a subtitle text for the page. Let's set them up using `title()` and `write()`. Note that we can use the two colon format to include emojis, e.g., `:books:` will display an emoji for books.

<img src='../misc/code_app_title.png' width=450>

Now let's create a user input area where user can type in the search phrase. We do this by creating a Streamlit "form" called **book-search** and we create a user-input area using the `text_input()` property of this form. We also add a **Submit** button at the bottom of this form.

<img src='../misc/code_app_user_input.png' width=500>

Based on this code, this is what our app would look like (once launched):

<img src='../misc/app_title.png' width=500>

The next step is to grab the text input entered by the user and call the vector search to retrieve results. Here's the code:

<img src='../misc/code_app_submit.png' width=500>

The code will run only if the user clicks the submit button. We first need to initialize a connection the vector dataset. We do this in line # 24. Then we call the `vector_search()` function along with the client and the search phrase (aka the "query").

If no recommendations are found, then we simply print a message. 

Otherwise, we iterate through each of the top three results. For each result, we create two columns, the first one will be used to display the book cover image and the second one will be used to display the book description text. We set the width of these two columns as `[1, 3]`, meaning that the second column (which will be used to display the book description) will be three times as wide as the first one. Check out the [documentation page](https://docs.streamlit.io/library/api-reference/layout/st.columns) for more details on this.

Now the original dataset does contain a column called `coverImg` that contains a public URL for the book cover image. We will use this to grab the cover image from that URL and display it on our app. I have read the dataset into a `pandas` dataframe called `df`. We grab the URL from the `coverImg` column for that specific `bookId` from the search results. And then we display that image using `st.image()` option.

In the second colum, called `text_col`, we simply write the book title and description. Note that we could have grabbed these two values from the `df` dataset, but we already have them available in the search results. We also include the `distance` value at the top for reference. Note that lower values indicate better matches, and the results are sorted from low to high distance scores. Here's one example of search result for the search phrase ""

<img src='../misc/app_sample_result.png' width=500>

You can launch this app by running the following command: `streamlit run src/app.py`. 

That should print a pair of local and network URLs as shown below. You can Ctrl+Click on either one to launch the app in you browser.

<img src='../misc/app_launch.png' width=500>

And you should be able to perform a search and view the results! Congratulations! :)

