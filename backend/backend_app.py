from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_swagger_ui import get_swaggerui_blueprint
import json
import os
from datetime import datetime

# URL Definition
SWAGGER_URL="/api/docs"  # (1) swagger endpoint e.g. HTTP://localhost:5002/api/docs
API_URL="/static/masterblog.json" # (2) ensure you create this dir and file
app = Flask(__name__)
app.config['TEMPLATES_AUTO_RELOAD'] = True
CORS(app)  # This will enable CORS for all routes

# Get the json-file which saves the posts-data
POSTS_FILE = os.path.join(app.static_folder, "posts.json")

# Start the swagger_ui
swagger_ui_blueprint = get_swaggerui_blueprint(
    SWAGGER_URL,
    API_URL,
    config={
        'app_name': 'Masterblog API' # (3) You can change this if you like
    }
)
app.register_blueprint(swagger_ui_blueprint, url_prefix=SWAGGER_URL)


# Handle json_data
def load_posts():
    if not os.path.exists(POSTS_FILE):
        return []
    with open(POSTS_FILE, "r", encoding="utf-8") as file:
        return json.load(file)


def save_posts(posts):
    with open(POSTS_FILE, "w", encoding="utf-8") as file:
        json.dump(posts, file)


@app.route('/api/posts', methods=['GET'])
def get_posts():
    posts = load_posts()
    sort_by = request.args.get('sort', default="id")
    sort_direction = request.args.get('direction', default="asc")
    if not sort_by or not sort_direction:
        return "Wrong sort-parameters given!", 400
    if sort_direction == "desc":
        is_reversed = True
    else:
        is_reversed = False
    sorted_posts = sorted(posts, key=lambda post: post[sort_by], reverse = is_reversed)
    return jsonify(sorted_posts), 200

@app.route('/api/posts', methods=['POST'])
def add_post():
    data = request.get_json()
    posts = load_posts()
    if not data:
        return jsonify("Wrong Parameters given!"), 405

    if not data.get("title") or not data.get("content") or not data.get("author"):
        return jsonify("Parameters not found"), 404

    new_id = max((post["id"] for post in posts), default=0) + 1
    post = {
        "id": new_id,
        "title": data["title"],
        "content": data["content"],
        "author": data["author"],
        "date": datetime.now().strftime("%Y-%m-%d")
    }

    posts.append(post)
    save_posts(posts)
    return jsonify(post), 201


@app.route('/api/posts/<int:post_id>', methods=['DELETE'])
def delete_post(post_id):
    posts = load_posts()
    for post in posts:
        if post['id'] == post_id:
            posts.remove(post)
            save_posts(posts)
            return jsonify({
            "message": "Post with id <post_id> has been deleted successfully."
             }), 200
    return 'Post with the id <post_id> not found', 404


@app.route('/api/posts/<int:post_id>', methods=['PUT'])
def update_post(post_id):
    posts = load_posts()
    data = request.get_json()
    post = next((post for post in posts if post["id"] == post_id), None)

    if not post:
        return "Post not found", 404
    if "title" in data:
        post["title"] = data["title"]
    if "content" in data:
        post["content"] = data["content"]
    if "author" in data:
        post["author"] = data["author"]

    save_posts(posts)
    return jsonify(post), 200


@app.route('/api/posts/search', methods=['GET'])
def search_post():
    posts = load_posts()
    search_fields = ["title", "content", "author", "date"]
    found_posts = []
    for post in posts:
        for field in search_fields:
            query = request.args.get(field)
            if query and query.lower() in post[field].lower():
                found_posts.append(post)
                break

    return jsonify(found_posts), 200





if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5002, debug=True)
