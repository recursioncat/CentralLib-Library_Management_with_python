import os
import platform
import pickle
import pandas as pd

class Library:
    def __init__(self, name) -> None:
        self.lib_name = name
        print(self.lib_name+".lib")
        try:
            if os.stat("Server/"+str(name)+".lib").st_size == 0:
                self.books = pd.DataFrame(columns=['ID','Name','Author', 'Date', 'Image', 'Genre', 'Path','Last_page'])
            else:
                self.books = pd.read_pickle("Server/"+str(name)+".lib")
        except FileNotFoundError:
            self.books = pd.DataFrame(columns=['ID','Name','Author', 'Date', 'Image', 'Genre', 'Path','Last_page'])
            with open("Server/"+str(name)+".lib", 'wb') as file:
                pickle.dump(self.books, file)

    def add_book(self, book):
        id = book.id
        name = book.name.title()
        author = book.author.title()
        path = book.path
        last_page = book.last_page
        image = book.image
        genre = book.genre
        date = book.date
        
        if id not in self.books['ID'].tolist():
            new_entry_df = pd.DataFrame([[id, name, author, date, image, genre, path, last_page]], columns=['ID','Name','Author', 'Date' ,'Image', 'Genre', 'Path','Last_page'])
            updated_df = pd.concat([self.books, new_entry_df], ignore_index=True)
            self.books = updated_df
            
            with open("Server/"+self.lib_name+".lib", 'wb') as file:
                pickle.dump(updated_df, file)
            print("Entry Successful")
        else:
            print("Book Already exists")

    def add_collection(self, collection):
        for book in collection:
            self.add_book(book)

    def show_books(self):
        print(pd.read_pickle("Server/"+self.lib_name+".lib"))

    def remove_book(self, id):
        if id in self.books["ID"].tolist():
            self.books.drop(self.books[self.books["ID"] == id].index, inplace=True)
            with open("Server/"+self.lib_name+".lib", 'wb') as file:
                pickle.dump(self.books, file)
            return 1
        else:
            return 0

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
    def __init__(self, name, author, date, path, image, genre) -> None:
        if name and author and path and path[-1:-4:-1]=="fdp":
            self.name = name
            self.author = author
            self.path = path
            self.id = self.name[-1:-3:-1]+self.author[0:2]
            self.image = image
            self.genre = genre
            self.date = date
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



if __name__=="__main__":
    lib1 = Library("New_Library")
    # goosebumps = Book("Welcome to Dead House", "R.L.Stine", 1995, "Server/Books/01 - Welcome to Dead House - R.L. Stine - (BooksWorm.Tk).pdf", "goosebumps.jpeg", "Horror")
    # dracula = Book("Dracula", "Bram Stoker", 1897, "Server/Books/Dracula.pdf", "dracula.jpg", "Horror")
    # oliver = Book("Oliver Twist", "Charles Dickens", 1831, "Server/Books/oliver-twist.pdf", "oliver-twist.jpg", "Drama")
    # meeting = Book("Meeting Pool", "Ruskin Bond", 0000, "Server/Books/meeting-pool.pdf", "unknown.jpeg", "Drama")
    # pride = Book("Pride and Prejudice", "Jane Austen", 1811, "Server/Books/p&p.pdf", "pride.jpeg", "Drama")
    # lib1.add_collection([goosebumps, dracula, oliver, meeting, pride])
    # lib1.show_books()


    books = pd.read_pickle("Server/New_Library.lib")
    lib1.remove_book('alBr')
    print(books)