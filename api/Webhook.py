import flask

from controller.News import NewsController

api = flask.Flask(__name__)


@api.route("/search", methods=["POST"])
def webhook() -> flask.Response:
    request_data = flask.request.get_json(force=True)
    keywords = request_data.get("keywords", None)
    since_hours = request_data.get("since_hours", 1)
    language = request_data.get("language", None)

    if keywords is None:
        return flask.Response(
            response="Invalid Request - Empty Keywords Data.", status=400
        )

    controller = NewsController()
    try:
        search_result = controller.retrieve_news(keywords=keywords, since_hours=since_hours, language=language)
    except ValueError:
        return flask.Response(
            response="Invalid Request - Empty or Invalid Language Data.", status=400
        )

    if search_result is None:
        r_text = f"No results found. Search Range: NOW-{since_hours}h."
    else:
        r_text = (
            f"A total of {len(search_result)} articles were found. Search Range: NOW-{since_hours}h."
        )

    response = {
        "status": r_text,
        "keywords": keywords,
        "search_result": search_result
    }

    return flask.jsonify(response)


if __name__ == "__main__":
    api.run(port=5000, debug=True)
