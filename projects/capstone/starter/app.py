import os
from flask import Flask, request, abort, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
from models import Actor, Movie, setup_db


def create_app(test_config=None):
    # create and configure the app
    app = Flask(__name__)
    setup_db(app)
    CORS(app)
    Movies_Per_Page = 3

    def paginate_movies(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * Movies_Per_Page
        end = start + Movies_Per_Page
        if start > len(selection):
            abort(404)
        movies = [movie.format() for movie in selection]
        current_movies = movies[start:end]
        return current_movies

        # This method id added to sort list od categories

    def format_movies(movies):
        if len(movies) == 0:
            abort(404)
        formated_movies = []
        index = 0

        for index in range(len(movies)):
            
            current_movie={
                'id': movies[index]['id'],
                'title': movies[index]['title'],
                'release_date': movies[index]['release_date'],

                }
            formated_movies.append(current_movie)
        return formated_movies

    @app.after_request
    def after_request(response):
        response.headers.add(
            'Access-Control-Allow-Headers',
            'Content-Type, Authorization'
            )
        response.headers.add(
            'Access-Control-Allow-Methods',
            'GET, POST, PATCH, DELETE, OPTIONS'
            )
        return(response)

    @app.route('/movies', methods=['GET'])
    def get_movies():
        try:
            movies = Movie.query.order_by(Movie.title).all()
            if len(movies) == 0:
                abort(404)
        except:
            abort(422)
        
        current_movies = paginate_movies(request, movies)
        return(jsonify({
            'success': True,
            'movies': format_movies(current_movies),
            'status_code': 200
            })), 200










    @app.errorhandler(404)
    def not_found(error):
        return jsonify({
            'success': False,
            'error': 404,
            'message': 'resource not found'
        }), 404

    @app.errorhandler(400)
    def bad_request(error):
        return jsonify({
            'success': False,
            'error': 400,
            'message': 'bad request'
        }), 400

    @app.errorhandler(500)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 500,
            'message': 'internal server error'
            }), 500

    @app.errorhandler(422)
    def method_not_allowed(error):
        return jsonify({
            'success': False,
            'error': 422,
            'message': 'Unprocessable Entity'
        }), 422


    return app

APP = create_app()

if __name__ == '__main__':
    APP.run(host='0.0.0.0', port=8080, debug=True)