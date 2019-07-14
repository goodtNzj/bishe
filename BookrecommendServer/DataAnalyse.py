from DatabaseSet import ratings_explicit
from DatabaseSet import ratings_implicit
from DatabaseSet import users, books
import numpy as np
import pandas as pd
from sklearn.neighbors import NearestNeighbors

users_exp_ratings = users[users.userID.isin(ratings_explicit.userID)]
users_imp_ratings = users[users.userID.isin(ratings_implicit.userID)]
counts1 = ratings_explicit['userID'].value_counts()
# print(counts1)
# 至少评了100本书的人
ratings_explicit = ratings_explicit[ratings_explicit['userID'].isin(counts1[counts1 >= 100].index)]
counts2 = ratings_explicit['bookRating'].value_counts()
# print(counts2)
# 打同一分数的至少有100人
ratings_explicit = ratings_explicit[ratings_explicit['bookRating'].isin(counts2[counts2 >= 100].index)]
# print(ratings_explicit.head())
ratings_matrix = ratings_explicit.pivot(index='userID', columns='ISBN', values='bookRating')
userID = ratings_matrix.index
ISBN = ratings_matrix.columns
# print(ratings_matrix.shape) 304个用户对47155本书的打分
# print(ratings_matrix.head())
ratings_matrix.fillna(0, inplace=True)
ratings_matrix = ratings_matrix.astype(np.int32)
# print(type(ratings_matrix.index))
k = 10
metric = 'cosine'


# print(userID.unique())
# print(ISBN.unique())


def findksimilaritems(item_id, ratings, metric=metric, k=k):
    similarities = []
    indices = []
    ratings = ratings.T
    loc = ratings.index.get_loc(item_id)
    model_knn = NearestNeighbors(metric=metric, algorithm='auto')
    model_knn.fit(ratings)

    # 函数findksimilaritems使用最近邻方法采用余弦相似性来找到k+1项最相似的书(包括它自己，所以加1)，所以真正为10个最相近的书
    distances, indices = model_knn.kneighbors(ratings.iloc[loc, :].values.reshape(1, -1), n_neighbors=k + 1)
    similarities = 1 - distances.flatten()
    # 1减去distances数组中每一个元素
    # distances中每一元素越小，说明余弦距离越小，从而similarties每一元素越大，相似度越大
    # indices为相似度较高的每一个元素的索引
    return similarities, indices


def predict_itembased(user_id, item_id, ratings, metric=metric, k=k):
    prediction = wtd_sum = 0
    user_loc = ratings.index.get_loc(user_id)
    item_loc = ratings.columns.get_loc(item_id)
    similarities, indices = findksimilaritems(item_id, ratings)  # similar users based on correlation coefficients
    sum_wt = np.sum(similarities) - 1
    # 去掉自己
    for i in range(0, len(indices.flatten())):
        if indices.flatten()[i] == item_loc:  # 若在距离比较小的每一个书目中有自己要预测的书目(与自己预测的书目距离肯定为0)则跳过
            continue
        else:
            product = ratings.iloc[user_loc, indices.flatten()[i]] * (similarities[i])
            # 根据此人对其他距离相近的书的评价预测对此书的评价
            wtd_sum = wtd_sum + product
    prediction = int(round(wtd_sum / sum_wt))

    # 在非常稀疏的数据集的情况下，使用基于协作的方法的相关度量可能会给出负面的评价
    # 在这里处理的是下面的//代码，没有下面的代码片段，下面的代码片段是为了避免负面影响
    # 在使用相关度规时，可能会出现非常稀疏的数据集的预测
    if prediction <= 0:
        prediction = 1
    elif prediction > 10:
        prediction = 10
    # print('用户预测等级 {0} -> item {1}: {2}'.format(user_id, item_id, prediction))
    return prediction




# recommendItem('4385', ratings_matrix)

# def recommendItem(user_id, ratings, metric=metric):
#     print(ratings.index)
#     user_location = ratings.index.get_loc(user_id)
#     prediction = []
#     prediction = pd.Series(prediction)
#     for i in range(ratings.shape[1]):
#         item_location = ratings.columns.get_loc(str(ratings.columns[i]))
#         if ratings.iloc[user_location, item_location] == 0:  # not rated already
#             prediction.append(pd.Series([predict_itembased(str(user_id), str(ratings.columns[i]), ratings, metric)]))
#         else:
#             prediction.append(pd.Series([-1]))  # for already rated items
#             # prediction = pd.Series(prediction)
#             prediction = prediction.sort_values(ascending=False)
#             recommended = prediction[:10]
#     print("As per {0} approach....Following books are recommended...".format('Item-based'))
#     for i in range(len(recommended)):
#         print("{0}. {1}".format(i + 1, books.bookTitle[recommended.index[i]].encode('utf-8')))
#
#
# recommendItem('104399', ratings_matrix)

