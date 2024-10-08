from apps.utils import BusinessException, BUSINESS_FAIL

# from apps.paint.creatives import DesignCreative
from agent.sd import sd_pool
from agent.gpt import gpt_pool
import base64
import os
import json
from datetime import datetime
from PIL import Image
from io import BytesIO
import subprocess
import glob


from settings import prompts

from concurrent.futures import ThreadPoolExecutor

from pymongo import MongoClient
import config

mongo_client = MongoClient(config.MONGO_HOST)
mongo_db = mongo_client[config.MONGO_DB]
mongo_users_collection = mongo_db["users"]


def filename_to_base64(filename):
    with open(filename, "rb") as fh:
        return base64.b64encode(fh.read())


def parse_generated(generated_text):
    return generated_text.strip().split("#")


def generate_prompts(template: str, **input):
    try:
        return template.format(**input)
    except KeyError as e:
        print(f"Missing a required placeholder in the template: {e}")
        raise
    except Exception as e:
        print(f"An error occurred while generating the prompt: {e}")
        raise


def imageSave(
    username,
    image_data,
    i=0,
    filepath="/data0/refinity_webui/step by step/Demo/public/images",
):
    # filepath = '/data0/refinity_webui/step by step/Demo/public/images'  # 更改为您的文件路径
    current_time = datetime.now()
    formatted_time = current_time.strftime("%Y%m%d%H%M%S")
    filename = os.path.join(
        filepath, f"{formatted_time}_{username}_out_{i}.png"
    )  # 或者其他你想要的文件名和格式

    # 将解码后的图像数据写入文件
    with open(filename, "wb") as file:
        # print("img data:")
        # print(image_data)
        file.write(image_data)

    print(f"Image saved as {filename}")

    image_filename = f"{formatted_time}_{username}_out_{i}.png"
    return image_filename


def transparent_to_white_bg(base64_str):
    # 确保base64字符串是干净的
    def clean_base64(b64_str):
        # 去除可能存在的base64数据URL前缀
        if "," in b64_str:
            b64_str = b64_str.split(",")[1]
        return b64_str

    # 解码base64字符串到图像
    def base64_to_image(b64_str):
        b64_str = clean_base64(b64_str)  # 清洁base64字符串
        image_data = base64.b64decode(b64_str)
        image = Image.open(BytesIO(image_data))
        return image

    # 将透明背景图像转换为白色背景
    def convert_to_white_background(image):
        white_background = Image.new("RGBA", image.size, "WHITE")  # 创建白色背景
        white_background.paste(image, mask=image.split()[3])  # 使用alpha层作为蒙版
        return white_background.convert("RGB")  # 转换为不带透明通道的RGB格式

    # 将图像转换为base64字符串
    def image_to_base64(img):
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        return base64.b64encode(buffered.getvalue()).decode("utf-8")

    # 主要转换流程
    original_image = base64_to_image(base64_str)  # 将base64字符串转换为图像
    image_with_white_bg = convert_to_white_background(original_image)  # 转换背景
    return image_to_base64(image_with_white_bg)


# 1-1 完成/测试
def designBrief_createNew(json_in):
    print("[Process] In designBrief_createNew")
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        userInput_list = json_in.get("selectedTexts")
        userInput = ""
        for usertext in userInput_list:
            userInput = userInput + "'" + usertext + "'"

        # prompt_designBrief_createNew = "设计任务：{designTask}，数量：{num}，用户输入：{userInput}"
        template_in = prompts.prompt_designBrief_createNew
        ret = {}
        for i in range(num):
            gpt_task = {
                "messages": generate_prompts(
                    template_in,
                    designTask=designTask,
                    userInput=userInput,  # 这里传递真实的用户输入
                )
            }
            products = gpt_pool.chat(gpt_task)["text"]
            ret[i] = products.replace("```json\n", "").replace("```", "")
        print(ret)
        return ret
    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 1-2 完成/测试
def designBrief_refine(json_in):
    print("[Process] In designBrief_refine")
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        userInput_list = json_in.get("selectedTexts")
        userInput = ""
        for usertext in userInput_list:
            userInput = userInput + "'" + usertext + "'"

        template_in = prompts.prompt_designBrief_refine
        ret = {}
        for i in range(num):
            gpt_task = {
                "messages": generate_prompts(
                    template_in,
                    designTask=designTask,
                    userInput=userInput,  # 这里传递真实的用户输入
                )
            }
            products = gpt_pool.chat(gpt_task)["text"]
            ret[i] = products.replace("```json\n", "").replace("```", "")
        print(ret)
        return ret
    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 1-3 完成/测试
def designBrief_extend(json_in):
    print("[Process] In designBrief_extend")
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        userInput_list = json_in.get("selectedTexts")
        if userInput_list == None:
            raise BusinessException(BUSINESS_FAIL, "用户选择文本缺失")
        userInput = ""
        for usertext in userInput_list:
            userInput = userInput + "'" + usertext + "'"

        template_in = prompts.prompt_designBrief_extend
        ret = {}
        for i in range(num):
            gpt_task = {
                "messages": generate_prompts(
                    template_in,
                    designTask=designTask,
                    userInput=userInput,  # 这里传递真实的用户输入
                )
            }
            products = gpt_pool.chat(gpt_task)["text"]
            ret[i] = products.replace("```json\n", "").replace("```", "")
        print(ret)
        return ret
    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 2-1 完成/测试/校对效果 text2image_RV
