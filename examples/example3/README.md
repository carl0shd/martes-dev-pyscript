## Example 3 - Deploying ML Model

This example demonstrates the deployment of a machine learning model, specifically a K-Nearest Neighbors (KNN) model for recommendations. The code and concepts used in this example are derived from [pyscript-tutorial](https://github.com/Cheukting/pyscript-tutorial/blob/main/chapter_3/chapter_3.md).

Before proceeding with this example, there are a few initial steps to follow. We have included two additional files: `knn_recommender.py` and `requirements.txt`. The `knn_recommender.py` file contains the Python script that implements an item-based collaborative filtering recommender using the [KNN algorithm](https://www.javatpoint.com/k-nearest-neighbor-algorithm-for-machine-learning). The `requirements.txt` file lists the necessary dependencies for running the script.

---

## Step 1 - Prepare the data and train the model

In this example, we will be using [MovieLens Datasets](https://grouplens.org/datasets/movielens/latest/) to build a recommender system based on KNN Item-Based Collaborative Filtering. Get the full data set from [MovieLens Datasets](https://files.grouplens.org/datasets/movielens/ml-latest.zip) and put the movies.csv and ratings.csv in this folder

Create a new Python environment, for example, using venv:
```sh
python -m venv .venv
```
then you can activate it, like this in Unix system (macOS and Linux):
```sh
source .venv/bin/activate
```
After that, install all the requirements:
```sh
pip install -r requirements.txt
```
Run the code in knn_recommender.py to train the model. For example using this command:
```sh
python knn_recommender.py --movie_name "Iron Man" --top_n 10
```
It may take a while to run. When it is finished, it will show you the recommendation and there will be two files, `hashmap.p` and `movie_user_mat_sparse.p`, generated. The option `--movie_name` and `--top_n` does not matter as we do not care about the result. We only want to run this code once to generate the `hashmap.p` and `movie_user_mat_sparse.p` which we will be using for the deployment in the following exercises.

## Step 2 - Using fetch and launching a server

We can start with `index.html`. The first thing we want to is to add the `hashmap.p` and `movie_user_mat_sparse.p` to our application (this will load the files into the web browser VM, without doing it, the application will not be able to access those files). In PyScript, it is straightforward. It can be done with [[fetch]] in <py-config>. In <py-config> tag pairs:

And in the `index.html` add the `<py-config>` at the top of the body

```html
<py-config>
    packages = ["pandas", "scikit-learn", "fuzzywuzzy"]
    [[fetch]]
    files = ["hashmap.p", "movie_user_mat_sparse.p"]
</py-config>
```

## Step 3 - Set the action for the button

When we start with the `index.html`, we have already added some interactive elements. One of them is the `Recommend!` button. Before we make the recommendation work, lets make sure we can have interactivity of this button with our Python code.

When we work with interactive elements, we need event handlers. To do that, we will add a function that just print out "Recommended!" like this:

```py
def recommend():
    print("Recommend!")
```

Next, in the `index.html` locate the `Recommend!` button and add the event handle to the element like this: `py-click="recommend"`

That button needs to looks like this:

```html
<button id="run-btn" py-click="recommend()" type="submit">
    Recommend!
</button>
```

**Note: PyScript required button to have an id attribute, when using the py-click attribute**


Save and refresh the page, press the `Recommend!` button and see what happened.

## Step 4 - Taking input values

Besides the `Recommend!` button, we also have the input boxes `fav-movie` and `top-n`, lets see how we can get the values from them.

So, lets create 2 elements corresponding to the boxes:

```py
fav_movie_box = Element('fav-movie')
top_n_box = Element('top-n')
```

and get their values:

```py
fav_movie = fav_movie_box.value
top_n = top_n_box.value
```

However, I prefer to do it in one go:

```py
movie_name = Element('fav-movie').value
top_n = Element('top-n').value
```

Then, we can use those values in our output:

```py
print("Recommend!")
print(f"{top_n} recommendation based on {movie_name}")
```

Now code with in the `<py-script>` tag pairs looks like this:
```html
<py-script>
    def recommend():
        movie_name = Element('fav-movie').value
        top_n = Element('top-n').value
        print("Recommend!")
        print(f"{top_n} recommendation based on {movie_name}")
</py-script>
```

Refresh the page and try it out, first with "Iron man" and "10", it looks alright, however, you may spot a problem that we may have. Now try "Iron man" and "random" as input. The code will take the value as `string` by default.

There are many ways of handling it, for example try converting `top_n` to integer if failed give user a warning. For simplicity here, we will assume the default of `top_n` is 10 and if anything failed, we will just use 10 as the `top_n` value:

```py
try:
  top_n = int(top_n)
except:
  top_n = 10
```

Before continue we can extract the code inside of `<py-script>` tag to a file, to have better organization and syntax highlighting

So, lets create a `main.py` and add the content:

```py
def recommend():
    movie_name = Element('fav-movie').value
    top_n = Element('top-n').value

    try:
        top_n = int(top_n)
    except:
        top_n = 10

    print("Recommend!")
    print(f"{top_n} recommendation based on {movie_name}")
```

And in the `index.html` import this new file
```diff
-<py-script>
-    def recommend():
-        movie_name = Element('fav-movie').value
-        top_n = Element('top-n').value
-        try:
-           top_n = int(top_n)
-        except:
-           top_n = 10
-        print("Recommend!")
-        print(f"{top_n} recommendation based on {movie_name}")
-</py-script>
+<py-script src="./main.py"></py-script>
```

## Step 4 -- Give recommendations

To use our trained recommender, we need to first include the `knn_recommender.py` in `fetch` so our application have access to it:

In the <py-config>` tag
```diff
packages = ["pandas", "scikit-learn", "fuzzywuzzy"]
[[fetch]]
-files = ["hashmap.p", "movie_user_mat_sparse.p"]
+files = ["hashmap.p", "movie_user_mat_sparse.p", "knn_recommender.py"]
```

This allow us to import the `KnnRecommender` in the `main.py` file:

```py
from knn_recommender import KnnRecommender
```

Save and refresh the page, you will see a warning about installing python-Levenshtein, ignore it for now as we will not be using it.

Next, in the `recommend` function, we want to create the `KnnRecommender` instances and set the model parameters

```py
recommender = KnnRecommender()
recommender.set_filter_params(50, 50)
recommender.set_model_params(20, 'brute', 'cosine', -1)
```

Now, instead of printing the input:

```py
print("Recommend!")
print(f"{top_n} recommendation based on {movie_name}")
```

We want to make recommendations:

```py
print(recommender.make_recommendations(movie_name, top_n))
```

However, if `movie_name` is empty, there will be an error in the recommender. To avoid it, we better check if the `movie_name` is empty:

```py
if movie_name:
    print(recommender.make_recommendations(movie_name, top_n))
else:
    print("Sorry we need a movie name.")
```

Combining everything, now in the `main.py` file we should have:

```py
from knn_recommender import KnnRecommender

def recommend():
    movie_name = Element('fav-movie').value
    top_n = Element('top-n').value

    try:
        top_n = int(top_n)
    except:
        top_n = 10

    recommender = KnnRecommender()
    recommender.set_filter_params(50, 50)
    recommender.set_model_params(20, 'brute', 'cosine', -1)

    if movie_name:
        print(recommender.make_recommendations(movie_name, top_n))
    else:
        print("Sorry we need a movie name.")
```

Save and refresh and get some recommendation from the recommender.


## Exercise 5 -- Better presentation

Now everything works, however, the presentation is not the best, it just print out the result in a command line style. To make it worse, it prints out everything including the warning where the users should not be seeing. We are going to fix it in the exercise.

Now instead of printing the output like this:

```py
print(recommender.make_recommendations(movie_name, top_n))
```

We turn on the `recommendation_only` flag and store the result:

```py
recommendation = recommender.make_recommendations(movie_name, top_n, recommendation_only=True)
```

As we are developing, let first print out `recommendation` and see how it looks like. Now we have:

```py
from knn_recommender import KnnRecommender

def recommend():
    movie_name = Element('fav-movie').value
    top_n = Element('top-n').value

    try:
        top_n = int(top_n)
    except:
        top_n = 10

    recommender = KnnRecommender()
    recommender.set_filter_params(50, 50)
    recommender.set_model_params(20, 'brute', 'cosine', -1)

    if movie_name:
        recommendation = recommender.make_recommendations(movie_name, top_n, recommendation_only=True)
        print(recommendation)
    else:
        print("Sorry we need a movie name.")
```

Save and refresh, try with "Iron man" again and now you see instead of a listed output, we got a list back from the `make_recommendations`


Next, we want to present the Python list that we got as a `List` element in `html`. Here's why we have these tags in our `index.html` when we start:

```html
<div><ol id="output"></ol></div>
<template id="movie-template"><li class="movie"></li></template>
```

So what we will do is to generate a clone of the `<li>` element for each of the recommended movies, customize the text, then we will add them to the `output` `<ol>` element. Before we do that, we need to select those elements so we can use them in the code:

```py
movie_template = Element("movie-template").select(".movie", from_content=True)
output_list = Element("output")
```

You can add them to the top after the `import` statement. Then we will replace the `print(recommendation)` with:

```py
for i, recommend in enumerate(recommendation):
    movie_html = movie_template.clone(f"movie_{i}")
    movie_html.element.innerText = recommend
    output_list.element.appendChild(movie_html.element)
```


Then, we replace the `print` statement when we have no `movie_name`:

```py
output_list.element.innerText = "Sorry we need a movie name."
```

Last, since we only want the most recent result to be shown, we will clear the last result when we press the button. Add this to the top of the `recommend` function:

```html
output_list.element.innerHTML = ""
```

To double check, now we have:

```py
from knn_recommender import KnnRecommender

movie_template = Element("movie-template").select(".movie", from_content=True)
output_list = Element("output")

def recommend(evt=None):
    output_list.element.innerHTML = ""
    movie_name = Element('fav-movie').value
    top_n = Element('top-n').value

    try:
        top_n = int(top_n)
    except:
        top_n = 10

    recommender = KnnRecommender()
    recommender.set_filter_params(50, 50)
    recommender.set_model_params(20, 'brute', 'cosine', -1)

    if movie_name:
        recommendation = recommender.make_recommendations(movie_name, top_n, recommendation_only=True)

        for i, recommend in enumerate(recommendation):
            movie_html = movie_template.clone(f"movie_{i}")
            movie_html.element.innerText = recommend
            output_list.element.appendChild(movie_html.element)
    else:
        output_list.element.innerText = "Sorry we need a movie name."
```

Now save and refresh and have a play. The only thing that get in the way is the warning that got printed on the py-terminal. To switch it off, we just need to add `terminal = false` to the `py-config` tag

```diff
+terminal = false
packages = ["pandas", "scikit-learn", "fuzzywuzzy"]
[[fetch]]
files = ["hashmap.p", "movie_user_mat_sparse.p", "knn_recommender.py"]
```

Now for the final time, save and refresh. This time, we have a reasonable recommender app.
