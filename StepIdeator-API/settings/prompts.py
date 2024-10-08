prompt_mainbody = ("Please provide a one-word or short vocabulary item in English representing the main object of the design task '{designTask}', for example: 'drone','cordless drill'")

# 1-1
prompt_designBrief_createNew = ("""
    #指令#
    设计摘要是一段描述产品的目标人群、使用场景、痛点、主要功能这四个类别的文本。\
    
    你是一个经验丰富的产品设计师，根据{designTask}和{userInput}，为我生成JSON格式的设计摘要。\
    在生成时，你需要：
    (1)针对每一个设计摘要中的类别，精简语言并整理在输出格式中。\
    (2)你所撰写的内容需要具有独特性并指出细节，避免普适性、笼统的回答。例如，不能回答“在处理这些问题时的低效率和不便利性”，需要指出具体是什么低效率、什么不便利。\
    (3)生成设计摘要时，拉大不同设计摘要之间内容的区分度，避免提到相近内容。\
    (4)使用中文输出，严格按照格式输出,只输出json格式，不得改变json的键名，仅在键值处补充
     #输出案例#
    {{
        "目标人群": [你的输出],
        "使用场景": [你的输出],
        "痛点": [你的输出],
        "主要功能": [你的输出]
    }}
""")
# 1-2
prompt_designBrief_refine = ("""
    #指令#
    设计摘要是一段描述产品的目标人群、使用场景、痛点、主要功能这四个类别的文本。\
    
    你是一个经验丰富的产品设计师，根据{designTask}和{userInput}，根据你数据库中的信息总结一个类似产品，以指定JSON格式输出。\
    在生成时，你需要：
    (1)按照输出格式的类别进行整理，精简语言并整理在输出格式中。若输入中不包含某类别的内容，则留空。
    (2)使用中文输出，严格按照格式输出,只输出json格式，不得改变json的键名，仅在键值处补充
                             
    #输出格式#
    {{
        "产品名":[你的输出], 
        "目标人群": [你的输出],
        "使用场景": [你的输出],
        "痛点": [你的输出],
        "主要功能": [你的输出],
        "结构":[你的输出],
        "外观造型":[你的输出],
        "现有技术": [你的输出],
    }}
""")
# 1-3
prompt_designBrief_extend = ("""
    #指令#
    
    你是一个经验丰富的产品设计师，根据{designTask}和{userInput}，判断{userInput}的内容类型，并为{userInput}中的内容提出细化建议，以指定JSON格式输出。\
    在生成时，你需要注意：
    (1){userInput}指你需要拓展或增加的文本，避免重复与原文相同或类似的观点。{userInput}中可能直接包含它的内容类型。
       如“结构：一体化机身”，则对应(2)中“当{userInput}的文本是外观造型或结构相关内容时”一条规则输出。
       如“现有技术：无刷电机”、“结构：一体化机身”，则对应(2)中“当{userInput}的文本包含多条内容时”一条规则，针对<现有技术>、<结构>分别列出8个关键短语。
    (2)当{userInput}的文本是目标人群相关内容时，针对<目标人群>列出8个关键短语；针对<痛点>、<使用场景>分别列出3个关键短语。避免输出其他键及内容。
       当{userInput}的文本是使用场景相关内容时，针对<使用场景>列出8个关键短语；针对<目标人群>、<主要功能>分别列出3个关键短语。避免输出其他键及内容。
       当{userInput}的文本是痛点相关内容时，针对<痛点>列出8个关键短语；针对<主要功能>分别列出3个关键短语。避免输出其他键及内容。
       当{userInput}的文本是主要功能相关内容时，针对<主要功能>列出8个关键短语；针对<外观造型>、<结构>、<现有技术>分别列出3个关键短语。避免输出其他键及内容。
       当{userInput}的文本是外观造型或结构相关内容时，针对<外观造型>列出8个关键短语；针对<结构>、<现有技术>分别列出3个关键短语。避免输出其他键及内容。
       当{userInput}的文本是现有技术相关内容时，针对<现有技术>列出8个关键短语。不输出其他键及内容。
       当{userInput}的文本包含多条内容时，判断{userInput}的内容类型，针对对应的键分别列出5个关键短语。
    (3)你所给出的观点需要使用不同的关键分词短语概括，每个短语使用""包含，并使用,隔开。避免短语的内容重复，避免给出完整句子。
    (4)<>内部的为指定键名，输出时不需要带<>。严格按照格式输出,只输出json格式，不得改变json的键名，仅在键值处补充；避免输出规则没有指定的内容。
    (5)所有{userInput}都可以用(2)中某一条规则判断，严格按照对应的规则输出；仔细检查你对{userInput}的分类，避免错误判断。
    (6)使用中文输出。
    #输出案例#
    {{
        "指定的键名":[你的输出], 
        "指定的键名": [你的输出],
        "指定的键名": [你的输出]
    }}
""")
# 2-1
prompt_sketchGeneration_createNew_pos=('(a pencil sketch of a {mainbody}:1.4),(lineart:1.2),(monochrome:1.1),white background,one-hour rough draft,complete view,ideas,sketch,crosshatch,contour lines and structural lines,hand-drawn sketching')
prompt_sketchGeneration_createNew_neg=('(out of frame:1.1),(weird structure:1.2),(unreasonable:1.1),(product image:1.1),(photorealistic:1.3),color,furniture,surroundings,worst quality,people,man,woman,lowres,cropped,text,jpeg,artifacts,signature,watermark,cartoon,duplicate,anime,blurry,ugly,deformed,Easy Negative,finely detailed,flame,grey,pen,book,paper,pencil,hands,rendering,(model:1.1)')

