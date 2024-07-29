import pymysql


config = {'host': '127.0.0.1', 'port': 8889, 'user': 'root', 'password': 'root', 'database': 'upcoming_concerts'}


def get_from_db(value, request):
    try:
        connection = pymysql.connect(host=config['host'], port=config['port'], user=config['user'],
                                     password=config['password'], database=config['database'])
        with connection.cursor() as cursor:
            cursor.execute(request, value)
            data = cursor.fetchall()
        connection.close()
        return data
    except Exception as e:
        print(f'database exception: {e}')


def change_db(value, request):
    try:
        connection = pymysql.connect(host=config['host'], port=config['port'], user=config['user'],
                                     password=config['password'], database=config['database'])
        with connection.cursor() as cursor:
            cursor.execute(request, value)
        connection.commit()
        connection.close()
    except Exception as e:
        print(f'database exception: {e}')