def sketch_createNew(json_in):
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        username = json_in.get("username")
        gpt_task = {
            "messages": generate_prompts(
                prompts.prompt_mainbody,
                designTask=designTask
                )
        }
        # mainbody = gpt_pool.chat(gpt_task)["text"]
        mainbody = 'agricultural drone'

        # Step 4: 并行生成 SD 图片
        print(mainbody)
        sd_tasks = []
        prompts_pos = generate_prompts(
            prompts.prompt_sketchGeneration_createNew_pos, mainbody=mainbody
        )
        prompts_neg = prompts.prompt_sketchGeneration_createNew_neg
        for i in range(num):
            task = {
                "index": i,
                "prompt": prompts_pos,
                "task_type": "sketchGeneration",
                "negative_prompt": prompts_neg,
                "options": {
                    "Model": "realisticVisionV60B1_v60B1VAE",
                    "width": 512,
                    "height": 512,
                    "sampler_name": "Euler a",
                    "steps": 20,
                },
            }
            sd_tasks.append(task)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(sd_pool.text2Image_RV, task) for task in sd_tasks]
            images = [future.result() for future in futures]

        if len(images) != num:
            raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

        count = len(images)

        # 初始化返回的路径字典
        web_paths = {}

        for i in range(count):
            base64_string = images[i]["image"]
            image_data = base64.b64decode(base64_string)

            image_filename = imageSave(username, image_data, i)

            web_paths[i] = f"/images/{image_filename}"
            print(f"Web accessible path: {web_paths[i]}")

        return {"paths": web_paths}

    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 2-2 完成/测试/校对效果 text2image_RV
def sketch_refine(json_in):
    print("in sketch refine")
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        userInput_list = json_in.get("selectedTexts")
        userInput = ""
        for usertext in userInput_list:
            userInput = userInput + "'" + usertext + "'"
        username = json_in.get("username")
        # selectedCanvasRecords = json_in.get('selectedCanvasRecords')
        ret = {}
        # if selectedCanvasRecords:
        prompt_sketch_refine = generate_prompts(
            prompts.prompt_sketch_refine, designTask=designTask, userInput=userInput
        )
        gpt_task = {
            "messages": prompt_sketch_refine,
        }
        products = (
            gpt_pool.chat(gpt_task)["text"].replace("```json\n", "").replace("```", "")
        )
        ret[0] = products
        # return products
        prompt_sketch_refine_sd = generate_prompts(
            prompts.prompt_sketch_refine_sd, description=products
        )

        gpt_task = {"messages": prompt_sketch_refine_sd}

        sd_prompt = gpt_pool.chat(gpt_task)["text"]
        cleaned_prompt_sd = sd_prompt.replace("```json\n", "").replace("```", "")
        # print(cleaned_prompt_sd)
        sd_prompt_phase = json.loads(cleaned_prompt_sd)["prompt"]
        print(sd_prompt_phase)
        # else:
        # sd_prompt_phase = ''
        # ret[0]=''
        # return sd_prompt
        gpt_task = {
                "messages": generate_prompts(
                prompts.prompt_mainbody,
                designTask=designTask
            )
        }
        # mainbody = gpt_pool.chat(gpt_task)["text"]
        mainbody = 'agricultural drone'
        
        #     # Step 4: 并行生成 SD 图片
        #     # print(mainbody)
        sd_tasks = []
        prompts_pos = generate_prompts(
            prompts.prompt_sketch_refine_sd_pos,
            mainbody=mainbody,
            sd_prompt_in=sd_prompt_phase,
        )
        prompts_neg = prompts.prompt_sketch_refine_sd_neg

        for i in range(num):
            task = {
                "index": i,
                "prompt": prompts_pos,
                "task_type": "sketchRefine",
                "negative_prompt": prompts_neg,
                "options": {
                    "Model": "realisticVisionV60B1_v60B1VAE",
                    "width": 512,
                    "height": 512,
                    "sampler_name": "Euler a",
                    "steps": 20,
                },
            }
            sd_tasks.append(task)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(sd_pool.text2Image_RV, task) for task in sd_tasks]
            images = [future.result() for future in futures]

        if len(images) != num:
            raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

        count = len(images)

        # 初始化返回的路径字典
        web_paths = {}

        for i in range(count):
            base64_string = images[i]["image"]
            # print(type(base64_string))
            image_data = base64.b64decode(base64_string)

            image_filename = imageSave(username, image_data, i)

            web_paths[i] = f"/images/{image_filename}"
            print(f"Web accessible path: {web_paths[i]}")

        return [ret, web_paths]

    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 2-3 完成/测试/校对效果 controlnet_text2image_RV
