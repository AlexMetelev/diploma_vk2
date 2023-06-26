from pprint import pprint
from datetime import datetime
# импорты
# import sqlalchemy as sq
import vk_api
from vk_api.exceptions import ApiError

# from config import acces_token

# импорты
# import vk_api
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.utils import get_random_id

from config import comunity_token, acces_token
from core import VkTools
from interface import BotInterface

if __name__ == '__main__':
    # bot_interface = BotInterface(comunity_token, acces_token)
    # bot_interface.event_handler()

    # if __name__ == '__main__':
    user_id = 183447999
    tools = VkTools(acces_token)
    params = tools.get_profile_info(user_id)

    pprint(params)

    worksheets = tools.search_worksheet(params, 20)
    worksheet = worksheets.pop()
    photos = tools.get_photos(worksheet['id'])

    pprint(worksheets)
    # pprint(photos)