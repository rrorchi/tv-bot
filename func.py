from replit import db
import requests, json, time, datetime, hmac
from urllib.parse import urlencode
import datetime

def log_in(username, **sett):
    for n in range(len(db['users'])):
        if username in db['users'][n]['username']:
            if sett['password'] not in db['users'][n]['password']:
                return(1024)
            print("Бобро ежа,", db['users'][n]['username'], "!")
            data = db.dumps(db['users'][n])
            return json.loads(data)
    return(1025)

def sign_up(username, password):
  flag = False
  for n in range(len(db['users'])):
    if username in db['users'][n]['username']:
      res = "Такой пользователь уже существует!"
      flag = True
      break
  if not flag:
    flag = True
    db['users'].append(db['users'][0])
    db['users'][len(db['users'])-1] = db['users'][0]
    db['users'][len(db['users'])-1]['username'] = username
    db['users'][len(db['users'])-1]['password'] = password
    db['users'][len(db['users'])-1]['user_id'] = str(len(db['users'])-1)
    res = "Пользователь создан!"
  for n in range(len(db['users'])):
    print(n , "-", db['users'][n]['user_id'], "-",db['users'][n]['username'])
  return res 

def save_settings(user, **new_sett):
  for opt, sett in new_sett.items():
    if sett:
      db['users'][user][opt] = sett
  print("Cохранено.")
  print(user,"-",db['users'][user]['username'])
  data = db.dumps(db['users'][user])
  return json.loads(data)

def update_data(user_id):
  data = db.dumps(db['users'][int(user_id)])
  return json.loads(data)

def delete_user(user_id):
  del db['users'][int(user_id)]
  for n in range(len(db['users'])):
    print(n , "-", db['users'][n]['user_id'], "-",db['users'][n]['username'])
  return



def tg_message(TOKEN, CHAT, res, message):
    req = "https://api.telegram.org/bot" + TOKEN + "/sendMessage?chat_id="+ CHAT + "&text=" + str(res) +"\r\n" + str(message)
    results = requests.get(req)
    print(message, results,  datetime.datetime.now())

def make_order(user, symbol, side, order_size, SECRET, KEY, close_p = False):
    header = {'X-MBX-APIKEY': KEY}
    params = {'symbol': symbol, 'side': side, 'type':'MARKET', 'quantity': order_size, 'reduceOnly': close_p, 'newOrderRespType': 'RESULT', 'timestamp': int(time.time() * 1000)}
    signature = hmac.new(SECRET.encode(), urlencode(params).encode(), 'sha256').hexdigest()
    params['signature'] = signature
    req_o = "https://fapi.binance.com/fapi/v1/order?"
    
    res = requests.post(req_o, params=params, headers=header)
    results = res.json()
    if not "code"in results:
      results_form = user + ": " + results["symbol"] + " " + results["side"] + " " + str(order_size)
    else:
      results_form = results
    print(user, ": ", results_form)

    return results_form

def parse_boolean(b):
	return b == "True"

def get_pos_percent(usern, prec, pos, current_price, leverage, *new_pos):
  to_close = pos
  for n in range(0, len(new_pos) - 1, 2):
    if new_pos[n+1] == False:
        continue
    to_close = (pos / 100 * new_pos[n])
    pos = pos - to_close

  order_size = round(to_close / current_price * leverage, prec)
  return order_size

