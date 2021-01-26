
# Import all dependencies
import unittest, json, os
from app import create_app
from models import setup_db, Movie, Actor


class AppTestCase(unittest.TestCase):
    """This class represents the resource test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "agency"
        self.username = 'postgres'
        self.password = '123456'
        self.url = 'localhost:5432'
        self.database_path = "postgres://{}:{}@{}/{}".format(self.username, self.password, self.url, self.database_name)
        setup_db(self.app, self.database_path)

        self.new_movie = {
            'title': 'The new Movie',
            'release_date': '2015-02-22'
        }


        # Set up authentication tokens info
        with open('auth_config.json', 'r') as f:
            self.auth = json.loads(f.read())
            assistant_jwt = self.auth["roles"]["Casting Assistant"]["jwt_token"]
            director_jwt = self.auth["roles"]["Casting Director"]["jwt_token"]
            producer_jwt = self.auth["roles"]["Executive Producer"]["jwt_token"]
            self.auth_headers = {
                "Casting Assistant": f'Bearer {assistant_jwt}',
                "Casting Director": f'Bearer {director_jwt}',
                "Executive Producer": f'Bearer {producer_jwt}'
        }

    def tearDown(self):
        """Executed after each test"""
        pass

    def test_get_movies(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().get('/movies', headers=header_obj)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['movies'])
        
    def test_add_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        num_of_movies_before_adding = len(Movie.query.all())
        res = self.client().post('/movies',headers=header_obj, json={
           'title': 'The new Movie',
            'release_date': '2015-02-22'
        })
        num_of_movies_after_adding = len(Movie.query.all())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(num_of_movies_after_adding, num_of_movies_before_adding + 1)



    def test_faild_add_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        num_of_movies_before_adding = len(Movie.query.all())
        res = self.client().post('/movies',headers=header_obj, json={
           'title': 'The new Movie',
            'age': '2015-02-22'
        })
        num_of_movies_after_adding = len(Movie.query.all())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(num_of_movies_after_adding, num_of_movies_before_adding)

    def test_unauthoriszed_add_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        res = self.client().post('/movies',headers=header_obj, json={
            'title': 'The new Movie',
            'release_date': '2015-02-22'
        })
        self.assertEqual(res.status_code, 401)

    def test_get_non_existed_movies(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().get('/movies/1000',headers=header_obj)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')

    def test_delete_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        movie = Movie.query.order_by(Movie.id.desc()).first()
        res = self.client().delete('/movies/' + str(movie.id),headers=header_obj)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], movie.id)

    def test_failed_delete_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        
        res = self.client().delete('/movies/50000',headers=header_obj)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)

    def test_unauth_delete_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        movie = Movie.query.order_by(Movie.id.desc()).first()
        res = self.client().delete('/movies/' + str(movie.id),headers=header_obj)
        self.assertEqual(res.status_code, 401)

    def test_update_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        movie = Movie.query.order_by(Movie.id.desc()).first()
        res = self.client().patch('/movies/' + str(movie.id),headers=header_obj, json={
            'title': 'The updated Movie',
            'release_date': '2020-02-22'
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_failed_update_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        movie = Movie.query.order_by(Movie.id.desc()).first()
        res = self.client().patch('/movies/5000',headers=header_obj, json={
            'age': 'The updated Movie',
            'date': '2020-02-22'
        })
        self.assertEqual(res.status_code, 404)

    def test_unauth_update_movie(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        movie = Movie.query.order_by(Movie.id.desc()).first()
        res = self.client().patch('/movies/' + str(movie.id),headers=header_obj, json={
            'title': 'The updated Movie',
            'release_date': '2020-02-22'
        })
        self.assertEqual(res.status_code, 401)
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++#

    def test_get_actors(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().get('/actors', headers=header_obj)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['actors'])
        
    def test_add_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        num_of_actors_before_adding = len(Actor.query.all())
        res = self.client().post('/actors',headers=header_obj, json={
            "name" : "The new Actor",
            "gender" : "MALE",
            "age": 29
        })
        num_of_actorss_after_adding = len(Actor.query.all())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 201)
        self.assertEqual(data['success'], True)
        self.assertEqual(num_of_actors_before_adding +1 , num_of_actorss_after_adding )



    def test_faild_add_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        num_of_actors_before_adding = len(Actor.query.all())
        res = self.client().post('/actors',headers=header_obj, json={
            "who" : "The new Actor",
            "gen" : "MALE",
            "date": "29"
            })
        num_of_actors_after_adding = len(Actor.query.all())
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(num_of_actors_after_adding, num_of_actors_before_adding)

    def test_unauthoriszed_add_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().post('/actors',headers=header_obj, json={
            'name': 'The new Actor',
            'age': 35
        })
        self.assertEqual(res.status_code, 401)

    def test_get_non_existed_actors(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        res = self.client().get('/actors/5000',headers=header_obj)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertTrue(data['message'], 'resource not found')

    def test_delete_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        actor = Actor.query.order_by(Actor.id.desc()).first()
        res = self.client().delete('/actors/' + str(actor.id),headers=header_obj)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], actor.id)

    def test_failed_delete_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Executive Producer"]
        }
        
        res = self.client().delete('/actors/50000',headers=header_obj)
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 422)

    def test_unauth_delete_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        actor = Actor.query.order_by(Actor.id.desc()).first()
        res = self.client().delete('/actors/' + str(actor.id),headers=header_obj)
        self.assertEqual(res.status_code, 401)

    def test_update_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        actor = Actor.query.order_by(Actor.id.desc()).first()
        res = self.client().patch('/actors/' + str(actor.id),headers=header_obj, json={
            'name': 'The new Actor',
            'age': 35
        })
        data = json.loads(res.data)
        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)

    def test_failed_update_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Director"]
        }
        res = self.client().patch('/actors/5000',headers=header_obj, json={
            'name': 'The new Actor',
            'age': 35
        })
        self.assertEqual(res.status_code, 404)

    def test_unauth_update_actor(self):
        header_obj = {
            "Authorization": self.auth_headers["Casting Assistant"]
        }
        actor = Actor.query.order_by(Actor.id.desc()).first()
        res = self.client().patch('/actors/' + str(actor.id),headers=header_obj, json={
            'name': 'The new Actor',
            'age': 35
        })
        self.assertEqual(res.status_code, 401)

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()
