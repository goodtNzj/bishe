import pymysql
import pandas as pd
import traceback
import numpy as np
import warnings

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置显示列数超过1000才换行
pd.set_option('display.width', 1000)
pd.set_option('max_colwidth', 2000)
URL = "localhost"
User = "admin1"
Password = "123456"
Database = "bookcrossing"
db = pymysql.connect(URL, User, Password, Database, charset='utf8')
cursor = db.cursor()
sql1 = "select * from `BX-Books`"
sql2 = "select * from `BX-Users`"
sql3 = "select * from `BX-Book-Ratings`"


def get_df(sql):
    try:
        db.ping(reconnect=True)
        cursor.execute(sql)
        res = cursor.fetchall()
        df = pd.DataFrame(list(res))
        return df
    except Exception:
        traceback.print_exc()


books = get_df(sql1)
books.columns = ["ISBN", "bookTitle", "bookAuthor", "yearOfPublication", "publisher",
                         "imageUrlS", "imageUrlM", "imageUrlL"]
users = get_df(sql2)
users.columns = ["userID", "Location", "Age", "Password"]
ratings = get_df(sql3)
ratings.columns = ["userID", "ISBN", "bookRating"]
# print(books.head())
# print(users.head())
# print(ratings.head())
# print(books.shape)
# print(users.shape)
# print(ratings.shape)
users.drop(["Password"], axis=1, inplace=True)
books.drop(["imageUrlS", "imageUrlM", "imageUrlL"], axis=1, inplace=True)
# print(books.head())
# print(books.yearOfPublication.unique())
books.yearOfPublication = pd.to_numeric(books.yearOfPublication, errors='coerce')
books.loc[(books.yearOfPublication > 2006) | (books.yearOfPublication == 0), 'yearOfPublication'] = np.NAN
books.yearOfPublication.fillna(round(books.yearOfPublication.mean()), inplace=True)
books.yearOfPublication = books.yearOfPublication.astype(np.int32)
books.loc[(books.ISBN == '193169656X'), 'publisher'] = 'other'
books.loc[(books.ISBN == '1931696993'), 'publisher'] = 'other'
users.loc[(users.Age > 90) | (users.Age < 5), 'Age'] = np.NAN
users.Age = users.Age.fillna(round(users.Age.mean()))
users.Age = users.Age.astype(np.int32)
ratings_new = ratings[ratings.ISBN.isin(books.ISBN)]
ratings_new = ratings_new[ratings_new.userID.isin(users.userID)]
ratings_explicit = ratings_new[ratings_new.bookRating != 0]
ratings_implicit = ratings_new[ratings_new.bookRating == 0]
# print(ratings_new.shape)
# print(ratings_explicit.shape)
# print(ratings_implicit.shape)
# sns.countplot(data=ratings_explicit, x='bookRating')
# plt.show()
db.close()
# print(ratings_explicit.dtypes)



