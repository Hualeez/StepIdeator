from pymongo import MongoClient
import base64
from io import BytesIO
from PIL import Image
import os

import datetime

MONGO_HOST = 'mongodb://127.0.0.1:27017/'
MONGO_DB = 'Refinity'

mongo_client = MongoClient(MONGO_HOST)
mongo_db = mongo_client[MONGO_DB]
mongo_users_collection = mongo_db['users']

current_time = datetime.datetime.now()
formatted_time = current_time.strftime("%Y-%m-%d_%H-%M-%S")

def export_images(usernames, folder_name="images"):  
    # 创建子文件夹
    folder_name = folder_name + '-' + formatted_time
    if not os.path.exists(folder_name):
        os.makedirs(folder_name)
    
    if usernames.lower() == 'all':
        user_cursor = mongo_users_collection.find()
    else:
        # 分割用户名并查询
        username_list = usernames.split()
        user_cursor = mongo_users_collection.find({"username": {"$in": username_list}})
        
    for user in user_cursor:
        username = user["username"]
        # print(username)
        # 从用户数据中提取并保存图片数据
        stages = ["DesignBrief", "Sketch", "ModelImage","Rendering"]
        scheme_types = ['设计摘要', '草图', '模型图', '渲染图']
        for i, stage in enumerate(stages):
            schemes = user[stage]
            scheme_type = scheme_types[i]
            for i, scheme in enumerate(schemes):
                canvas_image_b64 = scheme.get("canvasImage", "")
                if canvas_image_b64:
                    # 解码Base64图片数据
                    image_data = base64.b64decode(canvas_image_b64.split(",")[-1])
                    image = Image.open(BytesIO(image_data))
                    # 保存图片
                    file_name = f"{username}-{scheme_type}-{i}.png"
                    file_path = os.path.join(folder_name, file_name)
                    image.save(file_path)
                    print(f"保存图片到 {file_name}")

usernames = input("输入用户信息（用空格隔开），输入'all'代表获取所有用户：")
export_images(usernames)