def sketch_extend(json_in):
    designTask = json_in.get("designTask")
    if not designTask:
        raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
    num = json_in.get("num")
    if not num:
        raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
    userInput_list = json_in.get("selectedTexts")
    userInput = ""
    for usertext in userInput_list:
        userInput = userInput + "'" + usertext + "'"
    username = json_in.get("username")
    selectedCanvasRecords = json_in.get("selectedCanvasRecords")
    if not selectedCanvasRecords:
        raise BusinessException(BUSINESS_FAIL, "参考图像缺失")

    gpt_task = {
            "messages": generate_prompts(
            prompts.prompt_mainbody,
            designTask=designTask
        )
    }
    # mainbody = gpt_pool.chat(gpt_task)["text"]
    mainbody = 'agricultural drone'
    
    prompts_pos = generate_prompts(
        prompts.prompt_sketch_extend_sd_pos, mainbody=mainbody
    )
    prompts_neg = prompts.prompt_sketch_extend_sd_neg

    sd_tasks = []

    for i in range(num):
        task = {
            "index": i,
            "prompt": prompts_pos,
            "task_type": "sketchExtend",
            "negative_prompt": prompts_neg,
            "images": selectedCanvasRecords,
            "options": {
                "Model": "realisticVisionV60B1_v60B1VAE",
                "width": 512,
                "height": 512,
                "sampler_name": "Euler a",
                "steps": 20,
                "cfg_scale": 7,
                "alwayson_scripts": {
                    "controlnet": {
                        "args": [
                            {
                                "enabled": True,
                                "module": "pidinet_scribble",
                                "model": "control_v11p_sd15_scribble",
                                "weight": 1.0,
                                "image": selectedCanvasRecords,
                                "resize_mode": 1,
                                "lowvram": False,
                                "processor_res": 512,
                                "threshold_a": -1,
                                "threshold_b": -1,
                                "guidance_start": 0.0,
                                "guidance_end": 1.0,
                                "control_mode": 0,
                                "pixel_perfect": False,
                            }
                        ]
                    }
                },
            },
        }
        sd_tasks.append(task)

    with ThreadPoolExecutor() as executor:
        futures = [
            executor.submit(sd_pool.controlnet_text2image_RV, task) for task in sd_tasks
        ]
        images = [future.result() for future in futures]

    if len(images) != num:
        raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

    count = len(images)
    web_paths = {}

    for i in range(count):
        base64_string = images[i]["image"]
        # print(type(base64_string))
        image_data = base64.b64decode(base64_string)

        image_filename = imageSave(username, image_data, i)

        web_paths[i] = f"/images/{image_filename}"
        print(f"Web accessible path: {web_paths[i]}")

    return {"paths": web_paths}


# 2-4  完成/测试/校对效果 text2image_RV controlnet_text2image_RV
def sketch_toSketch(json_in):
    print("[Process] In sketch_toSketch")
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        userInput_list = json_in.get("selectedTexts")
        userInput = ""
        for usertext in userInput_list:
            userInput = userInput + "'" + usertext + "'"
        username = json_in.get("username")
        selectedCanvasRecords = json_in.get("selectedCanvasRecords")

        # print(selectedCanvasRecords)

        if not selectedCanvasRecords and not userInput:
            raise BusinessException(BUSINESS_FAIL, "参考图像或文本缺失")

        gpt_task = {
            "messages": generate_prompts(
                prompts.prompt_mainbody,
                designTask=designTask
                )
        }
        # mainbody = gpt_pool.chat(gpt_task)["text"]
        mainbody = 'agricultural drone'
        print(mainbody)

        if not selectedCanvasRecords:
            print("No selected canvas")
            sd_tasks = []
            prompts_pos = generate_prompts(
                prompts.prompt_sketch_toSketch_sd_pos_1, mainbody=mainbody
            )
            prompts_neg = prompts.prompt_sketch_toSketch_sd_neg_1
            for i in range(num):
                task = {
                    "index": i,
                    "prompt": prompts_pos,
                    "task_type": "sketchtoSketch",
                    "negative_prompt": prompts_neg,
                    "options": {
                        "Model": "realisticVisionV60B1_v60B1VAE",
                        "width": 512,
                        "height": 512,
                        "sampler_name": "Euler a",
                        "steps": 20,
                    },
                }

                sd_tasks.append(task)

            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(sd_pool.text2Image_RV, task) for task in sd_tasks
                ]
                images = [future.result() for future in futures]
            if len(images) != num:
                raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

            count = len(images)
            web_paths = {}
            for i in range(count):
                base64_string = images[i]["image"]
                # print(type(base64_string))
                image_data = base64.b64decode(base64_string)

                image_filename = imageSave(username, image_data, i)

                web_paths[i] = f"/images/{image_filename}"
                print(f"Web accessible path: {web_paths[i]}")

            return {"paths": web_paths}
        else:
            # mainbody = gpt_pool.chat(gpt_task)["text"]
            mainbody = 'agricultural drone'
            
            print(mainbody)
            prompts_pos = generate_prompts(
                prompts.prompt_sketch_toSketch_sd_pos_2, mainbody=mainbody
            )
            prompts_neg = prompts.prompt_sketch_toSketch_sd_neg_2
            task = {
                "index": 0,
                "task_type": "sketchtoSketch_sam",
                "mainbody": mainbody,
                "src_img_base64": selectedCanvasRecords,
            }
            sd_ret = sd_pool.bgremove(task)
            mask = sd_ret["mask"]
            masked_image = sd_ret["masked_image"]

            buffer = BytesIO()
            # 保存图像到字节流，这里以PNG格式为例
            masked_image.save(buffer, format="PNG")
            # 获取字节流的内容
            img_byte = buffer.getvalue()
            # 将字节数据转换为base64字符串
            base64_string = base64.b64encode(img_byte).decode("utf-8")
            # image_data = base64.b64decode(base64_string)

            # image_filename = imageSave(username,image_data,0)

            image_data_wbg_string = transparent_to_white_bg(base64_string)

            image_data_wbg = base64.b64decode(image_data_wbg_string)

            image_filename = imageSave(username, image_data_wbg, 0)

            # web_paths = f'/images/{image_filename}'
            # print(f"Web accessible path: {web_paths}")
            # paths = {}
            # paths[0]=web_paths

            sd_tasks = []
            for i in range(num):
                task = {
                    "index": i,
                    "prompt": prompts_pos,
                    "task_type": "sketchtoSketch_sd",
                    "negative_prompt": prompts_neg,
                    "options": {
                        "Model": "realisticVisionV60B1_v60B1VAE",
                        "width": 512,
                        "height": 512,
                        "sampler_name": "Euler a",
                        "steps": 20,
                        "denoising_strength": 0.75,
                        "cfg_scale": 7,
                        "alwayson_scripts": {
                            "controlnet": {
                                "args": [
                                    {
                                        "enabled": True,
                                        "module": "lineart",
                                        "model": "control_v11p_sd15_lineart",
                                        "weight": 1.0,
                                        "image": image_data_wbg_string,
                                        "resize_mode": "Crop and Resize",
                                        "processor_res": 512,
                                        "guidance_start": 0.0,
                                        "guidance_end": 1.0,
                                        "control_mode": 0,
                                        "pixel_perfect": False,
                                    }
                                ]
                            }
                        },
                    },
                }

                sd_tasks.append(task)

            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(sd_pool.controlnet_text2image_RV, task)
                    for task in sd_tasks
                ]
                images = [future.result() for future in futures]
            if len(images) != num:
                raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

            count = len(images)
            web_paths = {}
            for i in range(count):
                base64_string = images[i]["image"]
                # print(type(base64_string))
                image_data = base64.b64decode(base64_string)

                image_filename = imageSave(username, image_data, i)

                web_paths[i] = f"/images/{image_filename}"
                print(f"Web accessible path: {web_paths[i]}")

            return {"paths": web_paths}
            # return {"paths": paths}

    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 3-1 完成/测试/校对效果 text2Image_V2
