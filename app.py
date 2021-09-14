from pymongo import MongoClient
import jwt
import datetime
import hashlib
import math
from flask import Flask, render_template, jsonify, request, redirect, url_for
from werkzeug.utils import secure_filename
from datetime import datetime, timedelta


app = Flask(__name__)
app.config["TEMPLATES_AUTO_RELOAD"] = True
app.config['UPLOAD_FOLDER'] = "./static/profile_pics"

SECRET_KEY = 'SPARTA'

client = MongoClient('localhost', 27017)
db = client.todayKcal
# client = MongoClient('13.209.47.121', 27017, username="test", password="test")
# db = client.dbsparta_1stminiproject


@app.route('/')
def home():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_info = db.users.find_one({"username": payload["id"]})
        return render_template('index.html', user_info=user_info)
    except jwt.ExpiredSignatureError:
        return redirect(url_for("login", msg="로그인 시간이 만료되었습니다."))
    except jwt.exceptions.DecodeError:
        return redirect(url_for("login", msg="로그인 정보가 존재하지 않습니다."))



# [로그인 API]
@app.route('/sign_in', methods=['POST'])
def sign_in():
    # 로그인
    username_receive = request.form['username_give']
    password_receive = request.form['password_give']

    pw_hash = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()
    result = db.users.find_one({'username': username_receive, 'password': pw_hash})

    if result is not None:
        payload = {
         'id': username_receive,
         'exp': datetime.utcnow() + timedelta(seconds=60 * 60 * 24)  # 로그인 24시간 유지
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        return jsonify({'result': 'success', 'token': token})
    # 찾지 못하면
    else:
        return jsonify({'result': 'fail', 'msg': '아이디/비밀번호가 일치하지 않습니다.'})




## API 역할을 하는 부분
@app.route('/main', methods=['POST'])
def write_review():
    foodName_receive = request.form['foodName_give']
    foodDate_receive = request.form['foodDate_give']
    foodKcal_receive = request.form['foodKcal_give']

    doc = {
        'food_name':foodName_receive,
        'food_date':foodDate_receive,
        'food_kcal':foodKcal_receive
    }

    db.foodInfo.insert_one(doc)

    return jsonify({'msg': '저장 완료!'})


# 로그인 페이지
@app.route('/login')
def login():
    msg = request.args.get("msg")
    return render_template('login.html', msg=msg)

#메인페이지
@app.route('/index')
def main():
    return render_template("index.html")

# 오늘의프로필 페이지
@app.route('/profile')
def profile():
    return render_template("profile.html")





#오늘의프로필등록
@app.route('/api/profile', methods=['POST'])
def save_profile():
    myid_receive = request.form['myid_give']
    height_receive = request.form['heigt_give']
    weight_receive = request.form['weight_give']
    goal_cal_receive =request.form['goal_cal_give']
    h =int(height_receive)
    w =int(weight_receive)
    bmiscore = math.trunc(w/(h*h)*10000)
    bmi=""
    if(bmiscore>30):
        bmi="비만"
    elif(bmiscore>=25):
        bmi="과체중"
    elif(bmiscore>=19):
        bmi="정상"
    else:
        bmi="저체중"

    print(bmi)
    doc ={
        'myid':myid_receive,
        'height':height_receive,
        'weight':weight_receive,
        'goal_cal':goal_cal_receive,
        'bmi': bmi,
        'bmiscore':bmiscore
    }
    db.todayKcal.insert_one(doc)

    return jsonify({'msg': '등록 완료!'})

#오늘의 프로필 리스팅
@app.route('/api/profile', methods=['GET'])
def show_profile():
    myid_receive=request.args.get("myid")
    print(myid_receive)
    profiles = list(db.todayKcal.find({"myid":myid_receive},{'_id':False}))
    print(profiles)
    return jsonify({'profiles': profiles})

#오늘의 프로필 수정
@app.route('/api/profile', methods=['POST'])
def update_profile():
    myid_receive=request.args.get("myid")
    height_receive = request.form['heigt_give']
    weight_receive = request.form['weight_give']
    goal_cal_receive = request.form['goal_cal_give']
    h = int(height_receive)
    w = int(weight_receive)
    bmiscore = math.trunc(w / (h * h) * 10000)
    bmi = ""
    if (bmiscore > 30):
        bmi = "비만"
    elif (bmiscore >= 25):
        bmi = "과체중"
    elif (bmiscore >= 19):
        bmi = "정상"
    else:
        bmi = "저체중"

    print(myid_receive)
    db.users.update_one({'myid': myid_receive}, {'$set': {'height': height_receive}})
    db.users.update_one({'myid': myid_receive}, {'$set': {'weight': weight_receive}})
    db.users.update_one({'myid': myid_receive}, {'$set': {'goal_cal': goal_cal_receive}})
    db.users.update_one({'myid': myid_receive}, {'$set': {'bmi': bmi}})
    db.users.update_one({'myid': myid_receive}, {'$set': {'bmiscore': bmiscore}})

    return jsonify({'result': 'success'})




if __name__ == '__main__':

    app.run(debug=True)

    app.run('0.0.0.0', port=5000, debug=True)


