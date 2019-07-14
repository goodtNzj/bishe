import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import warnings

warnings.filterwarnings('ignore')
pd.set_option('display.max_columns', None)
# 显示所有行
pd.set_option('display.max_rows', None)
# 设置显示列数超过1000才换行
pd.set_option('display.width', 1000)
pd.set_option('max_colwidth', 2000)
books = pd.read_csv("BX-CSV-Dump/BX-Books.csv", sep=";", low_memory=False, error_bad_lines=False, encoding="latin-1")
books.columns = ["ISBN", "bookTitle", "bookAuthor", "yearOfPublication", "publisher",
                 "imageUrlS", "imageUrlM", "imageUrlL"]
users = pd.read_csv("BX-CSV-Dump/BX-Users.csv", sep=";", low_memory=False, error_bad_lines=False, encoding="latin-1")
users.columns = ["userID", "Location", "Age"]
ratings = pd.read_csv("BX-CSV-Dump/BX-Book-Ratings.csv", sep=";", low_memory=False, error_bad_lines=False,
                      encoding="latin-1")
ratings.columns = ["userID", "ISBN", "bookRating"]
# print(books.shape)
# print(users.shape)
# print(ratings.shape)
# print(books.head())
books.drop(["imageUrlS", "imageUrlM", "imageUrlL"], axis=1, inplace=True)
# print(books.head())
# print(books.dtypes)
# print(books.yearOfPublication.unique())
print(books.loc[books.yearOfPublication == "DK Publishing Inc", :])
# 0789466953
books.loc[books.ISBN == '0789466953', 'yearOfPublication'] = 2000
books.loc[books.ISBN == '0789466953', 'bookAuthor'] = "James Buckley"
books.loc[books.ISBN == '0789466953', 'publisher'] = "DK Publishing Inc"
books.loc[books.ISBN == '0789466953', 'bookTitle'] = "DK Readers: Creating the X-Men, How Comic Books Come to Life " \
                                                     "(Level 4: Proficient Readers)"
# 078946697x
books.loc[books.ISBN == '078946697X', 'yearOfPublication'] = 2000
books.loc[books.ISBN == '078946697X', 'bookAuthor'] = "Michalel Teitelbaum"
books.loc[books.ISBN == '078946697X', 'publisher'] = "DK Publishing Inc"
books.loc[books.ISBN == '078946697X', 'bookTitle'] = "DK Readers: Creating the X-Men, How It All Began (Level 4: " \
                                                     "Proficient Readers)"
# print()
# print(books.loc[(books.ISBN == '0789466953') | (books.ISBN == '078946697X'), :])
books.yearOfPublication = pd.to_numeric(books.yearOfPublication, errors='coerce')
books.loc[(books.yearOfPublication > 2006) | (books.yearOfPublication == 0), 'yearOfPublication'] = np.NAN
books.yearOfPublication.fillna(round(books.yearOfPublication.mean()), inplace=True)
# print(books.yearOfPublication.isnull().sum())
books.yearOfPublication = books.yearOfPublication.astype(np.int32)
# print(sorted(books['yearOfPublication'].unique()))
# print(books.loc[books.publisher.isnull(), :])
books.loc[(books.ISBN == '193169656X'), 'publisher'] = 'other'
books.loc[(books.ISBN == '1931696993'), 'publisher'] = 'other'
# 用户数据集
# print(users.shape)
# print(users.head())
# print(users.dtypes)
# print(users.userID.values)
users.loc[(users.Age > 90) | (users.Age < 5), 'Age'] = np.NAN
users.Age = users.Age.fillna(round(users.Age.mean()))
users.Age = users.Age.astype(np.int32)
# print(sorted(users.Age.unique()))
# print(ratings.shape)
n_users = users.shape[0]
n_books = books.shape[0]
# print(n_users*n_books)
# print(ratings.head())
ratings_new = ratings[ratings.ISBN.isin(books.ISBN)]
ratings_new = ratings_new[ratings_new.userID.isin(users.userID)]
# print("number of users: " + str(n_users))
# print("number of books: " + str(n_books))
sparsity = 1.0 - len(ratings_new) / float(n_users * n_books)
print('图书交叉数据集的稀疏级别是 ' + str(sparsity * 100) + ' %')
ratings_explicit = ratings_new[ratings_new.bookRating != 0]
ratings_implicit = ratings_new[ratings_new.bookRating == 0]
# print(ratings_new.shape)
#print(ratings_explicit.shape)
# print(ratings_implicit.shape)
sns.countplot(data=ratings_explicit, x='bookRating')
plt.show()
