import func, json
from flask import Flask, request, render_template, redirect, session, flash
from waitress import serve
import datetime, time, requests
import keep_alive

app = Flask(__name__)
app.secret_key = b'aw093ur9uwbtjhr9te8u9f0dgbd9gu83h'

@app.route('/', methods=['POST', 'GET'])
def index():
    if request.method == 'POST':
        session['username'] = request.form['login']
        session['password'] = request.form['password']
        if not session['username'] or not session['password']:
            flash("Введите логин и пароль!")
            return redirect('#')
        session['users_data'] = func.log_in(session['username'], password = session['password'])
        if session['users_data'] == 1024:
            print("Неправильный пароль!")
            flash("Неправильный пароль!")
            return redirect('#')
        if session['users_data'] == 1025:
            print("Юзер не найден")
            flash("Юзер не найден")
            return redirect('#')
        print(session['users_data']['username'])
        return redirect('user')

    return render_template('index.html')

@app.route('/sign', methods=['POST'])
def index_sign():
  session['new_login'] = request.form['new_login']
  session['new_password'] = request.form['new_password']
  res = func.sign_up(session['new_login'], password = session['new_password'])
  flash(res)
  return redirect('/')

@app.route('/user')
def user_page():
    if 'username' in session:
        session['users_data'] = func.update_data(session['users_data']['user_id'])
        print(session['username'])
        return render_template('user.html', users_data = session['users_data'])
    return redirect('/')

@app.route('/save_settings', methods=['POST'])
def save_settings():
    session['users_data'] = func.save_settings(int(session['users_data']['user_id']), symbol = request.form['symbol'], leverage = request.form['leverage'], min_dig = request.form['min_dig'], qty_pos = request.form['qty_pos'], qty1 = request.form['qty1'], qty2 = request.form['qty2'], qty3 = request.form['qty3'], qty4 = request.form['qty4'], qtyD = request.form['qtyD'], in_pos = request.form['in_pos'], take_1 = request.form['take_1'], take_2 = request.form['take_2'], take_3 = request.form['take_3'], take_4 = request.form['take_4'], take_d = request.form['take_d'], key1 = request.form['key'], key2 = request.form['sec'], tg_token = request.form['tg_token'], chat_id = request.form['chat_id'])
    return redirect('/user')

@app.route('/delete_user', methods=['POST'])
def delete_user():
    if 'username' in session:
      func.delete_user(session['users_data']['user_id'])
      flash("Пользователь " + str(session['username']) + " удалён!")
      print("Пользователь " + str(session['username']) + " удалён!")
      session.pop('username', None)
    return redirect('/')

@app.route('/log_out', methods=['POST'])
def logout():
    if 'username' in session:
        flash("Вы вышли!")
        session.pop('username', None)
        print("Вы вышли!")
    return redirect('/')

@app.route('/wh', methods = ['POST'])
def wh():
  tv_data = request.data
  tv_req = json.loads(tv_data)
  print("SIGNAL: ", tv_req['symbol'], datetime.datetime.now())
  result = func.init_order(tv_data)
  return result


func.initdb()

if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=8080)

keep_alive.keep_alive()
while True:
  for bot_url in keep_alive.bot_urls:
    requests.head(bot_url, allow_redirects=True)
    print('Ping: ' + bot_url + datetime.datetime.now())
  time.sleep(keep_alive.timeout*60)