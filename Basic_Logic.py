import os
import platform
import pickle
import pandas as pd

class Library:
    def __init__(self, name) -> None:
        self.lib_name = name
        print(self.lib_name+".lib")
        try:
            if os.stat(str(name)+".lib").st_size == 0:
                self.books = pd.DataFrame(columns=['ID','Name','Author','Path','Last_page'])
            else:
                self.books = pd.read_pickle(str(name)+".lib")
        except FileNotFoundError:
            self.books = pd.DataFrame(columns=['ID','Name','Author','Path','Last_page'])
            with open(self.lib_name+".lib", 'wb') as file:
                pickle.dump(self.books, file)

    def add_book(self, book):
        id = book.id
        name = book.name.title()
        author = book.author.title()
        path = book.path
        last_page = book.last_page
        
        if id not in self.books['ID'].tolist():
            new_entry_df = pd.DataFrame([[id, name, author, path, last_page]], columns=['ID','Name', 'Author', 'Path', 'Last_page'])
            updated_df = pd.concat([self.books, new_entry_df], ignore_index=True)
            
            with open(self.lib_name+".lib", 'wb') as file:
                pickle.dump(updated_df, file)
            print("Entry Successful")
        else:
            print("Book Already exists")

    def show_books(self):
        print(pd.read_pickle(self.lib_name+".lib"))

    def remove_book(self, book):
        if book.id in self.books["ID"].tolist():
            self.books.drop(self.books[self.books["ID"] == book.id].index, inplace=True)
            with open(self.lib_name+".lib", 'wb') as file:
                pickle.dump(self.books, file)
            print("Deletion Successful")
        else:
            print("Book Not Found")

    def path_by_id(self, ID):
        if ID in self.books["ID"].tolist():
            return self.books.loc[self.books['ID'] == ID, 'Path'].iloc[0]
        else:
            print("Book Not Found")
        
    def path_by_name(self,name):
        if name in self.books["Name"].tolist():
            return self.books.loc[self.books['Name'] == name, 'Path'].iloc[0]
        else:
            print("Book Not found")

    def show_author(self, author):
        if author in self.books["Author"].tolist():
            return self.books[self.books["Author"] == author]
        else:
            print("Author Not Found")



class Book:
    def __init__(self, name, author, path) -> None:
        if name and author and path and path[-1:-4:-1]=="fdp":
            self.name = name
            self.author = author
            self.path = path
            self.id = self.name[-1:-3:-1]+self.author[0:2]
            self.last_page = 1
        else:
            raise Exception("Cannot add an Empty Book or Non pdf File")

    def open(self):
        try:
            if platform.system() == 'Darwin':       # macOS
                os.system(f'open "{self.path}"')
            elif platform.system() == 'Windows':    # Windows
                os.system(f'start "" "{self.path}"')
            else:                                   # linux variants
                os.system(f'xdg-open "{self.path}"')

        except Exception:
            print(Exception)
