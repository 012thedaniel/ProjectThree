import spacy
from datetime import datetime
from db import get_from_db, change_db
from regex import scenario_manager, scenarios_user
from sql_requests import queries


@spacy.Language.component('component')
def component(doc):
    print('lemmas:', [token.lemma_ for token in doc])
    return doc


def get_venues_of_artist(artist):
    while True:
        try:
            artist_id = get_from_db(artist, queries['get_id_of_artist'])[0][0]
            venues = get_from_db(artist_id, queries['get_artists_venues'])
            return venues if venues else 'подій не заплановано'
        except IndexError:
            user_input = input(
                '\t** Такий виконавець на даний момент відсутній у БД **\n\tВведіть імʼя іншого '
                'виконавця для того, щоб продовжити, або \'завершити\', щоб завершити запит >> '
            )
            if user_input == 'завершити':
                return user_input
            artist = user_input


def city_validation(city):
    while not get_from_db(city, queries['check_existence_of_city']):
        user_input = input(
            "\t** Таке місто на даний момент відсутнє у БД **\n\tВведіть назву іншого міста "
            "для того, щоб продовжити, або 'завершити', щоб завершити запит >> "
        )
        if user_input == 'завершити':
            return False
        city = user_input
    return True


# requires improvement
def parse_city(lemmas):
    if lemmas[-2] == 'місто':
        return lemmas[:-3], lemmas[-1]
    elif lemmas[-2] == '-':
        return lemmas[:-5], f'{lemmas[-3]}-{lemmas[-1]}'
    return lemmas[:-4], f'{lemmas[-2]} {lemmas[-1]}'


def get_venues_in_city(city):
    if not city_validation(city):
        return 'завершити'
    venues = get_from_db(city, queries['get_venues_in_city'])
    return venues if venues else 'подій не заплановано'


def process_city_request(city, venues_quantity):
    while True:
        result = get_venues_in_city(city)
        match result:
            case 'завершити':
                return 'Добре, тоді введіть свій наступний запит >> '
            case 'подій не заплановано':
                print(f'  На жаль в даному місті не заплановано жодного концерту найближчим часом:(')
            case _:
                match venues_quantity:
                    case 'one':
                        concert = result[0]
                        concert_date = concert[-1].strftime('%d.%m.%y')
                        concert_time = concert[-1].strftime('%H:%M')
                        print(
                            f'  Найближчий концерт у місті {concert[2]} ({concert[3]}) - це виступ виконавця {concert[0]}, '
                            f'запланований на {concert_time} {concert_date} за адресою {concert[4]} ({concert[1]}).'
                        )
                    case 'many':
                        print(
                            f'  Список всіх запланованих концертів у місті {result[0][2]} ({result[0][3]}) '
                            f'в хронологічному порядку:'
                        )
                        for concert in result:
                            concert_date = concert[-1].strftime('%d.%m.%y')
                            concert_time = concert[-1].strftime('%H:%M')
                            print(f'\t{concert[0]} - {concert_date} о {concert_time} за адресою {concert[4]} ({concert[1]}).')
        users_input = input(
            f'Можливо ви бажаєте здійснити пошук '
            f'{'події' if venues_quantity == 'one' else 'подій'} в іншому місті? >> '
        )
        if not process_yes_no_question(users_input):
            return 'Добре, тоді введіть свій наступний запит >> '
        city = input('Тоді введіть назву міста >> ')


def process_artist_request(artist, venues_quantity):
    while True:
        result = get_venues_of_artist(artist)
        match result:
            case 'завершити':
                return 'Добре, тоді введіть свій наступний запит >> '
            case 'подій не заплановано':
                print(f'  На жаль у даного виконавця не заплановано жодного концерту найближчим часом:(')
            case _:
                match venues_quantity:
                    case 'one':
                        concert = result[0]
                        concert_date = concert[-1].strftime('%d.%m.%y')
                        concert_time = concert[-1].strftime('%H:%M')
                        print(
                            f'  Найближчий концерт виконавця {concert[0]} відбудеться {concert_date} о '
                            f'{concert_time} за адресою {concert[4]}, {concert[2]}, {concert[3]} ({concert[1]}).'
                        )
                    case 'many':
                        print(f'  Список всіх концертів виконавця {result[0][0]} в хронологічному порядку:')
                        for concert in result:
                            concert_date = concert[-1].strftime('%d.%m.%y')
                            concert_time = concert[-1].strftime('%H:%M')
                            print(f'\t{concert_date} о {concert_time} за адресою '
                                  f'{concert[4]}, {concert[2]}, {concert[3]} ({concert[1]})')
        users_input = input(
            f'Можливо ви бажаєте здійснити пошук '
            f'{'події' if venues_quantity == 'one' else 'подій'} у іншого виконавця? >> '
        )
        if not process_yes_no_question(users_input):
            return 'Добре, тоді введіть свій наступний запит >> '
        artist = input("Тоді введіть імʼя виконавця >> ")


