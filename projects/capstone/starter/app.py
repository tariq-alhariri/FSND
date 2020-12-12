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
    ELEMENT_By_PAGE = 3

    def paginate_elemets(request, selection):
        page = request.args.get('page', 1, type=int)
        start = (page - 1) * ELEMENT_By_PAGE
        end = start + ELEMENT_By_PAGE
        if start > len(selection):
            abort(404)
        print('----------------------> type', isinstance(selection[0], Actor))
        if isinstance(selection[0], Movie):
            elemets = [movie.format() for movie in selection]
        else:
            elemets = [actor.format() for actor in selection]
        current_elements = elemets[start:end]
        return current_elements

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

    def format_actors(actors):
        if len(actors) == 0:
            abort(404)
        formated_actors = []
        index = 0

        for index in range(len(actors)):
            
            current_actor={
                'id': actors[index]['id'],
                'name': actors[index]['name'],
                'age': actors[index]['age'],
                'gender': actors[index]['gender'].value,
                }
            formated_actors.append(current_actor)
        return formated_actors
   
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
        
        current_movies = paginate_elemets(request, movies)
        return(jsonify({
            'success': True,
            'movies': format_movies(current_movies),
            'status_code': 200
            })), 200


    @app.route('/movies/<int:movie_id>', methods=['GET'])
    def get_movie(movie_id):
        try:
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
            return jsonify({
                'status_code': 200,
                'success': True,
                'movie': Movie.format(movie),
                }), 200
        except:
            abort(404)

    @app.route('/movies', methods=['POST'])
    def add_movie():
        data = request.get_json()
        if (data.get('title') and data.get('release_date')):
            new_movie = Movie(
                title=data.get('title', None),
                release_date=data.get('release_date', None),
                )
            print('----------------------> title', new_movie.title, '--------> ', new_movie.release_date)
            try:
                Movie.insert(new_movie)
                return jsonify({
                    'success': True,
                    'status_code': 201,
                    'question_id': new_movie.id,
                }), 201
            except:
                abort(422)
        else:
            abort(422)


    @app.route('/movies/<int:movie_id>', methods=['PATCH'])
    def update_movie(movie_id):
        try:
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
            data = request.get_json()
            if data.get('title'):
                movie.title=data.get('title')
            if data.get('release_date'):
                movie.release_date=data.get('release_date')
            Movie.update(movie)
            return jsonify({
                'status_code': 200,
                'success': True,
                'movie': Movie.format(movie),
                }), 200
        except:
            abort(404)

    @app.route('/movies/<int:movie_id>', methods=['DELETE'])
    def delete_movie(movie_id):
        try:
            movie = Movie.query.filter(Movie.id == movie_id).one_or_none()
            if movie:
                Movie.delete(movie)
            return jsonify({
                'status_code': 200,
                'success': True,
                'deleted': movie_id ,
                }), 200
        except:
            abort(404)

    @app.route('/actors', methods=['GET'])
    def get_actors():
        try:
            actors = Actor.query.order_by(Actor.name).all()
            if len(actors) == 0:
                abort(404)
        except:
            abort(422)
        
        current_actors = paginate_elemets(request, actors)
        return(jsonify({
            'success': True,
            'actors': format_actors(current_actors),
            'status_code': 200
            })), 200
    @app.route('/actors/<int:actor_id>', methods=['GET'])
    def get_actor(actor_id):
        try:
            actor = Actor.query.filter(Actor.id == actor_id).one_or_none()
            return jsonify({
                'status_code': 200,
                'success': True,
                'actor': Actor.format(actor),
                }), 200
        except:
            abort(404)


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