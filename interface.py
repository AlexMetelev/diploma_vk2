# импорты
import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
# from data_store import Viewed

from pprint import pprint


# отправка сообщений

class BotInterface():
    def __init__(self, comunity_token, acces_token):
        self.vk = vk_api.VkApi(token=comunity_token)
        self.longpoll = VkLongPoll(self.vk)
        self.vk_tools = VkTools(acces_token)
        self.params = {}
        self.worksheets = []
        self.offset = 0

    def message_send(self, user_id, message, attachment=None):
        self.vk.method('messages.send',
                       {'user_id': user_id,
                        'message': message,
                        'attachment': attachment,
                        'random_id': get_random_id()}
                       )

    def get_data_from_user(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                return event.text.lower()

    def take_worksheet(self, tw_worksheets, user_id):
        print('twb')
        tw_worksheet = tw_worksheets.pop()
        print('tw')
        pprint(self.vk_tools.get_profile_info(tw_worksheet['id']))

        'проверка анкеты в бд в соотвествие с event.user_id'
        while check_user(user_id, tw_worksheet["id"]):
            tw_worksheet = tw_worksheets.pop()
            # print('Уже в базе')

        photos = self.vk_tools.get_photos(tw_worksheet['id'])
        tw_photo_string = ''
        for photo in photos:
            tw_photo_string += f'photo{photo["owner_id"]}_{photo["id"]},'
        return tw_worksheet, tw_photo_string

    # обработка событий / получение сообщений

    def event_handler(self):
        for event in self.longpoll.listen():
            if event.type == VkEventType.MESSAGE_NEW and event.to_me:
                self.params = self.vk_tools.get_profile_info(event.user_id)
                if event.text.lower() == 'привет':
                    '''Логика для получения данных о пользователе'''
                    # self.params = self.vk_tools.get_profile_info(event.user_id)
                    self.message_send(
                        event.user_id, f'Привет друг, {self.params["name"]}')
                elif event.text.lower() == 'поиск':
                    if self.params["city"] == None:
                        self.message_send(event.user_id, 'Ведите город:')
                        self.params["city"] = self.get_data_from_user()
                        print(self.params)
                    self.message_send(event.user_id, 'Минимальный возраст:')
                    self.params["age_from"] = int(self.get_data_from_user())
                    self.message_send(event.user_id, 'Максимальный возраст:')
                    self.params["age_to"] = int(self.get_data_from_user())

                    'Логика для поиска анкет'
                    self.message_send(event.user_id, 'Начинаем поиск')
                    pprint(self)
                    'если список пустой - false'
                    if self.worksheets:
                        print('не пустой список')
                        worksheet, photo_string = self.take_worksheet(self.worksheets, event.user_id)
                    else:
                        self.worksheets = self.vk_tools.search_worksheet(
                            self.params, self.offset)
                        print('пустой список')
                        pprint(self.worksheets)
                        try:
                            print('try')
                            worksheet, photo_string = self.take_worksheet(self.worksheets, event.user_id)
                            self.offset += 10
                        except:
                            self.message_send(event.user_id, 'Нет анкет. Попробуйте заново')
                            self.params["city"] = None
                            print(self.params)

                    try:
                        self.message_send(
                            event.user_id,
                            f'имя: {worksheet["name"]} ссылка: vk.com/{worksheet["id"]}',
                            attachment=photo_string)
                        'добавить анкету в бд в соотвествие с event.user_id'
                        self.message_send(event.user_id, 'Добавить анкету в БД ? (Да/...)')
                        if self.get_data_from_user() == 'да':
                            print('да')
                        #   add_user(event.user_id, worksheet["id"])
                    except:
                        self.message_send(event.user_id, 'Нет анкет, попробуйте заново')

                elif event.text.lower() == 'пока':
                    self.message_send(
                        event.user_id, 'До новых встреч')
                else:
                    self.message_send(
                        event.user_id, 'Неизвестная команда')


if __name__ == '__main__':
    bot_interface = BotInterface(comunity_token, acces_token)
    bot_interface.event_handler()