def model_createNew(json_in):
    print("[Process] In model_createNew")
    try:

        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        username = json_in.get("username")
        userInput_list = json_in.get("selectedTexts")
        userInput = ""
        for usertext in userInput_list:
            userInput = userInput + "'" + usertext + "'"
        username = json_in.get("username")
        gpt_task = {
            "messages": generate_prompts(
            prompts.prompt_mainbody,
            designTask=designTask
            )
        }
        # mainbody = gpt_pool.chat(gpt_task)["text"]
        mainbody = 'agricultural drone'
        
        # Step 4: 并行生成 SD 图片
        print(mainbody)
        sd_tasks = []
        prompts_pos = generate_prompts(
            prompts.prompt_model_createNew_sd_pos, mainbody=mainbody
        )
        prompts_neg = prompts.prompt_model_createNew_sd_neg

        for i in range(num):
            task = {
                "index": i,
                "prompt": prompts_pos,
                "task_type": "modelCreateNew",
                "negative_prompt": prompts_neg,
                "options": {
                    "Model": "v2-1_512-ema-pruned",
                    "width": 512,
                    "height": 512,
                    "sampler_name": "Euler a",
                    "steps": 20,
                    "cfg_scale": 7,
                },
            }
            sd_tasks.append(task)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(sd_pool.text2Image_V2, task) for task in sd_tasks]
            images = [future.result() for future in futures]

        if len(images) != num:
            raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

        count = len(images)
        web_paths = {}

        for i in range(count):
            base64_string = images[i]["image"]
            # print(type(base64_string))
            image_data = base64.b64decode(base64_string)

            image_filename = imageSave(username, image_data, i)

            web_paths[i] = f"/images/{image_filename}"
            print(f"Web accessible path: {web_paths[i]}")

        return {"paths": web_paths}

    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 3-2 wonder3d/测试/校对效果
