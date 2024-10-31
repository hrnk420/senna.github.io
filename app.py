from flask import Flask, render_template, request, redirect, send_file
from flask_socketio import SocketIO
import sqlite3
import qrcode
import os

app = Flask(__name__)
socketio = SocketIO(app)

def init_db():
    # staticディレクトリを作成
    if not os.path.exists('static'):
        os.makedirs('static')
    
    # データベースを初期化
    with sqlite3.connect('database.db') as conn:
        conn.execute('CREATE TABLE IF NOT EXISTS memos (id INTEGER PRIMARY KEY, content TEXT)')
        conn.commit()

@app.route('/')
def index():
    # データベースからメモを取得
    with sqlite3.connect('database.db') as conn:
        cur = conn.cursor()
        cur.execute('SELECT * FROM memos')
        memos = cur.fetchall()
    return render_template('index.html', memos=memos)

@app.route('/add', methods=['POST'])
def add_memo():
    # メモを追加
    content = request.form['content']
    with sqlite3.connect('database.db') as conn:
        conn.execute('INSERT INTO memos (content) VALUES (?)', (content,))
        conn.commit()
    socketio.emit('new_memo', {'content': content})
    return redirect('/')

@app.route('/delete/<int:id>', methods=['POST'])
def delete_memo(id):
    # メモを削除
    with sqlite3.connect('database.db') as conn:
        conn.execute('DELETE FROM memos WHERE id = ?', (id,))
        conn.commit()
    return redirect('/')

@app.route('/qr')
def qr_code():
    # QRコードを生成
    url = request.host_url  # アプリのURLを取得
    qr = qrcode.make(url)   # QRコードを生成
    
    # QRコードの保存パス
    qr_path = os.path.join(os.getcwd(), 'static', 'qr.png')
    qr.save(qr_path)  # QRコードを保存
    return send_file(qr_path, mimetype='image/png')

if __name__ == '__main__':
    init_db()
    socketio.run(app, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)), debug=True)  # SocketIOでアプリを実行
