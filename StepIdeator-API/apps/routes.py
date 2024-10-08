from datetime import datetime
import json
import logging
import os
from flask import current_app, request, jsonify, Blueprint, url_for
from flask_cors import CORS
import base64
from werkzeug.utils import secure_filename

from apps.paint import handler as paintHandler

from apps.utils import ResponseWrapper, BusinessException, BUSINESS_FAIL

apps = Blueprint("apps", __name__)
CORS(apps)


@apps.route('/ping', methods=['GET', 'POST'])
def index():
    return "pong"

# @apps.route('/info', methods=['GET', 'POST'])
# def re():
#     return "1"

@apps.route('/generate', methods=['GET','POST'])
def generate():
    # print("Start generating ...")
    try:
        print("Start generating ...")
        logging.info("Start generating ...")
        
        if(request):
            print("yes")
            print(request)
            
            logging.info("yes")
            logging.info(request)
            
        else:
            print("No")
            logging.info("No")
            
        designTask = request.json.get('designTask')
        num = int(request.json.get('currentNum'))
        # 所有前端传输来的数据（包含图片）都从prompt中获取
        currentAIStage = request.json.get('currentAIStage')
        selectedTexts =  request.json.get('selectedTexts')
        selectedCanvasRecords = request.json.get('selectedCanvasRecords')
        selectedButtonInfo = request.json.get('selectedButtonInfo')
        username = request.json.get('username')
        currentStage = request.json.get('currentStage')
        
        logging.info(selectedButtonInfo)
        logging.info(f"Received data: designTask={designTask}, num={num}, currentAIStage={currentAIStage}, username={username}, currentStage={currentStage}")
        
                
        if selectedCanvasRecords!=[]:
            # 将base64编码的图片保存到一个单独的文件中，而不是直接记录到日志中
            current_time = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
            large_data_dir = '/data0/refinity_webui/step by step/Refinity-api/large_data'
            os.makedirs(large_data_dir, exist_ok=True)  # 确保目录存在
            base64_filename = f'canvas_{current_time}.txt'
            base64_filepath = os.path.join(large_data_dir, base64_filename)
            
            with open('/data0/refinity_webui/step by step/Refinity-api/static/canvas.png', 'rb') as image_file:
                encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
                selectedCanvasRecords=f"data:image/png;base64,{encoded_string}"
                
            # 将编码字符串保存到文件
            with open(base64_filepath, 'w') as file:
                file.write(selectedCanvasRecords)
                
            logging.info(f'选中的画布base64已保存到文件: {base64_filepath}')
        
        # selectedCanvasRecords = []
        
        print(selectedButtonInfo)
        print(currentStage)
        
        response_data  = paintHandler.handle_request(num,designTask,currentAIStage,selectedCanvasRecords,selectedTexts,selectedButtonInfo,username,currentStage)
        
        logging.info(f"Handle complete: {response_data}")
        logging.info("handle ok!")
        
        print("handle ok!")
        # if app_id == 0:
        #     response_data = paintHandler.handle_request(type_, prompts)
        # else:
        #     raise BusinessException(message="应用不存在")
        # print(jsonify(ResponseWrapper.success(data=response_data)))
        return jsonify(ResponseWrapper.success(data=response_data))

        # 将图像数据发送到前端
        # return jsonify(ResponseWrapper.success({'image': image_base64}))
    except BusinessException as be:
        return jsonify(ResponseWrapper.fail(code=be.code, message=be.message))
    except Exception as e:
        return jsonify(ResponseWrapper.fail(code=BUSINESS_FAIL, message=str(e)))

@apps.route('/paint/save', methods=['POST'])
def paintSave():
    try:
        username = request.json.get('username')
        data = request.json.get('data')
        print(username)
        print(data)
        # paintLogic.save(username, data)
        return jsonify(ResponseWrapper.success())
    except BusinessException as be:
        return jsonify(ResponseWrapper.fail(code=be.code, message=be.message))
    except Exception as e:
        return jsonify(ResponseWrapper.fail(code=BUSINESS_FAIL, message=str(e)))
    
@apps.route('/paint/start', methods=['POST'])
def paintStart():
    try:
        username = request.json.get('username')
        # response_data = paintLogic.start(username)
        # print(response_data)
        return jsonify(ResponseWrapper.success(data=username))
    except BusinessException as be:
        return jsonify(ResponseWrapper.fail(code=be.code, message=be.message))
    except Exception as e:
        return jsonify(ResponseWrapper.fail(code=BUSINESS_FAIL, message=str(e)))
    
@apps.route('/timeRecord', methods=['POST'])
def handle_time_records():
    data = request.get_json()  # 获取 JSON 数据
    if not data:
        return jsonify({'success': False, 'message': 'No data provided'}), 400

    # 定义要保存数据的文件路径
    file_path = os.path.join('timing_records', f"{data.get('username')}_timing_records.json")
    
    # 确保 data 目录存在
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    # 保存数据到文件
    try:
        with open(file_path, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)
        return jsonify({'success': True, 'message': 'Timing records saved successfully'})
    except IOError as e:
        return jsonify({'success': False, 'message': 'Failed to save data'}), 500


    
@apps.route('/upload', methods=['POST'])
def upload_file():
    file = request.files['file']
    if file:
        filename = secure_filename(file.filename)
        
        # 定义要保存数据的文件路径
        file_path = os.path.join('static', filename)
        # 确保 data 目录存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        file.save(file_path)  # 保存文件到静态目录

        # 生成访问文件的 URL
        file_url = url_for('static', filename=filename, _external=True)
        print("url:", file_path)
        print("handle ok!")
        return jsonify({'url': file_url})
    else:
        return jsonify({'error': 'No file provided'}), 400


@apps.route('/uploadImage', methods=['POST'])
def upload_file_baseline():    
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'}), 400
    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'}), 400
    if file:
        # 获取当前时间并格式化为字符串
        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        
        # 获取安全的文件名并在其前面加上时间戳
        filename = secure_filename(file.filename)
        unique_filename = f"{timestamp}_{filename}"
        
        # 定义要保存画布图片的文件路径，确保它位于static目录下
        file_path = os.path.join(current_app.static_folder, 'baseline_canvas_upload', unique_filename)
        
        # 确保文件夹存在
        os.makedirs(os.path.dirname(file_path), exist_ok=True)

        # 保存文件到指定目录
        file.save(file_path)

        # 构造文件访问路径
        filepath = url_for('static', filename=os.path.join('baseline_canvas_upload', unique_filename), _external=True)

        print("handle ok!")
        print('path', filepath)
        
        return jsonify({'success': True, 'url': filepath})
    else:
        return jsonify({'success': False, 'error': 'No file provided'}), 400