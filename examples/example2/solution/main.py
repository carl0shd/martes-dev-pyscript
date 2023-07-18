from knn_recommender import KnnRecommender

movie_template = Element("movie-template").select(".movie", from_content=True)
output_list = Element("output")

def recommend():
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