def process_yes_no_question(users_input):
    doc = nlp(users_input)
    lemmas = [token.lemma_ for token in doc]
    if 'так' in lemmas:
        return True
    return False


def process_artist_and_city_request(artist, city):
    while True:
        result = get_venues_of_artist(artist)
        match result:
            case 'завершити':
                return 'Добре, тоді введіть свій наступний запит >> '
            case 'подій не заплановано':
                print(f'  На жаль у даного виконавця не заплановано жодного концерту найближчим часом:(')
                users_input = input(f'Можливо ви бажаєте здійснити пошук концерту іншого виконавця в цьому ж місті? >> ')
                if not process_yes_no_question(users_input):
                    return 'Добре, тоді введіть свій наступний запит >> '
                artist = input('Тоді введіть імʼя виконавця >> ')
            case _:
                if not city_validation(city):
                    return 'Добре, тоді введіть свій наступний запит >> '
                for venue in result:
                    if venue[2].lower() == city:
                        concert = venue
                        concert_date = concert[-1].strftime('%d.%m.%y')
                        concert_time = concert[-1].strftime('%H:%M')
                        print(
                            f'  Найближчий концерт виконавця {concert[0]} в місті {concert[2]} ({concert[3]}) '
                            f'відбудеться {concert_date} о {concert_time} за адресою {concert[4]} ({concert[1]}).'
                        )
                        break
                else:
                    print(f'  На жаль у даного виконавця не заплановано жодного концерту в даному місті найближчим часом:(')
                users_input = input(f'Можливо ви бажаєте здійснити пошук концерту цього ж виконавця в іншому місті? >> ')
                if not process_yes_no_question(users_input):
                    return 'Добре, тоді введіть свій наступний запит >> '
                city = input("Тоді введіть назву міста >> ")


def string_input_validation(normal_prompt, sql_request, error_prompt):
    current_prompt = normal_prompt
    while True:
        user_input = input(current_prompt)
        try:
            if current_prompt == error_prompt and user_input.lower() == 'завершити':
                return None
            return get_from_db(user_input, sql_request)[0][0]
        except IndexError:
            current_prompt = error_prompt


def date_input_validation(normal_prompt, error_prompt):
    current_prompt = normal_prompt
    while True:
        user_input = input(current_prompt)
        try:
            if current_prompt == error_prompt and user_input.lower() == 'завершити':
                return None
            return datetime.strptime(user_input, '%d.%m.%y %H:%M')
        except ValueError:
            current_prompt = error_prompt


def add_venue():
    artist_id = string_input_validation(
        "Введіть імʼя виконавця >> ", queries["get_id_of_artist"],
        "\t** Такий виконавець на даний момент відсутній у БД **\n\tВведіть імʼя іншого "
        "виконавця для того, щоб продовжити, або 'завершити', щоб скасувати додавання події >> "
    )
    if not artist_id:
        return False
    place_id = string_input_validation(
        "Введіть місце проведення події >> ", queries["get_id_of_place"],
        "\t** Таке місце проведення подій на даний момент відсутнє в БД **\n\tВведіть інше місце "
        "проведення події для того, щоб продовжити, або 'завершити', щоб скасувати додавання події >> "
    )
    if not place_id:
        return False
    concert_datetime = date_input_validation(
        "Введіть дату та час проведення у форматі 'дд.мм.рр гг:хх' >> ",
        "\t** Некоректно заданий формат дати **\n\tВведіть дату та час проведення у форматі "
        "'дд.мм.рр гг:хх' для того, щоб продовжити, або 'завершити', щоб скасувати додавання події >> "
    )
    if not concert_datetime:
        return False
    change_db((artist_id, place_id, concert_datetime), queries["add_venue_to_db"])
    return True


def process_adding_venue_request():
    users_input = 'так'
    while process_yes_no_question(users_input):
        if not add_venue():
            break
        users_input = input('Нову подію успішно додано! Хочете додати ще? >> ')


def entity_extractor(doc, entity):
    lemmas = []
    for ent in doc.ents:
        if ent.label_ in entity:
            lemmas.append(ent.lemma_)
    return lemmas