# 2-2
prompt_sketch_refine = ("""
#任务描述#
你将收到JSON格式的<设计任务>、JSON格式的<功能文本>。我现在正针对这一<设计任务>和<功能文本>完善概念草图，主要关注（1）外观形状造型（2）内部结构及功能模块在产品内部的布局。
<功能文本>：{userInput}
<设计任务>：{designTask}
#任务要求#
（1）为我提供具体、详细且可行的建议，告诉我如何完善草图。
（2）当你说明外观形状造型时，给出具体的、有针对性的形状、外观造型，避免笼统描述。包括形状、边缘加工、细节、使用方式等，不包括材料、颜色。
（3）当你说明内部结构及功能模块在产品内部的布局时，针对每个小模块和整体分别给出参考的尺寸大小、技术规格等。需要包括实现<功能文本>的所有可能技术模块，及组合建议。
（4）使用中文输出，严格按照格式输出,只输出json格式，不得改变json的键名，仅在键值处补充
（5）只输出json
#输出格式#
JSON格式输出，键为：
- 外观造型
- 内部结构

#输出格式以及案例#
{{
  "外观造型": {{
    "形状": "流线型",
    "边缘加工": "圆滑",
    "细节": "简洁，避免过多装饰",
    "使用方式": "符合人体工程学，易于握持和操作"
  }},
  "内部结构": {{
    "整体布局": {{
      "建议尺寸": "根据外部尺寸确定，确保内部模块布局合理",
      "技术规格": "考虑功能模块之间的连接和布线"
    }},
    "模块布局": {{
      "模块1": {{
        "尺寸": "根据功能要求确定",
        "技术规格": "确保与其他模块的连接和数据传输正常"
      }},
      "模块2": {{
        "尺寸": "根据功能要求确定",
        "技术规格": "确保与其他模块的连接和数据传输正常"
      }},
      "模块3": {{
        "尺寸": "根据功能要求确定",
        "技术规格": "确保与其他模块的连接和数据传输正常"
      }},
      "...": "其他功能模块同理"
    }}
  }}
}}
""")

