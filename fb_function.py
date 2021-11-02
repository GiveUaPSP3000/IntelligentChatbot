# reply function

import json
import requests
from model_computing import *
from numpy import *
from google_function import *
from aip import AipSpeech
from value_process import *
from mongoDB import *
import pytz
from datetime import datetime, timedelta
import dateutil.relativedelta
import pandas as pd
from pandas.plotting import  table
import matplotlib.pyplot as plt
import matplotlib
from requests_toolbelt import MultipartEncoder
import calendar
from bson.objectid import ObjectId
import os

matplotlib.rc("font", family='YouYuan')
tzinfo = pytz.timezone('Asia/Shanghai')

# Facebook Token
fb_token = ""

# link to Baidu api
""" APPID AK SK """
APP_ID = ''
API_KEY = ''
SECRET_KEY = ''
client = AipSpeech(APP_ID, API_KEY, SECRET_KEY)

# link to mongoDB
mongo_link = MongoDB('FBCHATBOT', 'bill_log').get_link()


def record_wrong(client_id, text):
    """
    record wrong text
    :param client_id:
    :param text:
    :return:
    """
    with open("wrong_record/log.csv", 'a+', encoding='gbk', newline='') as f:
        csv_write = csv.writer(f)
        csv_write.writerow([client_id, text])
    return


def mongo_insert(now_time, client_id, in_type, text, value, in_time):
    """
    insert value
    :param now_time: now time
    :param client_id: client id
    :param in_type: insert type
    :param text: original text
    :param value: insert value
    :param in_time: input time
    :return:
    """
    if in_type:
        in_type = -1
    else:
        in_type = 1
    mongo_link.insert_one({
        "client_id": client_id,
        "year": in_time[0],
        "month": in_time[1],
        "day": in_time[2],
        "description": text,
        "type": in_type,
        "value": value,
        "add_time": now_time
    })
    return


def time_get(now_time, text):
    """
    get the description time and the accuracy of time
    :param now_time:
    :param text:
    :return:
    """
    text = text.replace('十一', '11')
    text = text.replace('十二', "12")
    text = text.replace('十', '10')
    text = pre_pro(text)
    # accuracy of time, 1 means year, 2 means month, 3 means day
    state = 1
    real_y = 0
    real_m = 0
    real_d = 0
    de_y = 1
    de_m = 1
    de_d = 1
    year_cv = {
        '今年': 0,
        "去年": -1,
        "前年": -2,
    }
    month_cv = {
        '这个月': 0,
        '本月': 0,
        '上个月': -1,
        '上上个月': -2
    }
    day_cv = {
        '今天': 0,
        '昨天': -1,
        '前天': -2,
    }
    # check the day
    for i in day_cv:
        if i in text:
            de_d = day_cv[i]
            now_time = now_time + dateutil.relativedelta.relativedelta(days=de_d)
            real_d = now_time.day
            state = 3
            break
    if de_d == 1:
        ste = re.findall('\d+[日号]', text)
        if len(ste):
            real_d = int(ste[0].strip('日').strip('号'))
            state = 3
        else:
            ste = re.findall('月\d+', text)
            if len(ste):
                real_d = int(ste[0].strip('月'))
                state = 3
            else:
                real_d = now_time.day

    # check the month
    for i in month_cv:
        if i in text:
            de_m = month_cv[i]
            now_time = now_time + dateutil.relativedelta.relativedelta(months=de_m)
            real_m = now_time.month
            state = 2
            break
    if de_m == 1:
        ste = re.findall('\d+月', text)
        if len(ste):
            real_m = int(ste[0].strip('月'))
            state = 2
        else:
            real_m = now_time.month

    # check the year
    for i in year_cv:
        if i in text:
            de_y = year_cv[i]
            real_y = (now_time + dateutil.relativedelta.relativedelta(years=de_y)).year
            break
    if de_y == 1:
        ste = re.findall('\d+年', text)
        if len(ste):
            real_y = int(ste[0].strip('年'))
        else:
            real_y = now_time.year

    return state, real_y, real_m, real_d


