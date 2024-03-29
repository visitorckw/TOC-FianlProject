import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage, ImageSendMessage

from fsm import TocMachine
from utils import send_text_message
# from draw import draw

state = {}

load_dotenv()

machine = TocMachine(
    states=["new game", "playing", "win", "lose", "quit"],
    transitions=[
        {
            "trigger": "new game",
            "source": "new game",
            "dest": "new game",
        },
        {
            "trigger": "new game",
            "source": "playing",
            "dest": "new game",
        },
        {
            "trigger": "new game",
            "source": "win",
            "dest": "new game",
        },
        {
            "trigger": "new game",
            "source": "lose",
            "dest": "new game",
        },
        {
            "trigger": "new game",
            "source": "quit",
            "dest": "new game",
        },
        {
            "trigger": "move",
            "source": "new game",
            "dest": "playing",
        },
        {
            "trigger": "move",
            "source": "playing",
            "dest": "playing",
        },
        {
            "trigger": "move",
            "source": "playing",
            "dest": "win",
        },
        {
            "trigger": "move",
            "source": "playing",
            "dest": "lose",
        },
        {
            "trigger": "quit",
            "source": "new game",
            "dest": "quit",
        },
        {
            "trigger": "quit",
            "source": "playing",
            "dest": "quit",
        },
        {
            "trigger": "quit",
            "source": "win",
            "dest": "quit",
        },
        {
            "trigger": "quit",
            "source": "lose",
            "dest": "quit",
        },
    ],
    initial="quit",
    auto_transitions=False,
    show_conditions=True,
)


app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        message = event.message.text
        userID = str(event.source.user_id)
        f = open('input.txt', 'w')
        if message == 'quit' or message == 'q':
            message = 'Thanks for playing!'
            state[userID] = 'quit'
            line_bot_api.reply_message(
                event.reply_token, TextSendMessage(text=message)
            )
            continue 
        if len(message) == 2:
            state[userID] = 'playing'
        if message != 'new game':
            f.write(message + '\n')
        else:
            state[userID] = 'new game'
            open(userID + '.txt', 'w').close()
        f.write('q\n')
        f.close()
        os.system('python gobang.py ' + userID + '.txt < input.txt > output.txt')
        f = open('output.txt', 'r')
        result = f.readlines()
        f.close()
        message = ''
        data = ''
        for i in range(len(result)):
            s = result[i]
            if len(s) >= 4 and s[:4] == 'DUMP':
                filename = userID + '.txt'
                if not os.path.exists(filename):
                    open(filename, 'w').close()
                f = open(filename,'w')
                f.write(s[4:])
                data = s[4:]
                f.close()
                continue
            if len(s) >= 9 and s[:9] == 'Your move' and i <= len(result) - 10:
                message = ''
                continue
            if len(s) >= 8 and s[:8] == 'YOU LOSE':
                state[userID] = 'lose'
            if len(s) >= 7 and s[:7] == 'YOU WIN':
                state[userID] = 'win'
            message += s
        # pic = draw()
        # for i in range(0, len(data), 5):
        #     if data[i] == '1':
        #         pic.black.append(pic.trans(s[i+2], s[i+3]))
        #     else:
        #         pic.white.append(pic.trans(s[i+2], s[i+3]))
        # pic.draw(userID + '.png')
        # message = ImageSendMessage(
        #     original_content_url='https://tocfinalproject.herokuapp.com/getpic/' + userID,
        #     preview_image_url='https://tocfinalproject.herokuapp.com/getpic/' + userID
        # )
        # line_bot_api.reply_message(event.reply_token, message)
        line_bot_api.reply_message(
            event.reply_token, TextSendMessage(text=message)
        ) 
    print('state: ', state[userID])
    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)

    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")
        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")
@app.route("/getpic/<filename>")
def getpic(filename):
    return send_file(filename, mimetype='image/png')


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True) 
