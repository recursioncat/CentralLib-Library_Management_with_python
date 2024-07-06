from flask import Flask, render_template, request, redirect, send_file, url_for, jsonify, session
import pandas as pd
from Backend_Scripts.additional import pdf_to_image
from Backend_Scripts.Basic_Logic import Book, Library  
import os, shutil
import json


def to_raw(string):
    return fr"{string}"

app = Flask(__name__)
app.secret_key = 'xxxxxxxxxxxxx'
app.config['books'] = "Server/Books"
app.config['thumbnails'] = "static/thumbnails"
users = {'Rishit': '260704'}
logged_in = False


books_df = Library("New_Library")
IMAGE_DIR = os.path.join("static", "Images")

# Route to render main.html
@app.route('/')
def index():
    # Redirect to the home route
    return redirect('/home')



@app.route('/home', methods=['GET', 'POST'])
def home():
  global books_df
  books = books_df.books.to_dict('records')
  if 'Homepage-alert' in session:
    alert = session['Homepage-alert']
  else:
      alert = ""
  return render_template('home.html', books = books, genre = "All", alert = alert)

@app.route('/search', methods = ['POST', 'GET'])
def search():
    try:
        genre = "All"
        value = request.form.get("Search-Field", "")
        print("What BAckend Recieved: ", value)
        keyword = value.lower()
        filtered_books = books_df.books[books_df.books['Name'].str.lower().str.contains(keyword)]
        books = filtered_books.to_dict('records')
        empty_search = len(filtered_books) == 0
        session['Homepage-alert'] = r""
        return render_template('home.html', books=books, value = value, empty_search = empty_search, genre = genre)
    except Exception as e:
        print(e)
        session['Homepage-alert'] = r"Please Enter a Valid Name, Do not enter any of the Following: \\, [ , ]"
        return redirect('/home')
    
@app.route('/process_genre', methods = ['GET', 'POST'])
def genre_select():
    genre = request.form['genre']
    print(genre)
    books = Library("New_Library")

    if genre == "All":
        print("hobba")
        return redirect("/home")
    
    else:
        filtered_books = books_df.books[books_df.books['Genre']== genre]
        books = filtered_books.to_dict('records')
        return render_template('home.html', books=books, empty_search = len(filtered_books) == 0 ,  genre = genre)
        


@app.route('/login', methods=['GET', 'POST'])
def login():
    global logged_in

    if logged_in:
        return render_template('add_book.html')
    
    else:
        if request.method == 'POST':
            username = request.form['username']
            password = request.form['password']
            
            if username in users and users[username] == password:
                logged_in = True
                return redirect(url_for('add_book'))
            else:
                logged_in = False
                return render_template('login.html', alert='Invalid username or password')
        else:
            logged_in = False
            return render_template('login.html')

@app.route('/add_book')
def add_book():
    global logged_in
    if not logged_in:
        return redirect(url_for('login'))
    return render_template('add_book.html', logged_in=True)

@app.route('/about')
def about():
    return render_template("about.html")











@app.route('/upload_details', methods = ["GET", "POST"])
def upload_details():
    global books_df
    if request.method == "POST":
        if request.files:
            
            pdf = request.files["pdf"]
            image = request.files["Thumbnail"]

            # Handle PDF
            if not pdf:
                return render_template("add_book.html", flash = "Please Select a PDF")
            
            print(os.path.join(app.config['books'], pdf.filename))
            pdf.save(os.path.join(app.config['books'], pdf.filename))

            # Handle Image
            if image:
                print(os.path.join(app.config['thumbnails'], image.filename))
                image.save(os.path.join(app.config['thumbnails'], image.filename))
                thumb = image.filename
            else:
                thumb = "unknown.jpeg"
        
            
            name = str(request.form["book_name"]).title()
            if not name:
                return render_template("add_book.html", flash = "Book Name Required")

            author = request.form["author"]
            if not author:
                author = "Unknown"


            id = name[-1:-3:-1]+author[0:2]
            if id in books_df.books['ID'].tolist():
                return "File Already Exists"

            path = "Server/Books/"+pdf.filename
            
            genre = request.form["genre"]

            date = request.form["date"]
            if not date:
                date = 0

            plot = request.form["plot"]
            if not plot:
                plot = "Unknown"

            new_entry_df = Book(name, author, date, path, thumb, genre, plot)
            books_df.add_book(new_entry_df)
            
            books_df.show_books()
            books_df = Library("New_Library")

    return render_template("add_book.html", flash = "Book Added Successfully")




@app.route('/reader/<book_id>')
@app.route('/reader/<book_id>/<last_page>')
def reader(book_id, last_page=None):
    book_row = books_df.books[books_df.books['ID'] == book_id]
    if not book_row.empty:
        book_path = book_row.iloc[0]['Path']
        book_name = book_row.iloc[0]['Name']
        book_author = book_row.iloc[0]['Author']
        if last_page == "undefined":
            last_page = book_row.iloc[0]['Last_page']  # Use last page from .lib file if not provided in URL
        if last_page == None:
            last_page = book_row.iloc[0]['Total_Pages']
        book_plot = book_row.iloc[0]['Plot']

        alert = ""
        if 'Reader-alert' in session:
            alert = session['Reader-alert']
        

        books_df.books.loc[books_df.books['ID'] == book_id, 'Last_page'] = last_page
        pd.to_pickle(books_df.books, "Server/New_Library.lib")
        # print(books_df.books)

        shutil.rmtree("static/Images/")
        last_page_image_path = str(pdf_to_image(book_path, int(last_page), 150))
        return render_template('reader.html', book_id=book_id, last_page_image=last_page_image_path, total_pages =  book_row.iloc[0]['Total_Pages'], last_page=last_page, book_name=book_name, book_author=book_author, books_name=books_df.books['Name'].tolist(), book_plot = book_plot, reader_warning = alert)
    else:
        return "Book not found"

