from flask import Flask, render_template, request, redirect, send_file, url_for, jsonify
import pandas as pd
from Backend_Scripts.additional import pdf_to_image
from Backend_Scripts.Basic_Logic import Book, Library  
import os

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
  # Default data for initial render
  books = books_df.books.to_dict('records')
  original_books = books.copy()  # Assuming you want a copy for full data
  search_term = ''  # Initialize empty search term

  if request.method == 'POST':
    # Handle search term
    data = request.get_json()
    search_term = data.get('searchTerm', '').lower()  # Get and lowercase search term

    # Filter books based on search term (if provided)
    if search_term:
      filtered_books = books_df.books[books_df.books['Name'].str.lower().str.contains(search_term)]
      books = filtered_books.to_dict('records')
      print(books)
    return render_template('home.html', books=books, search_term = search_term)  # Pass both variables
  return render_template('home.html', original_books=original_books, search_term = None)


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
            pdf.save(os.path.join(app.config['books'], pdf.filename))
            
            image = request.files["Thumbnail"]
            image.save(os.path.join(app.config['thumbnails'], image.filename))


            thumb = image.filename
            name = request.form["book_name"]
            author = request.form["author"]
            id = name[-1:-3:-1]+author[0:2]

            if id in books_df.books['ID'].tolist():
                return "File Already Exists"

            path = "Server/Books/"+pdf.filename
            genre = request.form["genre"]
            date = request.form["date"]

            new_entry_df = Book(name, author, date, path, thumb, genre)
            books_df.add_book(new_entry_df)
            
            books_df.show_books()
            books_df = Library("Server/New_Library.lib")

    return redirect('/add_book')




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

        books_df.books.loc[books_df.books['ID'] == book_id, 'Last_page'] = last_page
        pd.to_pickle(books_df.books, "Server/New_Library.lib")
        print(books_df.books)

        last_page_image_path = str(pdf_to_image(book_path, int(last_page), 150))
        return render_template('reader.html', book_id=book_id, last_page_image=last_page_image_path, last_page=last_page, book_name=book_name, book_author=book_author, books_name=books_df.books['Name'].tolist())
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





if __name__ == '__main__':
    app.run(debug=True)