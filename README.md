Visit The Website [here](recursioncat.pythonanywhere.com)

# CentralLib: Library_Management_with_python
Introducing CentralLib: a Python-based book library management system. With centralized storage, easy initialization, and essential attributes like ID, Name, and Author, CentralLib simplifies book organization. Create or load libraries, add, remove, and search books effortlessly. Future updates promise a user-friendly GUI, more search options, and additional attributes. CentralLib is your go-to solution for efficient and comprehensive book management.

## Features
### 1. Centralised Storage
All Books are stored in a centralised file, which is written to and read every time the library is initialised
### 2. Several Attributes
Books have the followng attributes currently:-
```
ID
Name
Author
Path
Last_page_read
```
more to come

## How to Use
### Import the Files
```
from Basic_Logic import *
```
### Initialize a  Book Object
The format is `Book(name, author, path_to_pdf)`. For example:
```
book1 = Book("Goosebumps", "R.L.Stine", "C://Users/......")
```
### Create/Load a Library file and Add your Book 
You can create a Library file with any name and a .lib extension. This file will store all your book data. If you already have an Existing library you can load it into memory using the same method.
`var_name = Library(name_of_library_file)`
for example:-
```
lib1 = Library(new_lib) #creates a new new_lib.lib file
lib2 = Library(old_lib) #load data from already exisiting file old_lib
```
Now you can add books (do not forget to convert make a book object)
```
lib1.add_book(book1)
```

### Remove a Book
You can remove a book by passing the book object in the `remove_book()` function. for example:
```
lib1.remove(book1)
```

### Searching for Books
You have the ability to search a book by name, by id, or search all the books of an author.
To search a book by name:<br />
`lib1.path_by_name(name_of_book)`<br />
To search by ID:<br />
`lib1.path_by_id(id_of_book)`<br />
To search all the Books of a Particular Author:<br />
`lib1.show_author(name_of_author)`<br />

### See all the books in a library
Once you are done with the books, you can see the whole library as a dataframe  by using `lib1.show_books()`

### Open a Book as a PDF
You can open a book as a pdf by calling the `open()` function from the book object.
```
book1 = ("Dracula", "Bram Stoker", "path_to_file")
book1.open()
```
this will ope the book in your default pdf viewer.

## Whats Coming in the Future
1. A GUI Based Frontend and Backend
2. More Search Options
3. More Book Attributes like Genre and plot
