import socket
import pandas as pd
import numpy as np
import re
import time
from DataAnalyse import metric
from DatabaseSet import books
from DataAnalyse import ratings_matrix
from DataAnalyse import predict_itembased


def maerank(user_id):
    count = 0
    s =0
    for i in range(ratings_matrix.shape[1]):
        if ratings_matrix[str(ratings_matrix.columns[i])][user_id] == 0 and count < 20:
            count += 1
            user_loc = ratings_matrix.index.get_loc(user_id)
            item_loc = ratings_matrix.columns.get_loc(str(ratings_matrix.columns[i]))
            print(predict_itembased(user_id, str(ratings_matrix.columns[i]), ratings_matrix, metric), ratings_matrix.iloc[user_loc, item_loc], sep = ',')


def recommendItem(user_id, metric=metric):
    if (user_id not in ratings_matrix.index.values) or type(user_id) is not str:
        data = "User id should be a valid integer from this list :\n\n {} ".format(re.sub('[\[\]]', '', np.array_str(ratings_matrix.index.values)))

    else:
        data = []
        prediction = []
        for i in range(ratings_matrix.shape[1]):
            if (ratings_matrix[str(ratings_matrix.columns[i])][user_id] != 0): #not rated already
                prediction.append(predict_itembased(user_id, str(ratings_matrix.columns[i]), ratings_matrix, metric))
            else:
                prediction.append(-1) #for already rated items
        prediction = pd.Series(prediction)
        prediction = prediction.sort_values(ascending=False)
        recommended = prediction[:10]
        for i in range(len(recommended)):
            data.append("{0}. {1}".format(i+1, books.bookTitle[recommended.index[i]]))
        print(maerank(user_id))
    return data


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(('172.17.28.208', 8000))
server.listen(5)
while True:
    conn: socket
    conn, addr = server.accept()
    print("connect successfully", time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(time.time())), sep = ' ')
    user_id = conn.recv(2048)
    recommend = recommendItem(user_id.decode(encoding='utf_8', errors='strict'))
    result = ""
    if type(recommend) is str:
        conn.sendall(recommend.encode(encoding='utf_8', errors='strict'))
    else:
        for j in range(len(recommend)):
            result = result + recommend[j] + "||"
        result = result[:-2]
        conn.sendall(result.encode(encoding='utf_8', errors='strict'))
    conn.close()


