import json
import urllib
import requests
from decouple import config
from dbhelper3 import DBHelper

db = DBHelper()

TOKEN = config('TOKEN')
URL = "https://api.telegram.org/bot{}/".format(TOKEN)


def get_url(url):
    response = requests.get(url)
    content = response.content.decode("utf8")
    return content


def get_json_from_url(url):
    content = get_url(url)
    js = json.loads(content)
    return js


# timeout para fazer requisições ao servidor do Telegram em x segundos
def get_updates(offset=None):
    url = URL + "getUpdates?timeout=15"
    if offset:
        url += "&offset={}".format(offset)
    js = get_json_from_url(url)
    return js


def get_last_chat_id_and_text(updates):
    num_updates = len(updates["result"])
    last_update = num_updates - 1
    text = updates["result"][last_update]["message"]["text"]
    chat_id = updates["result"][last_update]["message"]["chat"]["id"]
    return text, chat_id


def get_last_update_id(updates):
    update_ids = []
    for update in updates["result"]:
        update_ids.append(int(update["update_id"]))
    return max(update_ids)


# urlib usado porque os caracteres especiais não eram retornados
def send_message(text, chat_id, reply_markup=None):
    text = urllib.parse.quote_plus(text)
    url = URL + "sendMessage?text={}&chat_id={}&parse_mode=Markdown".format(text, chat_id)
    if reply_markup:
        url += "&reply_markup={}".format(reply_markup)
    get_url(url)


def handle_updates(updates):
    for update in updates["result"]:
        name = update["message"]["chat"]["first_name"]
        text = update["message"]["text"]
        chat = update["message"]["chat"]["id"]
        items = db.get_items(chat)
        print(items)
        if text == "/lista":
            keyboard = build_keyboard(items)
            send_message("Selecione um item para apagar", chat, keyboard)
        elif text == "/start":
            send_message(
                "{},\nBem vindo à sua lista pessoal. Digite um item para adicionar à lista.\n"
                "Digite /lista para ver os itens e se quiser apagá-lo da lista, clique sobre o item.".format(name),
                chat)
        elif text.startswith("/"):
            continue
        elif text in items:
            db.delete_item(chat, text)
            items = db.get_items(chat)
            keyboard = build_keyboard(items)
            send_message("Selecione um item para apagá-lo.", chat, keyboard)
        else:
            db.add_item(name, chat, text)
            items = db.get_items(chat)
            message = "\n".join(items)
            send_message(message, chat)


def build_keyboard(items):
    keyboard = [[item] for item in items]
    reply_markup = {"keyboard": keyboard, "one_time_keyboard": True}
    return json.dumps(reply_markup)


def main():
    db.setup()
    last_update_id = None
    while True:
        print("Atualizando mensagens...")
        updates = get_updates(last_update_id)
        print(updates)
        if len(updates["result"]) > 0:
            last_update_id = get_last_update_id(updates) + 1
            handle_updates(updates)


if __name__ == '__main__':
    main()