prompt_sketch_refine_sd = ("""
#任务简介#我将告诉提供给你一个JSON格式的预输入<描述>，根据这段预输入文本，为我生成用于在stable diffusion生成产品图像的prompt。
#任务要求#stable diffusion是一款利用深度学习进行文生图的模型，支持通过使用prompt来产生新的图像，描述要包含或省略的元素。

下面我将说明输入的形式，输入的键包括：
- 外观形状造型（必须项）：JSON格式的描述。

下面我将说明prompt的生成要求:
（1）这里的prompt主要用于描述某个产品，所生成的图中不应包括除了产品以外的任何内容。
（2）首先需要将输入的内容翻译为英文，作为prompt的一部分。
（3）prompt需要精简文本长度，10词以内。重点保留形状、边缘加工、细节等外观造型和形状，prompt中不包括材料、颜色。
（4）使用英文短句来描述。
（5）使用英文半角,做分隔符分隔提示词，每个提示词不要带引号。
（6）prompt中不能含有-和，单词不能重复。

#案例#
当预输入是
{{"外观造型": 
    {{  "形状": "流线型",
        "边缘加工": "圆滑",
        "细节": "简洁，避免过多装饰",
        "使用方式": "符合人体工程学，易于握持和操作"
    }}
}}
时，输出为：
{{
"prompt": "Streamlined shape, Smooth edges, Clean and simple design, Ergonomically friendly"
}}

#输出要求#只需要输出提示词的内容，使用JSON列表输出，每一次输出为一个元素，不要有其他任何文本，包括对提示词的解释内容。

<描述>为：{description}
""")


prompt_sketch_refine_sd_pos = ('(a pencil sketch of a {mainbody}:1.4),{sd_prompt_in},colouring-in sheet,by Adam Marczyński,white background,one-hour rough drawing,complete view,monochrome,ideas,sketch,lineart,crosshatch,Only contour lines and structural lines')
prompt_sketch_refine_sd_neg = prompt_sketchGeneration_createNew_neg

# 2-3
prompt_sketch_extend_sd_pos = prompt_sketchGeneration_createNew_pos
prompt_sketch_extend_sd_neg = prompt_sketchGeneration_createNew_neg

# 2-4
# 无图
prompt_sketch_toSketch_sd_pos_1 = ('(a pencil sketch of a {mainbody}:1.4)(lineart:1.2),(monochrome:1.1),white background,one-hour rough draft,complete view,ideas,sketch,crosshatch,contour lines and structural lines,')
prompt_sketch_toSketch_sd_neg_1 = prompt_sketchGeneration_createNew_neg
# 有图
prompt_sketch_toSketch_sd_pos_2 = ('pencil sketch,lineart,monochrome,white background,one-hour rough draft,complete view,ideas,sketch,crosshatch,contour lines and structural lines,hand-drawn sketching')
prompt_sketch_toSketch_sd_neg_2 = ('(photorealistic:1.2),color,realistic,worst quality,people,man,woman,lowres,cropped,text,jpeg,signature,watermark,username,cartoon,duplicate,anime,blurry,(out of frame:1.1),ugly,deformed,Easy Negative,weird structure,unreasonable product,finely detailed,flame,grey,Blocks of color shaded with a pencil.,product model,book,paper,pencil,hands,(incomplete product:1.3)')

# 3-1
prompt_model_createNew_sd_pos = ('(A white clay model of a {mainbody}:1.3),complete view,polycount,shading,gadget,with accurate features,white background,blender,c4d,clear structure,autodesk inventor,an ambient occlusion render,parting lines,structural lines,monochrome,parametric design,(white model:1.1),')
prompt_model_createNew_sd_neg = ('(out of frame:1.1),(weird structure:1.2),(unreasonable:1.1),(product image:1.1),(colorful:1.3),ugly,deformed,Easy Negative,photorealistic,sketch,drawing,draft,texture,material,metal,plastic,black,logo,text,signature,words,worst quality,Light reflection,incomplete product,weird structure,unreasonable product,wrong parting lines,shadow,architecture,blurry,colorful,duplicate,')

# 3-4
prompt_model_toModel_sd_pos_1 = ('(A white clay model:1.3),complete view,polycount,shading,gadget,with accurate features,white background,blender,c4d,clear structure,autodesk inventor,an ambient occlusion render,parting lines,structural lines,monochrome,parametric design,(white model:1.1),')
prompt_model_toModel_sd_neg_1 = prompt_model_createNew_sd_neg

prompt_model_toModel_sd_pos_2 = prompt_model_toModel_sd_pos_1
prompt_model_toModel_sd_neg_2 = prompt_model_createNew_sd_neg


