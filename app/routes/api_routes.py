# region imports
from flask import request, jsonify
from flask_restful import Resource, Api, abort, reqparse
from blog import app, db, csrf
from app.models import BME, MPU, User, NEO
from datetime import datetime
# endregion

api = Api(app, decorators=[csrf.exempt])


# --- BME ---


# region parser
bmeParser = reqparse.RequestParser()
bmeParser.add_argument('time', required=True)
bmeParser.add_argument('temperature', required=True)
bmeParser.add_argument('humidity', required=True)
bmeParser.add_argument('pressure', required=True)
#endregion

@api.resource('/api/raspi/bme')
class BME_all(Resource):

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
            return {'id': BME.query.order_by(-BME.id).first().id, 'time': args['time'], 'temperature': args['temperature'], 'humidity': args['humidity'], 'pressure': args['pressure']}
        return {'error': 'the given login credentials were incorrect'}

def abortBmeIf404(id):
    measurement = BME.query.get_or_404(id)
    if measurement is None:
        abort(404, message="BME {} doesn't exist!".format(id))

@api.resource('/api/raspi/bme/<int:id>')
class BME_single(Resource):

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


# --- MPU ---


# region parser
mpuParser = reqparse.RequestParser()
mpuParser.add_argument('time', type=str, required=True)
mpuParser.add_argument('gyroscope_x', type=float, required=True)
mpuParser.add_argument('gyroscope_y', type=float, required=True)
mpuParser.add_argument('gyroscope_z', type=float, required=True)
mpuParser.add_argument('acceleration_x', type=float, required=True)
mpuParser.add_argument('acceleration_y', type=float, required=True)
mpuParser.add_argument('acceleration_z', type=float, required=True)
mpuParser.add_argument('rot_x', type=float, required=True)
mpuParser.add_argument('rot_y', type=float, required=True)
# endregion

@api.resource('/api/raspi/mpu')
class MPU_all(Resource):

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
                return {'id': MPU.query.order_by(-MPU.id).first().id, 'time': args['time'], 'gyroscope_x': args['gyroscope_x'], 'gyroscope_y': args['gyroscope_y'], 'gyroscope_z': args['gyroscope_z'], 'acceleration_x': args['acceleration_x'], 'acceleration_y': args['acceleration_y'], 'acceleration_z': args['acceleration_z'], 'rot_x': args['rot_x'], 'rot_y': args['rot_y']}
            return errJson
        except:
            return errJson

def abortMpuIf404(id):
    measurement = MPU.query.get_or_404(id)
    if measurement is None:
        abort(404, message="MPU {} doesn't exist!".format(id))

@api.resource('/api/raspi/mpu/<int:id>')
class MPU_single(Resource):

    def get(self, id):
        abortMpuIf404(id)
        post = MPU.query.get_or_404(id)
        return jsonify({
        'id': id,
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


# --- NEO-6M ---

# region parser
neoParser = reqparse.RequestParser()
neoParser.add_argument('time', type=str, required=True)
neoParser.add_argument('data', type=str, required=True)
# endregion

@api.resource('/api/raspi/neo')
class NEO_all(Resource):

    def get(self):
        posts = NEO.query.all()
        res = {}
        for post in posts:
            res[post.id] = {
                'time': datetime.strftime(post.time, '%Y-%m-%d %H:%M:%S'),
                'data': post.data
            }
        return res

    def put(self):
        auth = request.authorization
        args = neoParser.parse_args(strict=True)
        errJson = {'error': 'the given login credentials were incorrect'}
        user = User.query.filter(User.username == auth.username).first()
        print(args)
        try:
            if user is not None and user.check_password(auth.password):
                addTime = datetime.strptime(request.args['time'], '%Y-%m-%d %H:%M:%S')
                db.session.add(
                    NEO(time=addTime,
                        data=args['data']
                    )
                )
                db.session.commit()
                return {
                    'id': NEO.query.order_by(-NEO.id).first().id,
                    'time': args['time'],
                    'data': args['data']
                }
            return {'msg': "auth failed"}
        except Exception as e:
            return {'msg': str(e)}


def abortNeoIf404(id):
    measurement = NEO.query.get_or_404(id)
    if measurement is None:
        abort(404, message="NEO {} doesn't exist!".format(id))


@api.resource('/api/raspi/neo/<int:id>')
class NEO_single(Resource):
    def get(self, id):
        abortNeoIf404(id)
        post = NEO.query.get_or_404(id)
        return jsonify({
            'id': id,
            'time': post.time,
            'data': post.data
        })
