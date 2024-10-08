import logging
from datetime import datetime

from flask import Flask

from apps.routes import apps

from flask_cors import CORS

import os

# 获取当前时间
current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
# 创建日志文件夹路径
log_dir = '/data0/refinity_webui/step by step/Refinity-api/logs'
if not os.path.exists(log_dir):
    os.makedirs(log_dir)
log_file = os.path.join(log_dir, f'flask_app_{current_time}.log')
# 配置日志记录器
file_log_handler = logging.FileHandler(log_file)
formatter = logging.Formatter('%(asctime)s %(levelname)s: %(message)s')
file_log_handler.setFormatter(formatter)
logging.getLogger().addHandler(file_log_handler)
logging.getLogger().setLevel(logging.INFO)


app = Flask(__name__)

app.register_blueprint(apps)

app.config['MAX_CONTENT_LENGTH'] = 600 * 1024 * 1024

# 如果 nginx 中配置了 Access-Origin，则这里不需要开启CORS
CORS(app, resources={r"/*": {"origins": "*"}})

if __name__ == '__main__':
    # app.config['DEBUG'] = True
    app.run(host='0.0.0.0', port=5002)