import os
import platform
import pickle
import pandas as pd
import PyPDF2

def get_num_pages(pdf_path):
    with open(pdf_path, 'rb') as file:
        pdf_reader = PyPDF2.PdfReader(file)
        num_pages = len(pdf_reader.pages)
    return num_pages

class Library:
    def __init__(self, name) -> None:
        self.lib_name = name
        print(self.lib_name+".lib")
        try:
            if os.stat("Server/"+str(name)+".lib").st_size == 0:
                self.books = pd.DataFrame(columns=['ID','Name','Author', 'Date', 'Image', 'Genre', 'Path','Last_page', 'Total_Pages', 'Plot'])
            else:
                self.books = pd.read_pickle("Server/"+str(name)+".lib")
        except FileNotFoundError:
            self.books = pd.DataFrame(columns=['ID','Name','Author', 'Date', 'Image', 'Genre', 'Path','Last_page', 'Total_Pages', 'Plot'])
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
        total_pages = book.total_pages
        plot = book.plot
        
        if id not in self.books['ID'].tolist():
            new_entry_df = pd.DataFrame([[id, name, author, date, image, genre, path, last_page, total_pages, plot]], columns=['ID','Name','Author', 'Date' ,'Image', 'Genre', 'Path','Last_page', 'Total_Pages', 'Plot'])
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
    def __init__(self, name, author, date, path, image, genre, plot) -> None:
        if name and author and path and path[-1:-4:-1]=="fdp":
            self.name = name
            self.author = author
            self.path = path
            self.id = self.name[-1:-3:-1]+self.author[0:2]
            self.image = image
            self.genre = genre
            self.date = date
            self.last_page = 1
            self.total_pages = get_num_pages(path)
            self.plot = plot
    
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



# if __name__=="__main__":
#     lib1 = Library("New_Library")
#     # goosebumps = Book("Welcome to Dead House", "R.L.Stine", 1995, "Server/Books/01 - Welcome to Dead House - R.L. Stine - (BooksWorm.Tk).pdf", "goosebumps.jpeg", "Horror", "In \"Welcome to Dead House\" the Benson family moves to Dark Falls, a town filled with undead creatures. Amanda and Josh must unravel the town's dark secret and escape before becoming its permanent residents. They encounter ghostly figures and eerie occurrences, leading to a thrilling showdown where they confront the evil forces lurking within Dark Falls")

#     # dracula = Book("Dracula", "Bram Stoker", 1897, "Server/Books/Dracula.pdf", "dracula.jpg", "Horror", "Jonathan Harker journeys to Transylvania to assist Count Dracula with a real estate transaction in England. However, he soon realizes Dracula is a vampire who preys on innocent victims. With the help of Professor Van Helsing and others, they battle Dracula's undead forces to save Mina, Harker's fiancée, and stop the vampire's reign of terror. The story unfolds through journal entries, letters, and newspaper clippings, building suspense as they race against time to defeat the ancient evil.")
    
#     # oliver = Book("Oliver Twist", "Charles Dickens", 1831, "Server/Books/oliver-twist.pdf", "oliver-twist.jpg", "Drama", "A young orphan named Oliver navigates the grim streets of Victorian London. After escaping from a workhouse, he encounters a band of pickpockets led by the cunning Fagin and the menacing Bill Sikes. Oliver's innocence contrasts with the corruption and cruelty surrounding him as he seeks kindness and acceptance. Despite facing adversity, Oliver forms bonds with compassionate individuals like Mr. Brownlow and Nancy, who ultimately help him uncover the truth of his identity and find a better life. The novel explores themes of poverty, social injustice, and the power of compassion in a harsh world.")

#     # meeting = Book("Meeting Pool", "Ruskin Bond", 0000, "Server/Books/meeting-pool.pdf", "unknown.jpeg", "Drama", "Three Friends Promise To meet at a Pool when they have all grown up. Classic Ruskin Bond and his Exploration into Nostalgia.")

#     # pride = Book("Pride and Prejudice", "Jane Austen", 1811, "Server/Books/p&p.pdf", "pride.jpeg", "Drama","Elizabeth Bennet navigates the intricacies of love and social status in Regency-era England. When the wealthy and aloof Mr. Darcy enters her life, she forms a negative opinion of him based on his apparent arrogance. Meanwhile, her sisters pursue their own romantic interests, leading to misunderstandings and heartache. As Elizabeth and Mr. Darcy's paths continue to intersect, they confront their own prejudices and pride, eventually realizing the depth of their feelings for each other. Jane Austen's classic novel explores themes of class, marriage, and the complexities of human relationships in a society bound by strict social norms.")

#     # lib1.add_collection([goosebumps, dracula, oliver, meeting, pride])
#     # lib1.show_books()


#     lib1.show_books()