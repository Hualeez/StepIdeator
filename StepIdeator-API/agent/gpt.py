import openai
from queue import Queue
from threading import Semaphore
import config
import requests
import httpx

# from agent.utils import AgentException

class GPTInstance:
    def __init__(self):
        pass
        
        
class GPTInstancePool:
    def __init__(self, instance_num):
        self.gpt_instances = Queue()
        for _ in range(instance_num):
            self.gpt_instances.put(GPTInstance())
        self.semaphore = Semaphore(instance_num)
        self.client = openai.OpenAI(
            base_url="https://api.openai.com/v1", 
            api_key=config.OPENAI_KEY,
            http_client=httpx.Client(
                base_url="https://api.openai.com/v1",
                follow_redirects=True,
            )
        )       
        openai.OpenAI(base_url="https://api.openai.com/v1",api_key=config.OPENAI_KEY)
        
        # self.client = openai.OpenAI(
        #     base_url="https://kapkey.chatgptapi.org.cn/v1", 
        #     api_key=config.OPENAI_KEY,
        #     http_client=httpx.Client(
        #         base_url="https://kapkey.chatgptapi.org.cn/v1",
        #         follow_redirects=True,
        #     )
        # )
        # openai.OpenAI(base_url="https://kapkey.chatgptapi.org.cn/v1",api_key=config.OPENAI_KEY)

    def chat(self, task):
        # try:
        #     client = openai.OpenAI(
        #         base_url="https://kapkey.chatgptapi.org.cn/v1",
        #         api_key=config.OPENAI_KEY
        #     )

        #     completion = client.chat.completions.create(
        #     model="gpt-3.5-turbo",
        #     messages=[
        #         {"role": "system", "content": "You are a helpful assistant."},
        #         {"role": "user", "content": "Hello!"}
        #     ]
        #     )

        #     print(completion.choices[0].message)
        self.semaphore.acquire()
        gpt_instance = self.gpt_instances.get()
        try:
            print("chat: ")
            print(task["messages"])
            response = self.client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role":"user","content":task["messages"]}
                    ],
                # temperature=0.2,
                max_tokens=500
            )
            # print(response.choices[0].message.content)
            r = response.choices[0].message.content
            return {"text": r}
        except Exception as e:
            print(f"Error: 调用GPT生成文本失败，{str(e)}")
            return {"text": ""}
        finally:
            self.gpt_instances.put(gpt_instance)
            self.semaphore.release()

    def text2Image(self, task):
        self.semaphore.acquire()
        gpt_instance = self.gpt_instances.get()
        try:
            print("t2i: " + str(task["index"]))
            print(task["prompt"])
            response = openai.Image.create(
                model="dall-e-3",
                prompt=task["prompt"],
                size="1024x576",
                quality="standard",
                n=1,
            )
            r = response.data[0].url
            print("t2i res: " + str(r))
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": r
            }
        except Exception as e:
            print(f"Error: 调用GPT文生图失败，{str(e)}")
            return {
                "index": task["index"],
                "type": task["task_type"],
                "image": ""
            }
        finally:
            self.gpt_instances.put(gpt_instance)
            self.semaphore.release()       
    
    def ask_image(self, task):
        self.semaphore.acquire()
        gpt_instance = self.gpt_instances.get()
        try:
            print("ask image: ")
            print(str(task["prompt"]))
            # print(task['images']) # images 是一个列表，里面每张图片是 B64编码
            
            # images_content = [{
            #     "type": "image_url",
            #     "image_url": {
            #         "url": f"{image}"
            #     }
            # } for image in task['images']]
            images_content = [{
                "type": "image_url",
                "image_url": {"url":image}  # 直接使用image字符串，而不是一个字典
            } for image in task['images']]
        
            response = self.client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        # "content": [
                        #     {
                        #         "type": "text",
                        #         "text": task["prompt"]
                        #     },
                        #     *images_content,
                        # ]
                        "content": [
                            {
                                "type": "text",
                                "text": str(task['prompt'])
                            },
                            *images_content
                        ]
                    }
                ],
                max_tokens=1000,
            )
            # print(response)

            r = response.choices[0].message.content
            print("ask image res: " + str(r))
            return {
                "text": r
            }
        except Exception as e:
            print(f"Error: 调用GPT图片提问失败，{str(e)}")
            return {
                "text": ""
            }
        finally:
            self.gpt_instances.put(gpt_instance)
            self.semaphore.release()       

gpt_pool = GPTInstancePool(config.OPENAI_GPT_INSTANCE)