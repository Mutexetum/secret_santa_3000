from .models import User_s_santa, States
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from random import randint


def create_user(username, user_id):
    user, created = User_s_santa.objects.get_or_create(
                user_id=user_id, 
                defaults={"username": username}
                )
    return user, created


def get_buttons_for_user(user_id):
    user = User_s_santa.objects.filter(
                user_id=user_id
                ).first()
    if user is None:
        user, created = create_user(None, user_id)
    data_collected = True

    buttons = []
    if user.full_name is None or user.full_name == "":
        buttons.append({"title": "⭕️ Добавить ФИО", "callback_data": "add_full_name"})
        data_collected = False
    else:
        buttons.append({"title": "✅ Изменить ФИО", "callback_data": "edit_full_name"})

    if user.address is None or user.address == "":
        data_collected = False
        buttons.append({"title": "⭕️ Добавить адрес", "callback_data": "add_address"})
    else:
        buttons.append({"title": "✅ Изменить адрес", "callback_data": "edit_address"})

    if user.about_me is None or user.about_me == "":
        data_collected = False
        buttons.append({"title": "⭕️ Добавить 'О себе'", "callback_data": "add_about_me"})
    else:
        buttons.append({"title": "✅ Изменить 'О себе'", "callback_data": "edit_about_me"})

    if user.i_want is None or user.i_want == "":
        data_collected = False
        buttons.append({"title": "⭕️ Добавить 'Что я хочу'", "callback_data": "add_i_want"})
    else:
        buttons.append({"title": "✅ Изменить 'Что я хочу'", "callback_data": "edit_i_want"})
    
    if user.i_donnot_want is None or user.i_donnot_want == "":
        data_collected = False
        buttons.append({"title": "⭕️ Добавить 'Что я не хочу'", "callback_data": "add_i_donnot_want"})
    else:
        buttons.append({"title": "✅ Изменить 'Что я не хочу'", "callback_data": "edit_i_donnot_want"})

    if user.my_region == 2:
        data_collected = False
        buttons.append({"title": "️️⭕️ Добавить 'Где я нахожусь'", "callback_data": "add_my_region"})
    else:
        buttons.append({"title": "✅ Изменить 'Где я нахожусь'", "callback_data": "edit_my_region"})

    if user.ready_to_send_to == 2:
        data_collected = False
        buttons.append({"title": "⭕️ Добавить 'Куда готов отправить'", "callback_data": "add_ready_to_send_to"})
    else:
        buttons.append({"title": "✅ Изменить 'Куда готов отправить'", "callback_data": "edit_ready_to_send_to"})

    return buttons, data_collected


def are_data_collected(user_id):
    b, data_collected =  get_buttons_for_user(user_id)
    return data_collected


def application_closed():
    states = States.objects.all().first()
    if states is None:
        states = States.objects.create()

    return states.application_closed


def get_user_data(user_id):
    user = User_s_santa.objects.filter(
                user_id=user_id
                ).first()
    if user is None:
        user, created = create_user(None, user_id)

    data = "*ФИО:* {0}\n*Адресс:* {1}\n*Обо мне:* {2}\
            \n*Что я хочу:* {3}\n*Что я не хочу:* {4}\
            \n*Мой регион:* {5}\n*Куда я готов отправить:* {6}\
            ".format(
                user.full_name,
                user.address,
                user.about_me,
                user.i_want,
                user.i_donnot_want,
                user.my_region,
                user.ready_to_send_to)
    return data
    

def match_users():
    not_matched_santas = User_s_santa.objects.all().exclude(address__isnull=True).exclude(address="")

    matched_santas = []

    rest_target_count = not_matched_santas.count()
    first_santa = get_random_santa(not_matched_santas, rest_target_count)
    santa = first_santa
    rest_target_count -= 1
    not_matched_santas = not_matched_santas.exclude(id=santa.id)

    while rest_target_count > 0:
        target = None
        if santa.ready_to_send_to == 0:
            santas_in_ru = not_matched_santas.filter(my_region=0)
            target = get_random_santa(santas_in_ru, santas_in_ru.count())
        else:
            # my be make sense to process in beginning only those santas who deliver in russia
            target = get_random_santa(not_matched_santas, rest_target_count)

        santa.im_santa_for = target
        target.my_santa = santa
        santa.save()
        target.save()

        matched_santas.append(santa)
        santa = target
        rest_target_count -= 1
        not_matched_santas = not_matched_santas.exclude(id=santa.id)

    santa.im_santa_for = first_santa
    first_santa.my_santa = santa
    santa.save()
    first_santa.save()
    matched_santas.append(santa)



    # ready_to_send_to_ru = users.filter(ready_to_send_to=0)
    # print(ready_to_send_to_ru)
    # users_in_ru = users.filter(my_region=0)
    # print(users_in_ru)

    # for user in ready_to_send_to_ru:
    #     user_ru = get_user_from_list(user, 0)
    #     if user_ru is not None:
    #         user_ru.my_santa = user
    #         user_ru.save()


def get_random_santa(santas, count):
    print(count)
    random_index = randint(0, count - 1)
    print(random_index)

    return santas[random_index]



def get_user_from_list(user, region):
    result = User_s_santa.objects.filter(my_region=region, my_santa=None)
    for item in result:
        if item != user:
            return item
    return None

def dismatch():
    users = User_s_santa.objects.all()
    for user in users:
        user.my_santa = None
        user.im_santa_for = None
        user.save()
        
