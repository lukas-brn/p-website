# region imports
from flask import request, jsonify
from flask_restful import Resource, Api, abort, reqparse
from blog import app, db, csrf
from app.models import BME, MPU, User
from datetime import datetime
# endregion

api = Api(app, decorators=[csrf.exempt])


# --- BME ---


# region parser
bmeParser = reqparse.RequestParser()
bmeParser.add_argument('time')
bmeParser.add_argument('temperature')
bmeParser.add_argument('humidity')
bmeParser.add_argument('pressure')
#endregion

class BME_put(Resource):
	
	def get(self):
		posts = BME.query.all()
		res = {}
		for post in posts:
			res[post.id] = {
				'time': datetime.strftime(post.time, '%Y-%m-%d %H:%M:%S'),
				'temperature': post.temperature,
				'humidity': post.humidity,
				'pressure': post.pressure
			}
		return res

	def put(self):
		auth = request.authorization
		args = bmeParser.parse_args(strict=True)
		errJson = {'error': 'the given login credentials were incorrect'}
		try:
			user = User.query.filter(User.username == auth.username).first()
			if user is not None and user.check_password(auth.password):
				addTime = datetime.strptime(args['time'], '%Y-%m-%d %H:%M:%S')
				db.session.add(
					BME(
						time = addTime,
						temperature = args['temperature'],
						humidity = args['humidity'],
						pressure = args['pressure']
					)
				)
				db.session.commit()
				return {'time': args['time'], 'temperature': args['temperature'], 'humidity': args['humidity'], 'pressure': args['pressure']}
			return errJson
		except:
			return errJson

def abortBmeIf404(id):
	measurement = BME.query.get_or_404(id)
	if measurement is None:
		abort(404, message="BME {} doesn't exist!".format(id))

class BME_get(Resource):

	def get(self, id):
		abortBmeIf404(id)
		post = BME.query.get_or_404(id)
		return jsonify({
			'id': id,
			'time': post.time,
			'temperature': post.temperature,
			'humidity': post.humidity,
			'pressure': post.pressure
		})

api.add_resource(BME_put, '/api/raspi/bme')
api.add_resource(BME_get, '/api/raspi/bme/<int:id>')


# --- MPU ---


# region parser
mpuParser = reqparse.RequestParser()
mpuParser.add_argument('time')
mpuParser.add_argument('gyroscope_x')
mpuParser.add_argument('gyroscope_y')
mpuParser.add_argument('gyroscope_z')
mpuParser.add_argument('acceleration_x')
mpuParser.add_argument('acceleration_y')
mpuParser.add_argument('acceleration_z')
mpuParser.add_argument('rot_x')
mpuParser.add_argument('rot_y')
# endregion

class MPU_put(Resource):

	def get(self):
		posts = MPU.query.all()
		res = {}
		for post in posts:
			res[post.id] = {
				'time': datetime.strftime(post.time, '%Y-%m-%d %H:%M:%S'),
				'gyroscope_x': post.gyroscope_x,
				'gyroscope_y': post.gyroscope_y,
				'gyroscope_z': post.gyroscope_z,
				'acceleration_x': post.acceleration_x,
				'acceleration_y': post.acceleration_y,
				'acceleration_z': post.acceleration_z,
				'rot_x': post.rot_x,
				'rot_y': post.rot_y
			}
		return res

	def put(self):
		auth = request.authorization
		args = mpuParser.parse_args(strict=True)
		errJson = {'error': 'the given login credentials were incorrect'}
		try:
			user = User.query.filter(User.username == auth.username).first()
			if user is not None and user.check_password(auth.password):
				addTime = datetime.strptime(request.args['time'], '%Y-%m-%d %H:%M:%S')
				db.session.add(
					MPU(
						time = addTime,
						gyroscope_x = args['gyroscope_x'],
						gyroscope_y = args['gyroscope_y'],
						gyroscope_z = args['gyroscope_z'],

						acceleration_x = args['acceleration_x'],
						acceleration_y = args['acceleration_y'],
						acceleration_z = args['acceleration_z'],

						rot_x = args['rot_x'],
						rot_y = args['rot_y']
					)
				)
				db.session.commit()
				return {'time': args['time'], 'gyroscope_x': args['gyroscope_x'], 'gyroscope_y': args['gyroscope_y'], 'gyroscope_z': args['gyroscope_z'], 'acceleration_x': args['acceleration_x'], 'acceleration_y': args['acceleration_y'], 'acceleration_z': args['acceleration_z'], 'rot_x': args['rot_x'], 'rot_y': args['rot_y']}
			return errJson
		except:
			return errJson

def abortMpuIf404(id):
	measurement = MPU.query.get_or_404(id)
	if measurement is None:
		abort(404, message="MPU {} doesn't exist!".format(id))

class MPU_get(Resource):

	def get(self, id):
		abortMpuIf404(id)
		post = MPU.query.get_or_404(id)
		return jsonify({
			'time': post.time,
			'gyroscope_x': post.gyroscope_x,
			'gyroscope_y': post.gyroscope_y,
			'gyroscope_z': post.gyroscope_z,
			'acceleration_x': post.acceleration_x,
			'acceleration_y': post.acceleration_y,
			'acceleration_z': post.acceleration_z,
			'rot_x': post.rot_x,
			'rot_y': post.rot_y
		})

api.add_resource(MPU_put, '/api/raspi/mpu')
api.add_resource(MPU_get,  '/api/raspi/mpu/<int:id>')
