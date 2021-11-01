# start

from flask import Flask, request
from fb_function import *

app = Flask(__name__)


@app.route('/', methods=['GET'])
def verify():
    """
    This function is for verify the webhook is working. It will send a get request form the
    FACEBOOK, and we need return 200 and 'hub.challenge' filed.
    :return:
    """
    if request.args.get("hub.mode") == "subscribe" and request.args.get("hub.challenge"):
        if not request.args.get("hub.verify_token") == '0309':
            return "Verification token mismatch", 403
        return request.args["hub.challenge"], 200
    return


@app.route('/', methods=['POST'])
def webhook():
    """
    For dealing with the POST request.
    :return:
    """
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:

                if messaging_event.get("message"):
                    try:
                        # into the reply function
                        reply(messaging_event)
                    except:
                        record_wrong(messaging_event["sender"]["id"], messaging_event)
                        send_message(messaging_event["sender"]["id"], '发生错误，请核对')

                if messaging_event.get("delivery"):  # delivery confirmation
                    pass

                if messaging_event.get("optin"):  # optin confirmation
                    pass

                if messaging_event.get("postback"):  # user clicked/tapped "postback" button in earlier message
                    pass

    return "ok", 200


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