def get_month_show(client_id, year, month):
    """
    get the month bill
    :param client_id:
    :param year:
    :param month:
    :return:
    """
    month_dict = {'day': 1,
                 'type': 1,
                 'value': 1}
    # get the original data
    df = pd.DataFrame(mongo_link.find({'client_id': client_id, 'year': year, 'month': month}, month_dict))
    if not len(df):
        return []
    # get the maximum day of this month
    _, max_day = calendar.monthrange(year, month)
    show_df = []
    # income
    all_in = 0
    # spend
    all_out = 0
    # all sum
    all_sum = 0
    for i in range(1, max_day + 1):
        m_in = df[(df['type'] == 1) & (df['day'] == i)]['value'].sum()
        all_in += m_in
        m_out = df[(df['type'] == -1) & (df['day'] == i)]['value'].sum()
        all_out += m_out
        in_s_out = m_in - m_out
        all_sum += in_s_out
        show_df.append({
            '日': i,
            '收入': round(m_in, 2) if m_in != 0.0 else '',
            '支出': round(m_out, 2) if m_out != 0.0 else '',
            '总计': round(in_s_out, 2) if in_s_out != 0.0 else ''
        })
    show_df.append({
        '日': '汇总',
        '收入': round(all_in, 2),
        '支出': round(all_out, 2),
        '总计': round(all_sum, 2)
    })
    show_df = pd.DataFrame(show_df)
    return show_df


def get_year_show(client_id, year):
    """
    get the yearly bill
    :param client_id:
    :param year:
    :return:
    """
    year_dict = {'month': 1,
                 'type': 1,
                 'value': 1}
    df = pd.DataFrame(mongo_link.find({'client_id': client_id, 'year': year}, year_dict))
    if not len(df):
        return []
    show_df = []
    all_in = 0
    all_out = 0
    all_sum = 0
    for i in range(1, 13):
        m_in = df[(df['type'] == 1) & (df['month'] == i)]['value'].sum()
        all_in += m_in
        m_out = df[(df['type'] == -1) & (df['month'] == i)]['value'].sum()
        all_out += m_out
        in_s_out = m_in - m_out
        all_sum += in_s_out
        show_df.append({
            '月份': i,
            '收入': round(m_in, 2) if m_in != 0.0 else '',
            '支出': round(m_out, 2) if m_out != 0.0 else '',
            '总计': round(in_s_out, 2) if in_s_out != 0.0 else ''
        })
    show_df.append({
        '月份': '汇总',
        '收入': round(all_in, 2),
        '支出': round(all_out, 2),
        '总计': round(all_sum, 2)
    })
    show_df = pd.DataFrame(show_df)
    return show_df


def get_day_show(client_id, year, month, day):
    """
    get the month bill
    :param day:
    :param client_id:
    :param year:
    :param month:
    :return:
    """
    day_dict = {'description': 1,
                  'type': 1,
                  'value': 1}
    # get the original data
    df = pd.DataFrame(mongo_link.find({'client_id': client_id, 'year': year, 'month': month, 'day': day}, day_dict))
    # no data
    if not len(df):
        return []
    income = df[df['type'] == 1]['value'].sum()
    expend = df[df['type'] == -1]['value'].sum()
    df['value'] = df['type'] * df['value']
    df = df.drop(['type'], axis=1)
    df.rename(columns={'_id': 'ID', 'description': '描述', 'value': '金额'}, inplace = True)
    df = df.append({
        'ID': '汇总',
        '描述': f'总支出:{str(expend)}总收入:{str(income)}',
        '金额': income - expend
    }, ignore_index=True)
    return df


def create_image(df, client_id, title, o_size):
    """
    create a temporary image
    :param o_size:
    :param title:
    :param client_id:
    :param df:
    :return:
    """
    plt.cla()
    fig = plt.figure(figsize=(o_size[0], o_size[1]), dpi=1400)  # dpi表示清晰度
    ax = fig.add_subplot(111, frame_on=False)
    ax.xaxis.set_visible(False)  # hide the x axis
    ax.yaxis.set_visible(False)  # hide the y axis
    ax.set_title(title)

    table(ax, df, loc='center')  # 将df换成需要保存的dataframe即可
    plt.savefig(f'temple_images/{client_id}.png')