def model_multiView(json_in):

    print("[Process] In model_multiView")

    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        userInput_list = json_in.get("selectedTexts")
        userInput = ""
        for usertext in userInput_list:
            userInput = userInput + "'" + usertext + "'"
        username = json_in.get("username")
        selectedCanvasRecords = json_in.get("selectedCanvasRecords")

        # print(selectedCanvasRecords)

        if not selectedCanvasRecords and not userInput:
            raise BusinessException(BUSINESS_FAIL, "参考图像或文本缺失")

        gpt_task = {
            "messages": generate_prompts(
                "Write a directive to summarize the main object based on '{designTask}' and organize adjectives based on '{userInput_list}' in English. The output should be in a concise format, combining both the main object and the descriptive adjectives into a single phrase.For example: 'modular, detachable drone'".format(
                    designTask=designTask, userInput_list=userInput_list
                )
            )
        }
        # mainbody = gpt_pool.chat(gpt_task)["text"]
        mainbody = 'agricultural drone'
        print(mainbody)

        task = {
            "index": 0,
            "task_type": "sketchtoSketch_sam",
            "mainbody": mainbody,
            "src_img_base64": selectedCanvasRecords,
        }
        sd_ret = sd_pool.bgremove(task)
        mask = sd_ret["mask"]
        masked_image = sd_ret["masked_image"]

        buffer = BytesIO()
        # 保存图像到字节流，这里以PNG格式为例
        masked_image.save(buffer, format="PNG")
        # 获取字节流的内容
        img_byte = buffer.getvalue()
        # 将字节数据转换为base64字符串
        base64_string = base64.b64encode(img_byte).decode("utf-8")

        image_data = base64.b64decode(base64_string)
        # 创建一个字节流（BytesIO对象）来存储PNG图像数据
        image = Image.open(BytesIO(image_data))
        # 指定要保存图像的路径和文件名

        current_time = datetime.now()
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")

        img_name = f"{formatted_time}_{username}_out_sam"
        file_path = f"/data0/lcy/Wonder3D/example_images/" + img_name + ".png"
        image.save(file_path)
        print(f"透明背景图像已保存到：{file_path}")

        # 执行命令并捕获输出
        conda_env_name = "wonder3d"

        # 构建用于激活conda环境并获取当前激活的环境名称的命令
        # 注意：这里使用的是bash shell; 如果你使用的是其他shell, 可能需要修改这部分
        command = f"""
        source $(conda info --base)/etc/profile.d/conda.sh
        conda activate {conda_env_name}
        cd /data0/lcy/Wonder3D
        accelerate launch --config_file 1gpu.yaml test_mvdiffusion_seq.py  --config configs/mvdiffusion-joint-ortho-6views.yaml validation_dataset.root_dir=./example_images   validation_dataset.filepaths=['{img_name}.png'] save_dir=./outputs
        """

        # 执行命令
        bash_ret = subprocess.run(
            ["bash", "-c", command], capture_output=True, text=True
        )

        # 输出当前激活的环境名称
        # print("当前激活的conda环境名称:", result.stdout.strip())

        # img_name = '20240304133233_123_out_sam'

        folder_path = f"/data0/lcy/Wonder3D/outputs/cropsize-192-cfg1.0/{img_name}"
        image_paths = glob.glob(f"{folder_path}/normals_*.png")
        web_paths = {}

        for i in range(len(image_paths)):
            with open(image_paths[i], "rb") as image_file:
                # 读取图像数据
                image_data = image_file.read()
                # 将图像数据转换为Base64字符串
                base64_string = base64.b64encode(image_data).decode("utf-8")
                image_data = base64.b64decode(base64_string)

            image_filename = imageSave(username, image_data, i)

            web_paths[i] = f"/images/{image_filename}"

            # web_paths[i] = image_paths[i]
            print(f"Web accessible path: {web_paths[i]}")
        # print(image_paths)

        return [web_paths]
    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 3-4 完成/测试/校对效果 controlnet_text2image_RV controlnet_text2image_V15
def model_toModel(json_in):
    print("[Process] In model_toModel")
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        userInput_list = json_in.get("selectedTexts")
        userInput = ""
        for usertext in userInput_list:
            userInput = userInput + "'" + usertext + "'"
        username = json_in.get("username")
        selectedCanvasRecords = json_in.get("selectedCanvasRecords")
        userStage = json_in.get("userStage")

        if not selectedCanvasRecords and not userInput:
            raise BusinessException(BUSINESS_FAIL, "参考图像或文本缺失")
        if not selectedCanvasRecords:
            new_json_in = {
                "designTask": designTask,
                "num": num,
                "username": username,
                "selectedTexts": userInput_list,
            }
            return model_createNew(new_json_in)

        gpt_task = {
            "messages": generate_prompts(
                prompts.prompt_mainbody,
                designTask=designTask
                )
        }
        # mainbody = gpt_pool.chat(gpt_task)["text"]
        mainbody = 'agricultural drone'
        
        # Step 4: 并行生成 SD 图片
        print(mainbody)
        print(userStage)
        if userStage == "草图的环境":
            print(1)

            sd_tasks = []
            prompts_pos = generate_prompts(
                prompts.prompt_model_toModel_sd_pos_1, mainbody=mainbody
            )
            prompts_neg = prompts.prompt_model_toModel_sd_neg_1

            for i in range(num):
                task = {
                    "index": i,
                    "prompt": prompts_pos,
                    "task_type": "modeltoModel",
                    "negative_prompt": prompts_neg,
                    "options": {
                        "Model": "v1-5-pruned-emaonly",
                        "width": 512,
                        "height": 512,
                        "sampler_name": "Euler a",
                        "steps": 20,
                        "cfg_scale": 7,
                        "alwayson_scripts": {
                            "controlnet": {
                                "args": [
                                    {
                                        "enabled": True,
                                        "module": "lineart_standard",
                                        # "model": "control_v11p_sd15_softedge [a8575a2a]",
                                        "model": "control_v11p_sd15_lineart",
                                        "weight": 1.0,
                                        # "image": self.read_image(),
                                        "image": selectedCanvasRecords,
                                        "resize_mode": 1,
                                        "lowvram": False,
                                        "processor_res": 64,
                                        "threshold_a": 64,
                                        "threshold_b": 64,
                                        "guidance_start": 0.0,
                                        "guidance_end": 1.0,
                                        "control_mode": 0,
                                        "pixel_perfect": True,
                                    }
                                ]
                            }
                        },
                    },
                }
                sd_tasks.append(task)

            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(sd_pool.controlnet_text2image_RV, task)
                    for task in sd_tasks
                ]
                images = [future.result() for future in futures]

            if len(images) != num:
                raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

            count = len(images)
            web_paths = {}

            for i in range(count):
                base64_string = images[i]["image"]
                # print(type(base64_string))
                image_data = base64.b64decode(base64_string)

                image_filename = imageSave(username, image_data, i)

                web_paths[i] = f"/images/{image_filename}"
                print(f"Web accessible path: {web_paths[i]}")
            return {"paths": web_paths}

        elif userStage == "场景与产品渲染图的环境":
            print(2)

            sd_tasks = []
            prompts_pos = generate_prompts(
                prompts.prompt_model_toModel_sd_pos_2, mainbody=mainbody
            )
            prompts_neg = prompts.prompt_model_toModel_sd_neg_2

            for i in range(num):
                task = {
                    "index": i,
                    "prompt": prompts_pos,
                    "task_type": "modeltoModel",
                    "negative_prompt": prompts_neg,
                    "options": {
                        "Model": "v1-5-pruned-emaonly",
                        "width": 512,
                        "height": 512,
                        "sampler_name": "Euler a",
                        "steps": 20,
                        "cfg_scale": 7,
                        "alwayson_scripts": {
                            "controlnet": {
                                "args": [
                                    {
                                        "enabled": True,
                                        "module": "depth",
                                        "model": "control_v11f1p_sd15_depth",
                                        "weight": 1.0,
                                        # "image": self.read_image(),
                                        "image": selectedCanvasRecords,
                                        "resize_mode": 1,
                                        "lowvram": False,
                                        "processor_res": 64,
                                        "threshold_a": 64,
                                        "threshold_b": 64,
                                        "guidance_start": 0.0,
                                        "guidance_end": 1.0,
                                        "control_mode": 0,
                                        "pixel_perfect": False,
                                    }
                                ]
                            }
                        },
                    },
                }
                sd_tasks.append(task)

            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(sd_pool.controlnet_text2image_V15, task)
                    for task in sd_tasks
                ]
                images = [future.result() for future in futures]

            if len(images) != num:
                raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

            count = len(images)
            web_paths = {}

            for i in range(count):
                base64_string = images[i]["image"]
                # print(type(base64_string))
                image_data = base64.b64decode(base64_string)

                image_filename = imageSave(username, image_data, i)

                web_paths[i] = f"/images/{image_filename}"
                print(f"Web accessible path: {web_paths[i]}")
            return {"paths": web_paths}
        else:
            raise BusinessException(BUSINESS_FAIL, "用户阶段错误")

    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 4-1 完成/测试/校对效果 text2Image_V2