def init_order(tv_reqq):
    flag = False
    tv_req = json.loads(tv_reqq)
    results = ""
    for n in range(len(db['users'])):
        if tv_req['username'] == db['users'][n]['username']:
              name = n
              if tv_req['action_type'] == "UPDATE":
                print("START: ", tv_req['symbol'], datetime.datetime.now())
                
                db['users'][n]['in_pos'] = tv_req['action_side']
                db['users'][n]['take_1'] = "False"
                db['users'][n]['take_2'] = "False"
                db['users'][n]['take_3'] = "False"
                db['users'][n]['take_4'] = "False"
                db['users'][n]['take_d'] = "0"
                print("STOP: ", tv_req['symbol'], datetime.datetime.now())
                break

              if tv_req['action_type'] == "GET_POSITION" and db['users'][n]['in_pos'] == "False":
                  order_size = get_pos_percent(n, int(db['users'][n]['min_dig']), float(db['users'][n]['qty_pos']), float(tv_req['current_price']), int(db['users'][n]['leverage']))
                  results = make_order(db['users'][n]['username'], db['users'][n]['symbol'], tv_req['action_side'], order_size, db['users'][n]['key2'], db['users'][n]['key1'], False)
                  if 'code' in results:
                      print("ошибка ", results['code'], ": ", results['msg'])
                  else:
                    print(results, " ", tv_req['message'])
                    db['users'][n]['in_pos'] = tv_req['action_side']
                    db['users'][n]['take_1'] = "False"
                    db['users'][n]['take_2'] = "False"
                    db['users'][n]['take_3'] = "False"
                    db['users'][n]['take_4'] = "False"
                    db['users'][n]['take_d'] = "0"
                    flag = True
                  break
              
              if tv_req['action_type'] == "GET_POSITION" and db['users'][n]['in_pos'] == "BUY" and tv_req['action_side'] == "SELL" and not flag:
                  order_size = get_pos_percent(n, int(db['users'][n]['min_dig']), float(db['users'][n]['qty_pos']), float(tv_req['current_price']), int(db['users'][n]['leverage']))
                  results = make_order(db['users'][n]['username'], db['users'][n]['symbol'], tv_req['action_side'], order_size + 100, db['users'][n]['key2'], db['users'][n]['key1'], True)
                  if 'code' in results:
                      print("ошибка ", results['code'], ": ", results['msg'])
                      results = make_order(db['users'][n]['username'], db['users'][n]['symbol'], tv_req['action_side'], order_size + 100, db['users'][n]['key2'], db['users'][n]['key1'], True)
                  results = make_order(db['users'][n]['username'], db['users'][n]['symbol'], tv_req['action_side'], order_size, db['users'][n]['key2'], db['users'][n]['key1'], False)
                  if 'code' in results:
                      print("ошибка ", results['code'], ": ", results['msg'])
                  else:
                    print(results, " ", tv_req['message'])
                    db['users'][n]['in_pos'] = tv_req['action_side']
                    db['users'][n]['take_1'] = "False"
                    db['users'][n]['take_2'] = "False"
                    db['users'][n]['take_3'] = "False"
                    db['users'][n]['take_4'] = "False"
                    db['users'][n]['take_d'] = "0"
                    flag = True
                  break

              if tv_req['action_type'] == "GET_POSITION" and db['users'][n]['in_pos'] == "SELL" and tv_req['action_side'] == "BUY" and not flag:
                  order_size = get_pos_percent(n, int(db['users'][n]['min_dig']), float(db['users'][n]['qty_pos']), float(tv_req['current_price']), int(db['users'][n]['leverage']))
                  results = make_order(db['users'][n]['username'], db['users'][n]['symbol'], tv_req['action_side'], order_size + 100, db['users'][n]['key2'], db['users'][n]['key1'], True)
                  if 'code' in results:
                      print("ошибка ", results['code'], ": ", results['msg'])
                      results = make_order(db['users'][n]['username'], db['users'][n]['symbol'], tv_req['action_side'], order_size + 100, db['users'][n]['key2'], db['users'][n]['key1'], True)
                  results = make_order(db['users'][n]['username'], db['users'][n]['symbol'], tv_req['action_side'], order_size, db['users'][n]['key2'], db['users'][n]['key1'], False)
                  if 'code' in results:
                      print("ошибка ", results['code'], ": ", results['msg'])
                  else:
                    print(results, " ", tv_req['message'])
                    db['users'][n]['in_pos'] = tv_req['action_side']
                    db['users'][n]['take_1'] = "False"
                    db['users'][n]['take_2'] = "False"
                    db['users'][n]['take_3'] = "False"
                    db['users'][n]['take_4'] = "False"
                    db['users'][n]['take_d'] = "0"
                  break

              if ((tv_req['action_type'] == "TAKE_1" and db['users'][n]['take_1'] == "False") or
                  (tv_req['action_type'] == "TAKE_2" and db['users'][n]['take_2'] == "False") or
                  (tv_req['action_type'] == "TAKE_3" and db['users'][n]['take_3'] == "False") or 
                  (tv_req['action_type'] == "TAKE_4" and db['users'][n]['take_4'] == "False")) and db['users'][n]['in_pos'] != "False":
                  
                  if db['users'][n]['in_pos'] == "BUY":
                    tv_req['action_side'] = "SELL"
                  else:
                    tv_req['action_side'] = "BUY"
                  

                  print(results, " ", tv_req['message'])
                  if tv_req['action_type'] == "TAKE_1":
                    db['users'][n]['take_1'] = "True"
                  elif tv_req['action_type'] == "TAKE_2":
                    db['users'][n]['take_2'] = "True"
                  elif tv_req['action_type'] == "TAKE_3":
                    db['users'][n]['take_3'] = "True"
                  elif tv_req['action_type'] == "TAKE_4":
                    db['users'][n]['take_4'] = "True"

                  order_size = get_pos_percent(n, 
                  int(db['users'][n]['min_dig']), 
                  float(db['users'][n]['qty_pos']), 
                  float(tv_req['current_price']), 
                  int(db['users'][n]['leverage']), 
                  float(db['users'][n]['qty1']), parse_boolean(db['users'][n]['take_1']), 
                  float(db['users'][n]['qty2']), parse_boolean(db['users'][n]['take_2']), 
                  float(db['users'][n]['qty3']), parse_boolean(db['users'][n]['take_3']), 
                  float(db['users'][n]['qty4']), parse_boolean(db['users'][n]['take_4']))

                  results = make_order(db['users'][n]['username'], db['users'][n]['symbol'], tv_req['action_side'], order_size, db['users'][n]['key2'], db['users'][n]['key1'], True)
                  if 'code' in results:
                    print("ошибка ", db['users'][n]['username']," ", results['code'], ": ", results['msg'])
                    
                    if tv_req['action_type'] == "TAKE_1":
                      db['users'][n]['take_1'] = "False"
                    elif tv_req['action_type'] == "TAKE_2":
                      db['users'][n]['take_2'] = "False"
                    elif tv_req['action_type'] == "TAKE_3":
                      db['users'][n]['take_3'] = "False"
                    elif tv_req['action_type'] == "TAKE_4":
                      db['users'][n]['take_4'] = "False"
                  break 
                  
              if tv_req['action_type'] == "TAKE_NEXT" and db['users'][n]['in_pos'] != "False":
                  if db['users'][n]['in_pos'] == "BUY":
                    tv_req['action_side'] = "SELL"
                  else:
                    tv_req['action_side'] = "BUY"
                    
                  order_size = get_pos_percent(n, 
                  int(db['users'][n]['min_dig']), 
                  float(db['users'][n]['qty_pos']), 
                  float(tv_req['current_price']), 
                  int(db['users'][n]['leverage']), 
                  float(db['users'][n]['qty1']), parse_boolean(db['users'][n]['take_1']), 
                  float(db['users'][n]['qty2']), parse_boolean(db['users'][n]['take_2']), 
                  float(db['users'][n]['qty3']), parse_boolean(db['users'][n]['take_3']), 
                  float(db['users'][n]['qty4']), parse_boolean(db['users'][n]['take_4']),
                  float(db['users'][n]['qtyD']))
                  results = make_order(db['users'][n]['username'], db['users'][n]['symbol'], tv_req['action_side'], order_size, db['users'][n]['key2'], db['users'][n]['key1'], True)
                  if 'code' in results:
                    print("ошибка ", db['users'][n]['username']," ", results['code'], ": ", results['msg'])
                  else:
                    print(results, " ", tv_req['message'])
                  break
                  
              if tv_req['action_type'] ==  "CLOSE_POSITION" and db['users'][n]['in_pos'] != "False":
                  if db['users'][n]['in_pos'] == "BUY":
                      tv_req['action_side'] = "SELL"
                  else:
                      tv_req['action_side'] = "BUY"
                  order_size = get_pos_percent(n, int(db['users'][n]['min_dig']), float(db['users'][n]['qty_pos']), float(tv_req['current_price']), int(db['users'][n]['leverage'])) + 100
                  results = make_order(db['users'][n]['username'], db['users'][n]['symbol'], tv_req['action_side'], order_size, db['users'][n]['key2'], db['users'][n]['key1'], True)
                  if 'code' in results:
                      print("ошибка ", db['users'][n]['username']," ", results['code'], ": ", results['msg'])
                  else:
                      print(results, " ", tv_req['message'])
                      db['users'][n]['in_pos'] = "False"
                      db['users'][n]['take_1'] = "False"
                      db['users'][n]['take_2'] = "False"
                      db['users'][n]['take_3'] = "False"
                      db['users'][n]['take_4'] = "False"
                      db['users'][n]['take_d'] = "0"
                  break
        else:
            results = ""
    if results != "":
      tg_message(db['users'][name]['tg_token'], db['users'][name]['chat_id'], results, tv_req['message'])

    return (str(results))