def text_deal(client_id, text):
    """
    deal with text
    :param client_id: client id
    :param text:
    :return:
    """
    # preprocess the original text
    testEntry = jieba_text(text, True)
    thisDoc = array(setOfWords2Vec(model[0], testEntry))

    # Decide whether to 1:charge or 0:query,
    record_bill = classifyNB(thisDoc, model[1], model[2], model[3])

    # get the time
    now_time = tzinfo.localize(datetime.now())

    # get the corrected time
    state, year, month, day = time_get(now_time, text)
    # charge
    if record_bill:
        thisDoc2 = array(setOfWords2Vec(model2[0], testEntry))
        is_out = classifyNB(thisDoc2, model2[1], model2[2], model2[3])

        # get the description of value, if fails return False
        values = value_find(text)

        # get correct value
        if values:
            # textual value convert to number value
            value = number_comp(values)
            # record in database
            mongo_insert(now_time, client_id, is_out, text, value, [year, month, day])
            # reply
            if is_out:
                re_type = '支出'
            else:
                re_type = '收入'
            send_message(client_id, f'已记录\n时间:{year}年{month}月{day}日\n类型:{re_type}${value}')
        else:
            # 未检测到答案
            record_wrong(client_id, text)
            send_message(client_id, '未成功识别，请重新输入')
            return
    # query
    else:
        # query for a hole year bill
        if state == 1:
            # get the dataframe
            df = get_year_show(client_id, year)
            title = f'{str(year)}年的账单'
            o_size = [3, 4]
        # query for a month
        elif state == 2:
            # get the dataframe
            df = get_month_show(client_id, year, month)
            title = f'{str(year)}年{month}月的账单'
            o_size = [6, 7]
        else:
            # get the dataframe
            df = get_day_show(client_id, year, month, day)
            title = f'{str(year)}年{month}月{day}日的账单'
            add_size = round(len(df) / 15)
            o_size = [3+add_size, 4+add_size]
        if len(df):
            # get the picture
            create_image(df, client_id, title, o_size)
            # send image
            send_image(client_id)
        else:
            send_message(client_id, '记录为空')
        return


def send_message(recipient_id, message_text):
    """
    send message to client
    :param recipient_id:
    :param message_text:
    :return:
    """
    params = {
        "access_token": fb_token
    }
    headers = {
        "Content-Type": "application/json"
    }
    data = json.dumps({
        "recipient": {
            "id": recipient_id
        },
        "message": {
            "text": message_text
        }
    })
    r = requests.post("https://graph.facebook.com/v12.0/me/messages", params=params, headers=headers, data=data)
    if r.status_code != 200:
        print('send failed')


def send_image(recipient_id):
    """
    send image to client
    :param recipient_id:
    :return:
    """
    params = {
        "access_token": fb_token
    }
    image_open = open(f'temple_images/{recipient_id}.png', 'rb')
    data = {
        # encode nested json to avoid errors during multipart encoding process
        'recipient': json.dumps({
            'id': recipient_id
        }),
        # encode nested json to avoid errors during multipart encoding process
        'message': json.dumps({
            'attachment': {
                'type': 'image',
                'payload': {}
            }
        }),
        'filedata': (os.path.basename(f'temple_images/{recipient_id}.png'), image_open, 'image/png')
    }
    # multipart encode the entire payload
    multipart_data = MultipartEncoder(data)

    # multipart header from multipart_data
    multipart_header = {
        'Content-Type': multipart_data.content_type
    }
    r = requests.post("https://graph.facebook.com/v12.0/me/messages", params=params, headers=multipart_header, data=multipart_data)
    image_open.close()
    if r.status_code != 200:
        print('send failed')
    return


def get_text(message):
    """
    for get the right text
    :param message:
    :return:
    """
    # belong to text
    if "text" in message:
        return message['text']
    # input belong to attachments
    elif "attachments" in message:
        content = message["attachments"][0]
        # not the audio
        if content['type'] not in ['audio', 'video']:
            return False
        # audio
        else:
            # get the audio link
            link_path = content['payload']['url']
            audio_data = decode_audio(link_path)

            # baidu speech recognition
            transcripts = client.asr(audio_data, 'pcm', 16000, {'dev_pid': 1537, })['result']

            # google speech recognition
            # transcripts = get_transcripts(audio_data)

            # return the recognition words
            return transcripts[0]
    # Disallowed type
    else:
        return ''


def delete_function(client_id, text):
    """
    super order, delete one item
    :param client_id:
    :param text:
    :return:
    """
    text = text.split('@')
    record = pd.DataFrame(mongo_link.find({'_id': ObjectId(text[1])}, {'year': 1, 'month': 1, 'day': 1, 'description': 1}))
    if not len(record):
        send_message(client_id, '未找到该记录，请核实')
    else:
        send_message(client_id, f'已删除{record["year"][0]}{record["month"][0]}{record["day"][0]}的该记录\n{record["description"][0]}')
        mongo_link.delete_one({'_id': ObjectId(text[1])})
    return


def reply(messaging_event):
    """
    Deal with request message
    :param messaging_event: request's content
    :return:
    """
    # the facebook ID of the person sending you the message
    sender_id = messaging_event["sender"]["id"]

    # get the text
    text = get_text(messaging_event["message"])

    # deal with text
    if text:
        if text.startswith('删除命令@'):
            delete_function(sender_id, text)
        else:
            text_deal(sender_id, text)
    # wrong return
    else:
        send_message(sender_id, '暂时只支持文字、语音、视频')
