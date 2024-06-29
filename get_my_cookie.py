#Получение куки. Заходим на сайт, сами ручками авторизуемся и сохраняем куки для дальнейшнего использования
import pickle
from time import sleep


def get_my_cookie(cookie):
    sleep(60)
    pickle.dump(cookie, open('cookies.pkl', 'wb'))