from flask import Flask, render_template, request, redirect, send_file, url_for, jsonify
import pandas as pd
from Backend_Scripts.additional import pdf_to_image
from Backend_Scripts.Basic_Logic import Book, Library  
import os, shutil

app = Flask(__name__)
app.secret_key = 'RI260704'
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
  return render_template('home.html', books = books, genre = "All")

@app.route('/search', methods = ['POST', 'GET'])
def search():
    try:
        genre = "All"
        value = request.form.get("Search-Field", "").replace("[", "").replace("]", "").replace("\\", "")
        keyword = value.lower()
        filtered_books = books_df.books[books_df.books['Name'].str.lower().str.contains(keyword)]
        books = filtered_books.to_dict('records')
        empty_search = len(filtered_books) == 0

        return render_template('home.html', books=books, value = value, empty_search = empty_search, genre = genre)
    except Exception as e:
        print(e)
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


        books_df.books.loc[books_df.books['ID'] == book_id, 'Last_page'] = last_page
        pd.to_pickle(books_df.books, "Server/New_Library.lib")
        print(books_df.books)

        shutil.rmtree("static/Images/")
        last_page_image_path = str(pdf_to_image(book_path, int(last_page), 150))
        return render_template('reader.html', book_id=book_id, last_page_image=last_page_image_path, total_pages =  book_row.iloc[0]['Total_Pages'], last_page=last_page, book_name=book_name, book_author=book_author, books_name=books_df.books['Name'].tolist(), book_plot = book_plot)
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

@app.route('/fullscreen', methods=['POST'])
def fullscreen():
    # Retrieve the book_id from the form data
    book_id = request.form.get('book_id')
    path = books_df.books.loc[books_df.books['ID'] == book_id].iloc[0]['Path']
    page_number = books_df.books.loc[books_df.books['ID'] == book_id].iloc[0]['Last_page']

    # Ensure that the book_id is not None
    if book_id is not None:        
        # Send the PDF file to the browser for display
        url = f"{path}#page={page_number}"
        return send_file(path, mimetype='application/pdf', as_attachment=False)
    else:
        # Handle the case when book_id is not provided
        return "Book ID not provided"

@app.route('/gotopage', methods=['POST'])
def gotopage():
    page = request.form.get('page')
    print(page)
    book_id = request.form.get('book_id')
    if page == 1:
        page = "undefined"
    pages = books_df.books.loc[books_df.books['ID'] == book_id].iloc[0]['Total_Pages']
    if int(page)>int(pages):
        return redirect(f"/reader/{book_id}/{pages}")

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
    

if __name__ == '__main__':
    app.run(debug=True)