def rendering_createNew(json_in):
    print("[Process] In rendering_createNew")
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        username = json_in.get("username")
        # gpt_task = {
        #     "messages": generate_prompts(
        #         "What is the main object of the design task '{designTask}' in English, use only a word, for example:'设计一个好看的无人机',main body is 'drone'".format(designTask=designTask)
        #     )
        # }
        # mainbody = gpt_pool.chat(gpt_task)['text']
        # # Step 4: 并行生成 SD 图片
        # print(mainbody)
        prompt_rendering = generate_prompts(
            prompts.prompt_rendering_createNew, designTask=designTask
        )
        gpt_task = {"messages": prompt_rendering}
        sd_prompt = gpt_pool.chat(gpt_task)["text"]
        cleaned_prompt_sd = sd_prompt.replace("```json\n", "").replace("```", "")
        print(cleaned_prompt_sd)
        sd_prompt_phase = json.loads(cleaned_prompt_sd)["prompt"]
        print(sd_prompt_phase)
        # return sd_prompt
        # gpt_task = {
        #         "messages": generate_prompts(
        #             "What is the main object of the design task '{designTask}' in English, use only a word or short vocabulary, for example:'设计一个好看的无人机',main body is 'drone'".format(designTask=designTask)
        #         )
        #     }
        # mainbody = gpt_pool.chat(gpt_task)['text']
        #     # Step 4: 并行生成 SD 图片
        #     # print(mainbody)
        sd_tasks = []
        prompts_pos = generate_prompts(
            prompts.rendering_createNew_sd_pos, sd_prompt_in=sd_prompt_phase
        )
        prompts_neg = prompts.rendering_createNew_sd_neg
        for i in range(num):
            task = {
                "index": i,
                "prompt": prompts_pos,
                "task_type": "renderingCreateNew",
                "negative_prompt": prompts_neg,
                "options": {
                    "Model": "v2-1_512-ema-pruned",
                    "width": 512,
                    "height": 512,
                    "sampler_name": "Euler a",
                    "steps": 20,
                },
            }
            sd_tasks.append(task)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(sd_pool.text2Image_V2, task) for task in sd_tasks]
            images = [future.result() for future in futures]

        if len(images) != num:
            raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

        count = len(images)

        web_paths = {}

        for i in range(count):
            base64_string = images[i]["image"]
            # print(type(base64_string))
            image_data = base64.b64decode(base64_string)

            image_filename = imageSave(username, image_data, i)

            web_paths[i] = f"/images/{image_filename}"
            print(f"Web accessible path: {web_paths[i]}")

        return {"paths": web_paths}  # 打印web路径，而不是文件系统路径

    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 4-2 完成/测试/校对效果 text2Image_V2
