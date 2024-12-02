from flask import Flask, render_template, jsonify, request
from pymongo import MongoClient
from datetime import datetime
import os

# MUHAMMAD AFRIZAL RIZKY MAULADANI XII TKJ 3 NO 12
connection_string = 'mongodb+srv://muhammadmauladani:sparta@cluster0.xgv4nwv.mongodb.net/?retryWrites=true&w=majority'
client = MongoClient(connection_string)
db = client.dbsparta 

app = Flask(__name__)

@app.route('/') 
def home():
    return render_template('index.html')

@app.route('/diary', methods=['GET'])
def show_diary():
    articles = list(db.diary.find({}, {'_id': False}))
    return jsonify({'articles': articles})

@app.route('/diary', methods=['POST'])
def save_diary():
    title_receive = request.form.get('title_give')
    content_receive = request.form.get('content_give')
    
    # Mengubah format waktu untuk menghindari karakter yang tidak valid
    today = datetime.now()
    
    file = request.files['file_give']
    
    # Mendapatkan ekstensi file
    extension = file.filename.split('.')[-1]
    
    mytime = today.strftime('%Y-%m-%d-%H-%M-%S')
    
    # Membentuk nama file dengan format yang aman
    filename = f"static/post-{mytime}.{extension}"
    
    # Menyimpan file di lokasi statis
    file.save(filename)
    
    profile = request.files['profile_give']
    extension = profile.filename.split('.')[-1]
    profilename = f'static/profile-{mytime}.{extension}'
    profile.save(profilename)
    
    # Menyimpan data ke dalam MongoDB
    doc = {
        'file': filename,
        'profile': profilename,
        'title': title_receive,
        'content': content_receive
    }

    db.diary.insert_one(doc)
    return jsonify({'message': 'Data was saved!'})

@app.route('/diary/<title>', methods=['DELETE'])
def delete_diary(title):
    # Mencari data di MongoDB berdasarkan judul
    diary_entry = db.diary.find_one({'title': title})
    if diary_entry:
        # Menghapus file gambar dari folder static
        try:
            os.remove(diary_entry['file'])
            os.remove(diary_entry['profile'])
        except Exception as e:
            return jsonify({'message': 'Failed to delete files', 'error': str(e)}), 500
        
        # Menghapus data dari MongoDB
        db.diary.delete_one({'title': title})
        return jsonify({'message': 'Diary entry deleted successfully!'})
    
    return jsonify({'message': 'Entry not found!'}), 404

if __name__ == "__main__":
    app.run('0.0.0.0', port=5000, debug=True)