# 4-1
prompt_rendering_createNew = ("""
#任务简介#我将告诉提供给你一个JSON格式的预输入，根据这段预输入文本，为我生成用于在stable diffusion生成场景图像的prompt。
#任务要求#stable diffusion是一款利用深度学习进行文生图的模型，支持通过使用prompt来产生新的图像，描述要包含或省略的元素。

下面我将说明输入的形式，输入的键包括：
- designTask(必须项)：文本，一段关于设计任务的描述。

下面我将说明prompt的生成要求:
（1）这里的prompt主要用于描述某个产品的使用场景，场景内不包括该产品。
（2）首先需要将场景的内容翻译为英文，作为prompt的一部分。
（3）prompt还需要对场景中的细节、场景光线、视角的描述，细节越多越好。
（4）使用英文短句来描述。
（5）使用英文半角,做分隔符分隔提示词，每个提示词不要带引号。
（6）prompt中不能含有-和，单词不能重复。

#案例#
当预输入是{{"designTask": "设计一款户外徒步产品"}}时，输出为：
{{
"prompt": "forest, grass, trees, moss, sunlight, distant, morning, quietness"
}}

#输出要求#只需要输出提示词的内容，使用JSON列表输出，每一次输出为一个元素，不要有其他任何文本，包括对提示词的解释内容。
                                
#输入#
designTask: {designTask}                      
""")

rendering_createNew_sd_pos = (
    '((({sd_prompt_in}))),'
    '(photorealistic:1.5),bestquality,ultradetailed,masterpiece,realistic,finely detailed,purism,minimalism,4k'
)

rendering_createNew_sd_neg = (
    '(worst quality:1.4),people,man,woman,flame,Cloud,(low quality:1.4),(normal quality:1.5),lowres,((monochrome)),((grayscale)),cropped,text,jpeg,artifacts,signature,watermark,username,sketch,cartoon,drawing,anime,duplicate,blurry,semi-realistic,out of frame,ugly,deformed,weird colors,EasyNegative,flame'
)

# 4-2
rendering_refine_sd_pos = ('(({mainbody})),white background,(Product Design:1.3),intelligent,industrial products,Creative,Industrial Products,sense of future,complete view,High Quality,minimalistic futuristic design,emauromin style,finely detailed,64k,blender,purism,ue 5,minimalism,photorealistic')
rendering_refine_sd_neg = ('(worst quality:1.4),people,man,woman,flame,Cloud,(low quality:1.4),(normal quality:1.2),lowres,((grayscale)),cropped,text,jpeg,artifacts,signature,watermark,username,sketch,cartoon,drawing,duplicate,anime,blurry,semi-realistic,(out of frame:1.3),ugly,deformed,weird colors,Easy Negative,flame,(incomplete product:1.8)')


# 4-4
rendering_toRendering_sd_pos_1 = ('(({mainbody})),white background,(Product Design:1.3),intelligent,industrial products,Creative,Industrial Products,sense of future,complete view,High Quality,minimalistic futuristic design,emauromin style,finely detailed,64k,blender,purism,ue 5,minimalism,photorealistic')
rendering_toRendering_sd_neg_1 = ('(worst quality:1.4),people,man,woman,flame,Cloud,(low quality:1.4),(normal quality:1.2),lowres,((grayscale)),cropped,text,jpeg,artifacts,signature,watermark,username,sketch,cartoon,drawing,duplicate,anime,blurry,semi-realistic,(out of frame:1.3),ugly,deformed,weird colors,Easy Negative,flame,(incomplete product:1.8),Highly saturated colors,unsuitable for product design')


rendering_toRendering_sd_pos_2 = ('(({mainbody})),white background,(Product Design:1.3),intelligent,industrial products,Creative,Industrial Products,sense of future,complete view,High Quality,minimalistic futuristic design,emauromin style,finely detailed,64k,blender,purism,ue 5,minimalism,photorealistic')
rendering_toRendering_sd_neg_2 = ('(worst quality:1.4),people,man,woman,flame,Cloud,(low quality:1.4),(normal quality:1.2),lowres,((grayscale)),cropped,text,jpeg,artifacts,signature,watermark,username,sketch,cartoon,drawing,duplicate,anime,blurry,semi-realistic,(out of frame:1.3),ugly,deformed,weird colors,Easy Negative,flame,(incomplete product:1.8),Highly saturated colors,unsuitable color for product design')
