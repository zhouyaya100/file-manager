from app import app

if __name__ == '__main__':
    print("启动服务器...")
    app.run(host='127.0.0.1', port=5000, debug=False)
