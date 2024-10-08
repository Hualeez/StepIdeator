from queue import Queue
from threading import Semaphore

import requests
import base64
from PIL import Image
from io import BytesIO
import cv2
import config
from agent.utils import AgentException
from settings.sd_default import sd_default_options


class SDInstance:
    def __init__(self, url):
        self.url = url


class SDInstancePool:
    def __init__(self, sd_urls):
        self.sd_instances = Queue()
        for url in sd_urls:
            self.sd_instances.put(SDInstance(url)) 
        self.semaphore = Semaphore(len(sd_urls))
        
    def filename_to_base64(filename):
        with open(filename, "rb") as fh:
            return base64.b64encode(fh.read())


    def image2Image(self,task):
        self.semaphore.acquire()
        sd_instance = self.sd_instances.get()
        try:
            # url = sd_instance.url + config.SD_T2I_ENDPOINT
            url = "http://127.0.0.1:7867"+config.SD_I2I_ENDPOINT
            payload = {
                "batch_size": 1,
                "cfg_scale": 7,
                "height": 768,
                "width": 512,
                "n_iter": 1,
                "steps": 30,
                "sampler_name": "DPM++ 2M Karras",
                "prompt": task['prompt'],
                "negative_prompt": task['negative_prompt'],
                "seed_enable_extras": False,
                "seed_resize_from_h": 0,
                "seed_resize_from_w": 0,
                "subseed": -1,
                "subseed_strength": 0,
                "override_settings": {},
                "override_settings_restore_afterwards": False,
                "do_not_save_grid": False,
                "do_not_save_samples": False,
                "s_churn": 0,
                "s_min_uncond": 0,
                "s_noise": 1,
                "s_tmax": None,
                "s_tmin": 0,
                "script_args": [],
                "script_name": None,
                "styles": [],
                "alwayson_scripts": {
                    "ControlNet": {
                        "args": [
                            {
                                "control_mode": 0,
                                "enabled": True,
                                "guidance_end": 1,
                                "guidance_start": 0,
                                "low_vram": False,
                                "model": "control_v11p_sd15_inpaint",
                                "module": "inpaint_only",
                                "pixel_perfect": True,
                                "processor_res": 512,
                                "resize_mode": 1,
                                "threshold_a": 64,
                                "threshold_b": 64,
                                "weight": 1,
                            }
                        ]
                    }
                },
                "denoising_strength": 0.75,
                "initial_noise_multiplier": 1,
                "inpaint_full_res": 0,
                "inpaint_full_res_padding": 32,
                "inpainting_fill": 1,
                # "inpainting_mask_invert": 0, #画的是白色的区域
                "inpainting_mask_invert": 1,
                "mask_blur_x": 4,
                "mask_blur_y": 4,
                "mask_blur": 4,
                "resize_mode": 0,
                "init_images": task['images'],
                "mask": task['mask'],
                "width":512,
                "height": 512
            }

            # 更换checkpoint为RV
            override_settings = {}
            override_settings["sd_model_checkpoint"] = "realisticVisionV60B1_v60B1VAE"

            override_payload = {
                "override_settings": override_settings
            }
            payload.update(override_payload)
            
            print("i2i: " + str(task["index"]))
            # print(payload['init_images'][0][0])
            r = post_sdapi(url, payload)
            print("i2i res.")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": r['images'][0]
            }
        except Exception as e:
            print(f"Error: 调用Stable Diffusion失败，{str(e)}")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": ""
            }
        finally:
            self.sd_instances.put(sd_instance)
            self.semaphore.release()
        

    def text2Image(self, task):
        self.semaphore.acquire()
        sd_instance = self.sd_instances.get()
        try:
            # url = sd_instance.url + config.SD_T2I_ENDPOINT
            url = "http://127.0.0.1:7867"+config.SD_T2I_ENDPOINT

            payload = {
                "prompt": task["prompt"],
                "negative_prompt": task["negative_prompt"],
            }
            
            # 更换checkpoint为RV
            # override_settings = {}
            # override_settings["sd_model_checkpoint"] = "realisticVisionV60B1_v60B1VAE"

            # override_payload = {
            #     "override_settings": override_settings
            # }
            # payload.update(override_payload)
            
            payload.update(sd_default_options)
            
            if task["options"] is not None:
                print("options not None:")
                print(task["options"])
                payload.update(task["options"])

            print("t2i_RV" + str(task["index"]))
            print(payload)
            r = post_sdapi(url, payload)
            print("t2i_RV res.")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": r['images'][0]
            }
        except Exception as e:
            print(f"Error: 调用Stable Diffusion失败，{str(e)}")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": ""
            }
        finally:
            self.sd_instances.put(sd_instance)
            self.semaphore.release()
            
    def text2Image_RV(self, task):
        self.semaphore.acquire()
        sd_instance = self.sd_instances.get()
        try:
            # url = sd_instance.url + config.SD_T2I_ENDPOINT
            url = "http://127.0.0.1:7867"+config.SD_T2I_ENDPOINT

            payload = {
                "prompt": task["prompt"],
                "negative_prompt": task["negative_prompt"],
            }
            
            # 更换checkpoint为RV
            override_settings = {}
            override_settings["sd_model_checkpoint"] = "realisticVisionV60B1_v60B1VAE"

            override_payload = {
                "override_settings": override_settings
            }
            payload.update(override_payload)
            payload.update(sd_default_options)
            
            if task["options"] is not None:
                print("options not None:")
                print(task["options"])
                payload.update(task["options"])

            print("t2i_RV" + str(task["index"]))
            print(payload)
            r = post_sdapi(url, payload)
            print("t2i_RV res.")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": r['images'][0]
            }
        except Exception as e:
            print(f"Error: 调用Stable Diffusion失败，{str(e)}")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": ""
            }
        finally:
            self.sd_instances.put(sd_instance)
            self.semaphore.release()
         
    def text2Image_V2(self, task):
        self.semaphore.acquire()
        sd_instance = self.sd_instances.get()
        try:
            # url = sd_instance.url + config.SD_T2I_ENDPOINT
            url = "http://127.0.0.1:7867"+config.SD_T2I_ENDPOINT

            payload = {
                "prompt": task["prompt"],
                "negative_prompt": task["negative_prompt"],
            }
            
            # 更换checkpoint为V2
            override_settings = {}
            override_settings["sd_model_checkpoint"] = "v2-1_512-ema-pruned"

            override_payload = {
                "override_settings": override_settings
            }
            payload.update(override_payload)
            payload.update(sd_default_options)
            
            if task["options"] is not None:
                print("options not None:")
                print(task["options"])
                payload.update(task["options"])

            print("t2i_RV" + str(task["index"]))
            print(payload)
            r = post_sdapi(url, payload)
            print("t2i_RV res.")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": r['images'][0]
            }
        except Exception as e:
            print(f"Error: 调用Stable Diffusion失败，{str(e)}")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": ""
            }
        finally:
            self.sd_instances.put(sd_instance)
            self.semaphore.release()
    
    def read_image(self,path):
        img = cv2.imread(path)
        retval, bytes = cv2.imencode('.png', img)
        encoded_image = base64.b64encode(bytes).decode('utf-8')
        return encoded_image
    
    def controlnet_text2image(self, task):
        self.semaphore.acquire()
        sd_instance = self.sd_instances.get()
        try:
            # url = sd_instance.url + config.SD_T2I_ENDPOINT
            url = "http://127.0.0.1:7867"+config.SD_T2I_ENDPOINT
            
            payload = {
                "prompt": task['prompt'],
                "negative_prompt": task['negative_prompt']
            }

            
            payload.update(sd_default_options)
            
            if task["options"] is not None:
                print(task["options"])
                payload.update(task["options"])
                
            print("i2i: " + str(task["index"]))
            # print(payload)
            r = post_sdapi(url, payload)
            print("i2i res.")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": r['images'][0]
            }
        except Exception as e:
            print(f"Error: 调用Stable Diffusion失败，{str(e)}")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": ""
            }
        finally:
            self.sd_instances.put(sd_instance)
            self.semaphore.release()
            
    def controlnet_text2image_RV(self, task):
        self.semaphore.acquire()
        sd_instance = self.sd_instances.get()
        try:
            # url = sd_instance.url + config.SD_T2I_ENDPOINT
            url = "http://127.0.0.1:7867"+config.SD_T2I_ENDPOINT
            
            payload = {
                "prompt": task['prompt'],
                "negative_prompt": task['negative_prompt']
            }

            
            # 更换checkpoint为RV
            override_settings = {}
            override_settings["sd_model_checkpoint"] = "realisticVisionV60B1_v60B1VAE"

            override_payload = {
                "override_settings": override_settings
            }
            payload.update(override_payload)
            payload.update(sd_default_options)
            
            if task["options"] is not None:
                print(task["options"])
                payload.update(task["options"])
                
            print("i2i: " + str(task["index"]))
            # print(payload)
            r = post_sdapi(url, payload)
            print("i2i res.")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": r['images'][0]
            }
        except Exception as e:
            print(f"Error: 调用Stable Diffusion失败，{str(e)}")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": ""
            }
        finally:
            self.sd_instances.put(sd_instance)
            self.semaphore.release()
            
    def controlnet_text2image_V15(self, task):
        self.semaphore.acquire()
        sd_instance = self.sd_instances.get()
        try:
            # url = sd_instance.url + config.SD_T2I_ENDPOINT
            url = "http://127.0.0.1:7867"+config.SD_T2I_ENDPOINT
            
            payload = {
                "prompt": task['prompt'],
                "negative_prompt": task['negative_prompt']
            }

            
            # 更换checkpoint为RV
            override_settings = {}
            override_settings["sd_model_checkpoint"] = "v1-5-pruned-emaonly"

            override_payload = {
                "override_settings": override_settings
            }
            payload.update(override_payload)
            payload.update(sd_default_options)
            
            if task["options"] is not None:
                print(task["options"])
                payload.update(task["options"])
                
            print("i2i: " + str(task["index"]))
            # print(payload)
            r = post_sdapi(url, payload)
            print("i2i res.")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": r['images'][0]
            }
        except Exception as e:
            print(f"Error: 调用Stable Diffusion失败，{str(e)}")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": ""
            }
        finally:
            self.sd_instances.put(sd_instance)
            self.semaphore.release()
    
    def paste(self,eimg):
        img_pil = Image.open(BytesIO(base64.b64decode(eimg[1]))).resize((512, 512))
        return img_pil
    
    def bgremove(self,task):
        self.semaphore.acquire()
        sd_instance = self.sd_instances.get()
        try:
            # url = sd_instance.url + config.SD_T2I_ENDPOINT
            # url = "http://127.0.0.1:7864"+config.SD_T2I_ENDPOINT
            url = "http://127.0.0.1:7867"+config.SD_SAM_PRED
            print(url)
            
            img_data = task['src_img_base64']
            sam_mainbody = task['mainbody']
            
            
            
            payload = {
                "input_image": str(img_data).replace("data:image/png;base64,",''),
                "dino_enabled": True,
                "dino_text_prompt": "drone",
                "dino_preview_checkbox": False,
            }
            response = requests.post(url, json=payload)
            r = response.json()
            # print(payload)
            # print(r)
            # r = post_sdapi(url, payload)
            print("SAM:"+str(r["msg"]))

            blended_image_2 =self.paste(r["blended_images"])
            mask_2 = self.paste(r["masks"])
            masked_image_2 = self.paste(r["masked_images"])
            return {
                    "index": task["index"],
                    "type": task["task_type"],
                    "mask": mask_2,
                    "masked_image":masked_image_2
            }       
        except Exception as e:
            print(f"Error: 调用Stable Diffusion失败，{str(e)}")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "mask": "",
                "masked_image":""
            }
        finally:
            self.sd_instances.put(sd_instance)
            self.semaphore.release()
       

def call_sdapi(url: str, params):
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise AgentException(f"调用 Stable Diffusion 失败，URI {str(url)}，{str(e)}")


def post_sdapi(url: str, payload, headers=None):
    try:
        response = requests.post(url, json=payload, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        print(f"调用 Stable Diffusion 失败：URI {str(url)}，{str(e)}")


sd_pool = SDInstancePool(config.SD_ENDPOINTS)
