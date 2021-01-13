import telegram
from telegram.ext import CommandHandler,ConversationHandler, MessageHandler, Updater, Filters
import logging
from telegram import ReplyKeyboardMarkup, Update
import os

PORT = int(os.environ.get('PORT', 5000))
TOKEN=''
##Connecting to my bot
bot = telegram.Bot(token=TOKEN)
print(bot.get_me())

##For error handling 
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                     level=logging.INFO)
logger = logging.getLogger()

#Command functions for bot
def start(update, context):
    if players != {}:
        bot.send_message(update.message.chat.id, "GAME ALREADY IN PROGRESS \nPlease use /done to end your current game before using /start to start a new game.")
    else:
        global ID
        ID =  update.message.chat.id
        context.user_data['Players'] = players
        context.user_data['All Scores'] = all_scores
        bot.send_message(ID,"Welcome to your new mahjong game!🀄🀄🀄\nThis bot was created to help track points in a mahjong game as a substitute for mahjong chips.")
        update.message.reply_text(
            "What is Player 1's name?",
        )
        return PLAYER1

def help(update, context):
    bot.send_message(ID, "Type /start to start a game, /edit to edit player name, /fix to manually enter scores, /done to end a game")

def unknown(update, context):
    bot.send_message(chat_id=update.effective_chat.id, text="Sorry, I didn't understand that command.")

def done(update, context):
    update.message.reply_text(
        "Game Over! Final scores are: " + players_to_str(players)
        )
    context.user_data.clear()
    players.clear()
    all_scores.clear()
    return ConversationHandler.END