def rendering_refine(json_in):
    print("[Process] In rendering refine")
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        username = json_in.get("username")

        gpt_task = {
            "messages": generate_prompts(
                prompts.prompt_mainbody,
                designTask=designTask
                )
        }
        # mainbody = gpt_pool.chat(gpt_task)["text"]
        mainbody = 'agricultural drone'
        
        print(mainbody)
        sd_tasks = []
        prompts_pos = generate_prompts(
            prompts.rendering_refine_sd_pos, mainbody=mainbody
        )
        prompts_neg = prompts.rendering_refine_sd_neg
        for i in range(num):
            task = {
                "index": i,
                "prompt": prompts_pos,
                "task_type": "renderingRefine",
                "negative_prompt": prompts_neg,
                "options": {
                    "Model": "v2-1_512-ema-pruned",
                    "width": 512,
                    "height": 512,
                    "sampler_name": "Euler a",
                    "steps": 20,
                },
            }
            sd_tasks.append(task)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(sd_pool.text2Image_V2, task) for task in sd_tasks]
            images = [future.result() for future in futures]

        if len(images) != num:
            raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

        count = len(images)

        web_paths = {}

        for i in range(count):

            base64_string = images[i]["image"]
            # print(type(base64_string))
            image_data = base64.b64decode(base64_string)

            task = {
                "index": 0,
                "task_type": "sketchtoSketch_sam",
                "negative_prompt": prompts_neg,
                "mainbody": mainbody,
                "src_img_base64": base64_string,
            }
            sd_ret = sd_pool.bgremove(task)
            mask = sd_ret["mask"]
            masked_image = sd_ret["masked_image"]

            buffer = BytesIO()
            # 保存图像到字节流，这里以PNG格式为例
            masked_image.save(buffer, format="PNG")
            # 获取字节流的内容
            img_byte = buffer.getvalue()
            # 将字节数据转换为base64字符串
            base64_string = base64.b64encode(img_byte).decode("utf-8")

            # image_data = base64.b64decode(base64_string)
            image_data_wbg_string = transparent_to_white_bg(base64_string)

            image_data_wbg = base64.b64decode(image_data_wbg_string)

            image_filename = imageSave(username, image_data_wbg, i)

            web_paths[i] = f"/images/{image_filename}"
            print(f"Web accessible path: {web_paths[i]}")

        return {"paths": web_paths}  # 打印web路径，而不是文件系统路径

    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 4-3 完成
def rendering_extend(json_in):
    print("[Process] In rendering extend")
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        username = json_in.get("username")
        selectedCanvasRecords = json_in.get("selectedCanvasRecords")

        if not selectedCanvasRecords:
            raise BusinessException(BUSINESS_FAIL, "参考图像缺失")

        # 获得prompt

        prompt_rendering = generate_prompts(
            prompts.prompt_rendering_createNew, designTask=designTask
        )
        gpt_task = {"messages": prompt_rendering}
        sd_prompt = gpt_pool.chat(gpt_task)["text"]
        cleaned_prompt_sd = sd_prompt.replace("```json\n", "").replace("```", "")
        print(cleaned_prompt_sd)
        sd_prompt_phase = json.loads(cleaned_prompt_sd)["prompt"]
        print(sd_prompt_phase)

        # 获得主体
        gpt_task = {
            "messages": generate_prompts(
                prompts.prompt_mainbody,
                designTask=designTask
                )
        }
        # mainbody = gpt_pool.chat(gpt_task)["text"]
        mainbody = 'agricultural drone'
        #   去除背景
        print(mainbody)
        print(selectedCanvasRecords)
        task = {
            "index": 0,
            "task_type": "sketchtoSketch_sam",
            "mainbody": mainbody,
            "src_img_base64": selectedCanvasRecords,
        }
        sd_ret = sd_pool.bgremove(task)
        mask = sd_ret["mask"]
        buffer = BytesIO()
        # 保存图像到字节流，这里以PNG格式为例
        mask.save(buffer, format="PNG")
        # 获取字节流的内容
        img_byte = buffer.getvalue()
        # 将字节数据转换为base64字符串
        base64_string_mask = base64.b64encode(img_byte).decode("utf-8")

        # image_data = base64.b64decode(base64_string)
        # image_filename = imageSave(username,image_data,0)

        #### Image 2 Image 待施工
        sd_tasks = []

        prompts_pos = sd_prompt_phase
        prompts_neg = ""
        for i in range(num):
            task = {
                "index": i,
                "prompt": prompts_pos,
                "task_type": "renderingExtend",
                "negative_prompt": prompts_neg,
                "mask": base64_string_mask,
                "images": [selectedCanvasRecords],
            }
            sd_tasks.append(task)

        with ThreadPoolExecutor() as executor:
            futures = [executor.submit(sd_pool.image2Image, task) for task in sd_tasks]
            images = [future.result() for future in futures]

        if len(images) != num:
            raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

        count = len(images)

        web_paths = {}

        for i in range(count):
            base64_string = images[i]["image"]
            # print(type(base64_string))
            image_data = base64.b64decode(base64_string)

            image_filename = imageSave(username, image_data, i)

            web_paths[i] = f"/images/{image_filename}"
            print(f"Web accessible path: {web_paths[i]}")

        return {"paths": web_paths}  # 打印web路径，而不是文件系统路径

    except BusinessException as be:
        raise be
    except Exception as e:
        raise e