def process_adding_venue_request_lm(doc):
    action_lemma_options = ['додати', 'внести', 'створити', 'записати', 'вставити']
    venue_lemma_options = ['захід', 'подія', 'концерт', 'шоу', 'виступ']
    action_lemma_found, venue_lemma_found = False, False
    for token in doc:
        if token.lemma_ in action_lemma_options and token.dep_ in ['ROOT', 'xcomp']:
            action_lemma_found = True
        elif token.lemma_ in venue_lemma_options and token.dep_ == 'obj':
            venue_lemma_found = True
    if action_lemma_found and venue_lemma_found:
        process_adding_venue_request()
        return 'Добре, тоді введіть свій наступний запит >> '
    else:
        return 'Невідомий для мене запит:( Спробуйте ще раз >> '


def check_venue_lemma_in_sentence(doc):
    venue_lexeme_options = {
        'захід': {
            'singular': ['захід', 'заходу', 'заходові', 'заходом', 'заході', 'заходе'],
            'plural':   ['заходи', 'заходів', 'заходам', 'заходи', 'заходами', 'заходах', ]
        },
        'подія': {
            'singular': ['подія', 'події', 'подію', 'подією', 'подіє'],
            'plural':   ['події', 'подій', 'подіям', 'подіями', 'подіях']
        },
        'концерт': {
            'singular': ['концерт', 'концерту', 'концертові', 'концертом', 'концерті', 'концерте'],
            'plural':   ['концерти', 'концертів', 'концертам', 'концертами', 'концертах']
        },
        'шоу': {
            'singular': ['шоу'],
            'plural':   ['шоу']
        },
        'виступ': {
            'singular': ['виступ', 'виступу', 'виступові', 'виступом', 'виступі', 'виступе'],
            'plural': ['виступи', 'виступів', 'виступам', 'виступами', 'виступах']
        }
    }
    for token in doc:
        if token.lemma_ in venue_lexeme_options.keys():
            return 'singular' if token.text in venue_lexeme_options[token.lemma_]['singular'] else 'plural'
    return None


def virtual_assistant(person):
    prompt = 'Введіть свій запит >> '
    phrase = input(prompt)
    phrase = phrase if phrase[-1] != '?' else phrase[:-1]
    doc = nlp(phrase)
    lemmas = [token.lemma_ for token in doc]
    while 'бувати' not in lemmas:
        if person == 'user':
            for scenario_num, scenario in enumerate(scenarios_user, 1):
                if scenario.search(phrase):
                    match scenario_num:
                        case 1 | 2 | 3:
                            if scenario_num in [2, 3] and lemmas[-1] == 'час':
                                lemmas = lemmas[:-2]
                            artist = lemmas[-1] if lemmas[-2] == 'виконавець' else f'{lemmas[-2]} {lemmas[-1]}'
                            prompt = process_artist_request(artist, 'one' if scenario_num == 1 else 'many')
                        case 4 | 5:
                            if scenario_num == 5 and lemmas[-1] == 'час':
                                lemmas = lemmas[:-2]
                            _, city = parse_city(lemmas)
                            prompt = process_city_request(city, 'one' if scenario_num == 4 else 'many')
                        case 6:
                            lemmas, city = parse_city(lemmas)
                            artist = lemmas[-1] if lemmas[-2] == 'виконавець' else f'{lemmas[-2]} {lemmas[-1]}'
                            prompt = process_artist_and_city_request(artist, city)
                    break
            else:
                gpe = entity_extractor(doc, ['LOC'])
                per = entity_extractor(doc, ['PER', 'ORG'])
                if per and gpe:
                    prompt = process_artist_and_city_request(per[0], gpe[0])
                elif per:
                    result = check_venue_lemma_in_sentence(doc)
                    prompt = process_artist_request(per[0], 'one' if result == 'singular' else 'many')
                elif gpe:
                    result = check_venue_lemma_in_sentence(doc)
                    prompt = process_city_request(gpe[0], 'one' if result == 'singular' else 'many')
                else:
                    prompt = 'Невідомий для мене запит:( Спробуйте ще раз >> '
        else:
            if scenario_manager.search(phrase):
                process_adding_venue_request()
                prompt = 'Добре, тоді введіть свій наступний запит >> '
            else:
                prompt = process_adding_venue_request_lm(doc)
        phrase = input(prompt)
        phrase = phrase if phrase[-1] != '?' else phrase[:-1]
        doc = nlp(phrase)
        lemmas = [token.lemma_ for token in doc]


if "__main__" == __name__:
    nlp = spacy.load("uk_core_news_lg")
    nlp.add_pipe('component')
    virtual_assistant('user')