def edit(update, context):
    reply_keyboard = get_players(players)
    update.message.reply_text(
        "Whose would you like to edit?", 
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return EDITNAME

def fix(update, context):
    pp = ', '.join(map(str, list(players.keys())))
    update.message.reply_text(
        "Please input the scores for each player, separated by commas, in the order of:\n" + str(pp), 
    )
    return HARDCODE

PLAYER1, PLAYER2, PLAYER3, PLAYER4, CHOSEN, GANG, GANG_TYPE, GANG_SCORE, ROUND_END, ROUND_END_SCORE, ROUND_END_THROW,EDITNAME,NEWNAME,HARDCODE = range(14)
prev_scores = {}
players = {}
all_scores = []

#Non-command functions
def edit_name(update, context):
    global to_edit
    to_edit = update.message.text
    if to_edit not in players:
        bot.send_message(ID, "No player with name " + to_edit + " exists.")
    else:
        update.message.reply_text(
            "What is " + to_edit + "'s new name?", 
        )
        return NEWNAME

def new_name(update, context):
    players[to_edit] = update.message.text
    bot.send_message(ID, to_edit + "'s name has been changed to " + update.message.text)
    return choice(update, context)

def hard_code(update, context):
    slst = update.message.text.split(",")
    if len(slst) != 4:
        return fix(update, context)
    else:
        i = 0
        for key in list(players.keys()):
            players[key] = int(slst[i])
            i += 1
        bot.send_message(ID, players_to_str(players))
        return choice(update, context)
    
def get_player2(update, context):
    text = update.message.text
    players[text] = 0
    update.message.reply_text(
        "What is Player 2's name?"
    )
    return PLAYER2

def get_player3(update, context):
    text = update.message.text
    players[text] = 0
    update.message.reply_text(
        "What is Player 3's name?"
    )
    return PLAYER3
def get_player4(update, context):
    text = update.message.text
    players[text] = 0
    update.message.reply_text(
        "What is Player 4's name?"
    )
    return PLAYER4

def players_to_str_change(user_data):
    lst = []
    prev = all_scores[-1]
    for key, value in players.items():
        if key != "winner" and key != "gang":
            s = f'{key} has score: {value}'
            if value >= prev[key]:
                s+= " (+" + str(int(value)-int(prev[key])) +")"
            else:
                s+= " (" + str(int(value)-int(prev[key])) +")"
            lst.append(s)
    return "\n".join(lst).join(['\n', '\n'])

def players_to_str(user_data):
    lst = []
    for key, value in players.items():
        if key != "winner" and key != "gang":
            lst.append(f'{key} has score: {value}')
    return "\n".join(lst).join(['\n', '\n'])

def get_players(data):
    playerslst = []
    innerlst = []
    for key, value in data.items():
        innerlst.append(key)
        if len(innerlst) == 2:
            playerslst.append(innerlst)
            innerlst = []
    return playerslst

def start_game(update, context):
    text = update.message.text
    players[text] = 0
    update.message.reply_text(
        "Game start"+
        players_to_str(players)
        )
    return choice(update, context)

def choice(update, context):
    reply_keyboard = [['gang 杠', 'round end'],['undo previous action']]
    update.message.reply_text(
        "Choose an action or type /done to end game",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return CHOSEN

def process_choice(update, context):
    chosen = update.message.text
    if chosen.find("gang")>-1:
        reply_keyboard = get_players(players)
        update.message.reply_text(
            "Who gang 杠?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return GANG_TYPE
    elif chosen == "round end":
        reply_keyboard = get_players(players)
        update.message.reply_text(
            "Who won the round?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )    
        return ROUND_END
    elif chosen == "undo previous action":
        if len(all_scores) > 0:
            last_round = all_scores.pop()
            for key, value in players.items():
                if key in prev_scores:
                    players[key] = last_round[key]
            update.message.reply_text(
                "Last score change has been reversed. \n" + players_to_str(players),
            )
        else:
            update.message.reply_text(
                "No previous rounds found, scores remain unchanged. Use /fix to manually key in other score values.",
            )
        return choice(update, context)
    else:
        update.message.reply_text(
            "Failed to make valid choice, please try again",
        )
        return choice(update, context)
        

def gang_type(update, context):
    who = update.message.text
    context.user_data['gang'] = who
    reply_keyboard = [['zi mo 自摸', 'thrown by others']]
    update.message.reply_text(
        "Where did the gang tile come from?",
        reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
    )
    return GANG_SCORE

def gang_score(update, context):
    g_type = update.message.text
    score_increment = 0
    if g_type.find("zi mo")>-1:
        score_increment = 2
    elif g_type == "thrown by others":
        score_increment = 1
    else:
        update.message.reply_text(
            "Failed to make valid choice, please try again",
        )
        return choice(update, context)
    
    who_gang = context.user_data['gang']
    if 'gang' in context.user_data:
        del context.user_data['gang']
    
    for key, value in players.items():
        prev_scores[key] = players[key]
    all_scores.append(prev_scores.copy())
    for key, value in players.items():
        if key != who_gang:
            players[key] -= score_increment
            players[who_gang] += score_increment
    update.message.reply_text(
            "congrats " + who_gang + "! \n" + players_to_str_change(players),
        )
    return choice(update, context)

def round_end(update, context):
    winner = update.message.text
    user_data = context.user_data
    user_data['winner'] = winner
    score_increment = 0
    if winner not in players:
        update.message.reply_text(
            "Failed to make valid choice, please try again",
        )
        return choice(update, context)
    else:
        nested = get_players(players)
        inner = [val for sublist in nested for val in sublist]
        inner.remove(winner)
        inner.insert(0,"zi mo 自摸")
        rinner = []
        reply_keyboard = []
        for ele in inner:
            rinner.append(ele)
            if len(rinner) == 2:
                reply_keyboard.append(rinner)
                rinner = []
        update.message.reply_text(
            "Who threw the tile?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        ) 
        return ROUND_END_THROW

def round_end_throw(update, context):
    thrower = update.message.text
    user_data = context.user_data
    user_data['thrower'] = thrower
    score_increment = 0
    if thrower not in players and thrower.find("zi mo")==-1:
        update.message.reply_text(
            "Failed to make valid choice, please try again",
        )
        return choice(update, context)
    else:
        reply_keyboard = [range(1,6)]
        update.message.reply_text(
            "Points (台) scored?",
            reply_markup=ReplyKeyboardMarkup(reply_keyboard, one_time_keyboard=True),
        )
        return ROUND_END_SCORE
        
def round_end_score(update, context):    
    score_increment = int(update.message.text)
    user_data = context.user_data
    winner = context.user_data['winner']
    thrower = context.user_data['thrower']
    if score_increment > 5 or score_increment < 1:
        update.message.reply_text(
            "Invalid points (台) given, please re-try")
        return choice(update, context)
    else:
        score_increment -= 1
        if 'winner' in context.user_data:
            del context.user_data['winner']
        if 'thrower' in context.user_data:
            del context.user_data['thrower']
        if thrower.find("zi mo")>-1:
            score_increment += 1
        
        for key, value in players.items():
            prev_scores[key] = players[key]
        all_scores.append(prev_scores.copy())
        for key, value in players.items():
            if key != winner:
                if key == thrower:
                    players[key] -= 2**(score_increment+1)
                    players[winner] += 2**(score_increment+1)
                else:
                    players[key] -= 2**score_increment
                    players[winner] += 2**score_increment

        update.message.reply_text(
                "congrats " + winner + "! \n" + players_to_str_change(players),
            )
        return choice(update, context)


def main() -> None:
    updater = Updater(token=TOKEN,use_context=True)
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            PLAYER1: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), get_player2
                ),CommandHandler('done', done)
            ],
            PLAYER2: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), get_player3
                ),CommandHandler('done', done)
            ],
            PLAYER3: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), get_player4
                ),CommandHandler('done', done)
            ],
            PLAYER4: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), start_game
                ),CommandHandler('done', done)
            ],
            EDITNAME: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), edit_name
                ),CommandHandler('done', done)
            ],
            NEWNAME: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), new_name
                ),CommandHandler('done', done)
            ],
            HARDCODE: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), hard_code
                ),CommandHandler('done', done)
            ],
            CHOSEN: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), process_choice
                ),CommandHandler('done', done),CommandHandler('edit', edit),CommandHandler('fix', fix)
            ],
            GANG_TYPE: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), gang_type
                ),CommandHandler('done', done),CommandHandler('edit', edit),CommandHandler('fix', fix)
            ],
            GANG_SCORE: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), gang_score
                ),CommandHandler('done', done),CommandHandler('edit', edit),CommandHandler('fix', fix)
            ],
            ROUND_END: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), round_end
                ),CommandHandler('done', done),CommandHandler('edit', edit),CommandHandler('fix', fix)
            ],
            ROUND_END_THROW: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), round_end_throw
                ),CommandHandler('done', done),CommandHandler('edit', edit),CommandHandler('fix', fix)
            ],
            ROUND_END_SCORE: [
                MessageHandler(
                    Filters.text& ~(Filters.command | Filters.regex('^done$')), round_end_score
                ),CommandHandler('done', done),CommandHandler('edit', edit),CommandHandler('fix', fix)
            ],
        },
        fallbacks=[MessageHandler(Filters.regex('^done$'), done)],
    )
    dispatcher.add_handler(conv_handler)

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CommandHandler('done', done))
    dispatcher.add_handler(CommandHandler('help', help))
    dispatcher.add_handler(CommandHandler('edit', edit))
    dispatcher.add_handler(MessageHandler(Filters.command, unknown))
    
    # Start the Bot
##    updater.start_polling()
    updater.start_webhook(listen="0.0.0.0",
                      port=int(PORT),
                      url_path=TOKEN)
    updater.bot.setWebhook('' + TOKEN)
    updater.idle()


if __name__ == '__main__':
    main()