# 4-4 完成 controlnet_text2image_V15
def rendering_toRendering(json_in):
    print("[Process] In rendering_toRendering")
    try:
        designTask = json_in.get("designTask")
        if not designTask:
            raise BusinessException(BUSINESS_FAIL, "设计任务缺失")
        num = json_in.get("num")
        if not num:
            raise BusinessException(BUSINESS_FAIL, "设计数量缺失")
        userInput_list = json_in.get("selectedTexts")
        userInput = ""
        for usertext in userInput_list:
            userInput = userInput + "'" + usertext + "'"
        username = json_in.get("username")
        selectedCanvasRecords = json_in.get("selectedCanvasRecords")
        userStage = json_in.get("userStage")

        if not selectedCanvasRecords:
            raise BusinessException(BUSINESS_FAIL, "参考图像缺失")

        gpt_task = {
            "messages": generate_prompts(
                prompts.prompt_mainbody,
                designTask=designTask
                )
        }
        # mainbody = gpt_pool.chat(gpt_task)["text"]
        mainbody = 'agricultural drone'
        print(mainbody)

        if userStage == "草图的环境":
            print(1)

            sd_tasks = []
            prompts_pos = generate_prompts(
                prompts.rendering_toRendering_sd_pos_1, mainbody=mainbody
            )
            prompts_neg = prompts.rendering_toRendering_sd_neg_1

            for i in range(num):
                task = {
                    "index": i,
                    "prompt": prompts_pos,
                    "task_type": "modeltoModel",
                    "negative_prompt": prompts_neg,
                    "options": {
                        "Model": "v1-5-pruned-emaonly",
                        "width": 512,
                        "height": 512,
                        "sampler_name": "Euler a",
                        "steps": 20,
                        "cfg_scale": 7,
                        "alwayson_scripts": {
                            "controlnet": {
                                "args": [
                                    {
                                        "enabled": True,
                                        "module": "lineart_standard",
                                        "model": "control_v11p_sd15_lineart",
                                        "weight": 1.0,
                                        "image": selectedCanvasRecords,
                                        "resize_mode": 1,
                                        "lowvram": False,
                                        "processor_res": 64,
                                        "threshold_a": 64,
                                        "threshold_b": 64,
                                        "guidance_start": 0.0,
                                        "guidance_end": 1.0,
                                        "control_mode": 0,
                                        "pixel_perfect": False,
                                    }
                                ]
                            }
                        },
                    },
                }
                sd_tasks.append(task)

            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(sd_pool.controlnet_text2image_V15, task)
                    for task in sd_tasks
                ]
                images = [future.result() for future in futures]

            if len(images) != num:
                raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

            count = len(images)
            web_paths = {}

            for i in range(count):
                base64_string = images[i]["image"]
                # print(type(base64_string))
                image_data = base64.b64decode(base64_string)

                image_filename = imageSave(username, image_data, i)

                web_paths[i] = f"/images/{image_filename}"
                print(f"Web accessible path: {web_paths[i]}")
            return {"paths": web_paths}

        elif userStage == "模型图的环境":
            print(2)

            sd_tasks = []
            prompts_pos = generate_prompts(
                prompts.rendering_toRendering_sd_pos_2, mainbody=mainbody
            )
            prompts_neg = prompts.rendering_toRendering_sd_neg_2

            for i in range(num):
                task = {
                    "index": i,
                    "prompt": prompts_pos,
                    "task_type": "modeltoModel",
                    "negative_prompt": prompts_neg,
                    "options": {
                        "Model": "v1-5-pruned-emaonly",
                        "width": 512,
                        "height": 512,
                        "sampler_name": "Euler a",
                        "steps": 20,
                        "cfg_scale": 7,
                        "alwayson_scripts": {
                            "controlnet": {
                                "args": [
                                    {
                                        "enabled": True,
                                        "module": "lineart_standard",
                                        "model": "control_v11p_sd15_lineart",
                                        "weight": 1.0,
                                        "image": selectedCanvasRecords,
                                        "resize_mode": 1,
                                        "lowvram": False,
                                        "processor_res": 64,
                                        "threshold_a": 64,
                                        "threshold_b": 64,
                                        "guidance_start": 0.0,
                                        "guidance_end": 1.0,
                                        "control_mode": 0,
                                        "pixel_perfect": False,
                                    }
                                ]
                            }
                        },
                    },
                }
                sd_tasks.append(task)

            with ThreadPoolExecutor() as executor:
                futures = [
                    executor.submit(sd_pool.controlnet_text2image_V15, task)
                    for task in sd_tasks
                ]
                images = [future.result() for future in futures]

            if len(images) != num:
                raise BusinessException(BUSINESS_FAIL, "生成目标数量不一致")

            count = len(images)
            web_paths = {}

            for i in range(count):
                base64_string = images[i]["image"]
                # print(type(base64_string))
                image_data = base64.b64decode(base64_string)

                image_filename = imageSave(username, image_data, i)

                web_paths[i] = f"/images/{image_filename}"
                print(f"Web accessible path: {web_paths[i]}")
            return {"paths": web_paths}
        else:
            raise BusinessException(BUSINESS_FAIL, "用户阶段错误")

    except BusinessException as be:
        raise be
    except Exception as e:
        raise e