@app.route('/reset', methods=['POST'])
def reset_page():
    # Retrieve the book_id from the form submission
    book_id = request.form.get('book_id')
    
    if book_id:
        # Add code here to reset the page
        # For example:
        # Reset the last page to the initial page
        initial_page = 1
        books_df.books.loc[books_df.books['ID'] == book_id, 'Last_page'] = initial_page
        
        # Redirect to the reader route with the book ID
        return redirect(f"/reader/{book_id}/undefined")
    else:
        # Handle the case when book_id is not provided
        return "Book ID not provided"


@app.route('/fullscreen/<book_id>/<pageno>', methods=['POST', 'GET'])
def fullscreen(book_id, pageno):
    if not pageno:
        pageno = 1
    book_row = books_df.books[books_df.books['ID'] == book_id]
    name = book_row.iloc[0]['Name']
    author = book_row.iloc[0]['Author']
    total = book_row.iloc[0]['Total_Pages']

    # Retrieve the book_id from the form data
    path = books_df.books.loc[books_df.books['ID'] == book_id].iloc[0]['Path']

    last_page_image_path = str(pdf_to_image(path, int(pageno), 150))
    last2_page_image_path = str(pdf_to_image(path, int(pageno)+1, 150))
    books_df.books.loc[books_df.books['ID'] == book_id, 'Last_page'] = pageno


    return render_template('newfullscreen.html', last_page_image_path = last_page_image_path, last2_page_image_path= last2_page_image_path, name=name, author=author, current_page = pageno, next_page = int(pageno)+1, book_id = book_id, total = total)

@app.route('/gotopage', methods=['POST'])
def gotopage():
    page = request.form.get('page')
    print(page)
    book_id = request.form.get('book_id')
    if page == 1:
        page = "undefined"
    pages = books_df.books.loc[books_df.books['ID'] == book_id].iloc[0]['Total_Pages']
    cp = books_df.books.loc[books_df.books['ID'] == book_id].iloc[0]['Last_page']
    

    try:
        int(page)
    except:
        session['Reader_alert'] = "Invalid Page Number"
        return redirect(f"/reader/{book_id}/{cp}")

    if int(page)>int(pages):
        session['Reader-alert'] = "This is the Last Page " + str(pages)
        return redirect(f"/reader/{book_id}/{pages}")
    
    if int(page)<1:
        session['Reader-alert'] = "Invalid Page Number"
        return redirect(f"/reader/{book_id}/1")

    session['Reader-alert'] = ""
    return redirect(f"/reader/{book_id}/{page}")



@app.route('/logout', methods = ['GET', 'POST'])
def logout():
    global logged_in
    logged_in = False
    return redirect('/add_book')


@app.route('/delete_book', methods =['GET', 'POST'])
def delete_book():
    global books_df
    id = request.form.get('id')
    value = books_df.remove_book(id)
    books_df = Library("New_Library")
    print(books_df.books)
    if value == 0:
        return render_template("add_book.html", flash = "Book Not Found")
    else:
        return render_template("add_book.html", flash = "Deleted Successfully")

@app.route('/gotopagefullscreen', methods = ['POST'])
def gotopagefullscreen():
    book_id = request.form.get('id')
    book_row = books_df.books[books_df.books['ID'] == book_id]
    name = book_row.iloc[0]['Name']
    author = book_row.iloc[0]['Author']
    total = book_row.iloc[0]['Total_Pages']
    page = request.form.get('page')
    last_page = book_row.iloc[0]['Last_page']
    path = books_df.books.loc[books_df.books['ID'] == book_id].iloc[0]['Path']
    last_page_image_path = str(pdf_to_image(path, int(last_page), 150))
    last2_page_image_path = str(pdf_to_image(path, int(last_page)+1, 150))

    
    #if Invalid Page Number
    try:
        page = int(page)
        last_page_image_path = str(pdf_to_image(path, int(page), 150))
        last2_page_image_path = str(pdf_to_image(path, int(page)+1, 150))
        books_df.books.loc[books_df.books['ID'] == book_id, 'Last_page'] = page
    except ValueError:
        #Send Warning To Socket
        warning_message = 'Invalid Page Number'
        return render_template('newfullscreen.html', last_page_image_path = last_page_image_path, last2_page_image_path= last2_page_image_path, name=name, author=author, current_page = last_page, next_page = int(last_page)+1, book_id = book_id, total = total, warning = warning_message)




    if int(page) >= int(total):
       last_page_image_path = str(pdf_to_image(path, int(total)-1, 150))
       last2_page_image_path = str(pdf_to_image(path, int(total), 150))
       warning_message = 'We are at the last Page'
       books_df.books.loc[books_df.books['ID'] == book_id, 'Last_page'] = total
       return render_template('newfullscreen.html', last_page_image_path = last_page_image_path, last2_page_image_path= last2_page_image_path, name=name, author=author, current_page = int(total)-1, next_page = int(total), book_id = book_id, total = total, warning = warning_message)
   
   
   
    if int(page) < 1:
        last_page_image_path = str(pdf_to_image(path, 1, 150))
        last2_page_image_path = str(pdf_to_image(path, 2, 150))
        warning_message = 'Invalid page number, We are at the first page.'
        books_df.books.loc[books_df.books['ID'] == book_id, 'Last_page']  = 1
        return render_template('newfullscreen.html', last_page_image_path = last_page_image_path, last2_page_image_path= last2_page_image_path, name=name, author=author, current_page = 1, next_page = 2, book_id = book_id, total = total, warning = warning_message)


    return redirect(f'fullscreen/{book_id}/{page}')




if __name__ == '__main__':
    app.run(debug=True)
