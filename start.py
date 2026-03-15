from app import app
import logging

# 启用日志
logging.basicConfig(level=logging.INFO)

if __name__ == '__main__':
    print("=" * 50)
    print("Starting Flask server...")
    print("=" * 50)
    app.run(host='127.0.0.1', port=5000, debug=False, use_reloader=False)
