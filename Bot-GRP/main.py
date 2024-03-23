import random
import time
import signal
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram import ChatAction
from telegram.error import Unauthorized
import re
import time
# Remplacez 'YOUR_TOKEN' par le token de votre bot Telegram
TOKEN = '7167044251:AAFYIiwwTr0GYpm0yNp2zhkTG5iuhK3g-t4'


# Définition de la fonction pour la commande /start
def start(update, context):
    # Récupérer les informations de l'utilisateur
    user_info = update.message.from_user
    first_name = user_info.first_name if user_info.first_name else ""
    last_name = user_info.last_name if user_info.last_name else ""
    name_surname = first_name + " " + last_name
    username = user_info.username if user_info.username else ""
    user_id = user_info.id
    lang = user_info.language_code

    # Définir l'emoji de langue en fonction du code de langue
    if lang == 'fr':
        lang_emoji = '🇨🇵'
    elif lang == 'en':
        lang_emoji = '🇬🇧'
    else:
        lang_emoji = '⬜'

    # Construire le message de bienvenue avec les informations de l'utilisateur
    message = ("Bienvenue! Je suis un bot Telegram conçu pour renvoyer des liens "
               "de groupe ou de canal en fonction de ce que vous envoyez. \n \n"
               "Envoyez-moi simplement un groupe ou un canal, et je vous répondrai "
               "avec le lien correspondant.\n \n"
               "Exemple : si tu m'envoies le lien d'un groupe, je t'enverrai le lien d'un groupe\n \n"
               "Ce bot vous permet d'échanger des canaux et des groupes.\n \n\n"
               "𝐕𝐎𝐒 𝐈𝐍𝐅𝐎𝐑𝐌𝐀𝐓𝐈𝐎𝐍 𝐃𝐄 𝐂𝐎𝐌𝐏𝐓𝐄 :\n"
               f"👦 𝙉𝙤𝙢/𝙋𝙧𝙚𝙣𝙤𝙢 : {name_surname}\n"
               f"🌐 𝙉𝙤𝙢 𝙙'𝙪𝙩𝙞𝙡𝙞𝙨𝙖𝙩𝙚𝙪𝙧 : {username}\n"
               f"🆔 𝙄𝘿 : {user_id}\n"
               f"{lang_emoji} 𝙇𝙖𝙣𝙜𝙪𝙚 : {lang}"
                "Lien de notre canal --> https://t.me/GroupSpamming_Canal")

    # Envoyer le message de bienvenue
    update.message.reply_text(message)
    time.sleep(2)
    update.message.reply_text("Pour commencer envoie moi le lien d'un groupe ou d'un canal !")
# Définition de la fonction pour répondre aux messages texte


# Définition de la fonction pour répondre aux messages texte
def save_links(update, context):
    try:
        links = extract_links(update.message.text)
        if links:
        # Ajouter les liens au fichier
            with open('links.txt', 'a') as file:
                for link in links:
                    file.write(link + '\n')
            message_text = "𝙍𝙚𝙘𝙝𝙚𝙧𝙘𝙝𝙚 𝙚𝙣 𝙘𝙤𝙪𝙧𝙨... \n\n Partage le Bot 3x pour avoir moin de temps a attendre a chaque fois en cliquant sur le bouton en bas ⬇️ "
            keyboard = [[InlineKeyboardButton("SHARE (0/3)", url="tg://msg?text=@GroupSpammingBot")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            update.message.reply_text(message_text, reply_markup=reply_markup)
            # Planifier l'envoi d'un lien au hasard après 1 heure
            context.job_queue.run_once(send_random_links, 30, context={'chat_id': update.message.chat_id})
            save_user_id(update.message.chat_id)
        else:
            update.message.reply_text('Seuls les liens Telegram commençant par "https://t.me/" sont autorisés et doivent avoir au moins 4 caractères après.')
    except Unauthorized:
    # Gérer l'erreur d'autorisation (utilisateur bloqué)
        user_id = update.effective_user.id
        update.message.reply_text(f"L'utilisateur avec l'ID {user_id} vous a bloqué. Le bot ne peut pas lui envoyer de messages.")
        
def extract_links(text):
    # Regex pour extraire les liens du texte
    pattern = r'https?://t\.me/\S{4,}'
    return re.findall(pattern, text)


def send_random_links(context):
    # Charger les liens depuis le fichier
    with open('links.txt', 'r') as file:
        stored_links = file.readlines()
    stored_links = [link.strip() for link in stored_links]

    # Vérifier si des liens sont disponibles
    if stored_links:
        # Sélectionner un nombre de liens au hasard jusqu'à un maximum de 3
        num_links_to_send = min(len(stored_links), 3)
        random_links = random.sample(stored_links, num_links_to_send)
        # Envoyer les liens à tous les utilisateurs enregistrés
        with open('user_id.txt', 'r') as file:
            user_ids = file.readlines()
        for user_id in user_ids:
            user_id = user_id.strip()
            for link in random_links:
                context.bot.send_message(chat_id=user_id, text=f"Voici un lien au hasard parmi ceux déjà stockés : {link}")
                context.bot.send_message(chat_id=user_id, text="N'hesite pas a envoyer un ou plusieurs autres.")
    else:
        # Si aucun lien n'est stocké, envoyer un message indiquant qu'aucun lien n'est disponible
        with open('user_id.txt', 'r') as file:
            user_ids = file.readlines()
        for user_id in user_ids:
            user_id = user_id.strip()
            context.bot.send_message(chat_id=user_id, text="Aucun lien n'est disponible pour le moment.")


def save_user_id(user_id):
    # Enregistrer l'ID de l'utilisateur dans le fichier
    with open('user_id.txt', 'a') as file:
        file.write(str(user_id) + '\n')


def main():
    # Initialisation de l'updater
    updater = Updater(TOKEN, use_context=True)

    # Récupération du dispatcher pour enregistrer les gestionnaires
    dp = updater.dispatcher

    # Enregistrement des gestionnaires de commandes
    dp.add_handler(CommandHandler("start", start))

    # Enregistrement du gestionnaire pour les messages texte
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, save_links))

    # Démarrage du bot
    updater.start_polling()

    # Garde le bot en marche jusqu'à ce que Ctrl+C soit pressé
    updater.idle()


if __name__ == '__main__':
    main()