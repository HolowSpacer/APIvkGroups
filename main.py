from pprint import pprint
from urllib.parse import urlencode
from pip._vendor import requests
import json
import time

TOKEN = '958eb5d439726565e9333aa30e50e0f937ee432e927f0dbd541c541887d919a7c56f95c04217915c32008'
params = {
    'access_token': TOKEN,
    'v': '5.89'
}

class Invalid_Id_Input(Exception):
    def __init__(self, text):
        self.txt = text

def input_and_get_id() -> str:
    id_or_name_user = str(input())
    try:
        user = requests.get('https://api.vk.com/method/users.get?user_ids=' + id_or_name_user,
                            params)
        if str(user.json().get('response', 'invalid')) == 'invalid':
            raise Invalid_Id_Input('Неверный id пользователя')
    except Invalid_Id_Input as e:
        print(e)
    else:
        return str(user.json()['response'][0]['id'])


def get_friends(id) -> set:
    friends = requests.get(
        'https://api.vk.com/method/friends.get?user_id=' + str(id),
        params)
    return set(friends.json()['response']['items'])


def get_groups(id) -> set:
    groups = requests.get(
        'https://api.vk.com/method/users.getSubscriptions?user_id=' + str(id),
        params)
    time.sleep(0.2)
    return set(groups.json()['response']['groups']['items'])


def comprasion_groups(set_friend_groups, set_user_groups) -> None:
    i = 1
    for group in set_user_groups:
        if group in set_friend_groups:
            print(group)
            set_user_groups.pop([i])
        i += 1


def set_sort_user_groups(set_id_user) -> set:
    counter = 0
    user_groups = get_groups(set_id_user)
    user_friends = get_friends(set_id_user)
    set_len = len(user_friends)
    for friend in user_friends:
        try:
            friend_groups = get_friends(friend)
        except KeyError:
            friends_groups = None
        else:
            comprasion_groups(friend_groups, user_groups)
        counter += 1
        print(f'Проверено {round(counter * 100/set_len)}%')
        if counter > 1000:
            break
    return user_groups


def json_creater(groups_set) -> list:
    counter = 0
    len_dict = len(groups_set)
    json_format = []
    for group in groups_set:
        list_name_and_count = get_group_name_and_members_count(group)
        json_format.append({'name': list_name_and_count[0],
        'gid': group,
        'members_count': list_name_and_count[1]})
        counter += 1
        print(f'Записано {round(counter * 100/len_dict)} %')
    return json_format



def get_group_name_and_members_count(group_id) -> list:
    time.sleep(0.4)
    name = requests.get(
        'https://api.vk.com/method/groups.getById?group_id=' + str(group_id) + '&fields=members_count',
        params)
    name_json = name.json()
    list_json_name = [name_json['response'][0]['name'], name_json['response'][0]['members_count']]
    return list_json_name


id_user = input_and_get_id()
if id_user:
    with open('venv/groups.json', 'w', encoding='utf-8') as f:
        json.dump(json_creater(set_sort_user_groups(id_user)), f, ensure_ascii=False, indent=2)


