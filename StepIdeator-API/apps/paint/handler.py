from apps.paint.logic import \
designBrief_createNew,designBrief_refine,designBrief_extend,\
sketch_createNew,sketch_refine,sketch_extend,sketch_toSketch,\
model_createNew,model_multiView,model_toModel,\
rendering_createNew,rendering_refine,rendering_extend,rendering_toRendering
from apps.utils import BusinessException, BUSINESS_FAIL
import json

def handle_request(num,designTask,currentAIStage,selectedCanvasRecords,selectedTexts,selectedButtonInfo,username,currentStage):
    print("[Handling request......]")
    try:
        if selectedButtonInfo['aiStage']=='设计摘要的辅助生成':
            if selectedButtonInfo['buttonText']=='生成全新摘要':
                json_in = {
                    "designTask": designTask,
                    "num": num,
                    "selectedTexts": selectedTexts
                }
                result = designBrief_createNew(json_in)
            elif selectedButtonInfo['buttonText']=='现有产品参考':
                json_in = {
                    "designTask": designTask,
                    "num": num,
                    "selectedTexts": selectedTexts
                }
                result = designBrief_refine(json_in)
            elif selectedButtonInfo['buttonText']=='扩展/增加':
                print("in desgin extend")
                json_in = {
                    "designTask": designTask,
                    "num": num,
                    "selectedTexts": selectedTexts
                }
                result = designBrief_extend(json_in)
            else:
                raise BusinessException(BUSINESS_FAIL, '无效的任务类型')
        elif selectedButtonInfo['aiStage']=='草图的辅助生成':
            if selectedButtonInfo['buttonText']=='生成全新草图':
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username
                    }
                tmp=sketch_createNew(json_in)
                paths = tmp['paths']
                result = paths
            elif selectedButtonInfo['buttonText']=='现有产品参考':
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username,
                        "selectedTexts": selectedTexts,
                        "selectedCanvasRecords":selectedCanvasRecords
                    }
                result =sketch_refine(json_in)
            elif selectedButtonInfo['buttonText']=='扩展/添加':
                print("in tuozhan")
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username,
                        "selectedTexts": selectedTexts,
                        "selectedCanvasRecords":selectedCanvasRecords
                    }
                tmp =sketch_extend(json_in)
                paths = tmp['paths']
                result = paths
            elif selectedButtonInfo['buttonText']=='转换为草图':
                print("in zhuanhuan")
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username,
                        "selectedTexts": selectedTexts,
                        "selectedCanvasRecords":selectedCanvasRecords
                }
                tmp=sketch_toSketch(json_in)
                paths = tmp['paths']
                result = paths
                
        elif selectedButtonInfo['aiStage']=='模型图的辅助生成':
            if selectedButtonInfo['buttonText']=='生成全新模型':
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username,
                        "selectedTexts": selectedTexts,
                    }
                tmp=model_createNew(json_in)
                paths = tmp['paths']
                print(paths)
                result = paths
            elif selectedButtonInfo['buttonText']=='多角度拓展':
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username,
                        "selectedTexts": selectedTexts,
                        "selectedCanvasRecords":selectedCanvasRecords
                    }
                tmp=model_multiView(json_in)
                # paths = tmp['paths']
                result = tmp
            elif selectedButtonInfo['buttonText']=='转化为白模图':
                print("in model to model")
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username,
                        "selectedTexts": selectedTexts,
                        "selectedCanvasRecords":selectedCanvasRecords,
                        'userStage':currentStage
                    }
                tmp=model_toModel(json_in)
                paths = tmp['paths']
                print(paths)
                result = paths
            else :
                raise BusinessException(BUSINESS_FAIL, '无效的任务类型')
        elif selectedButtonInfo['aiStage']=='场景与产品渲染图的辅助生成':
            if selectedButtonInfo['buttonText']=='生成全新场景':
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username
                    }
                tmp=rendering_createNew(json_in)
                paths = tmp['paths']
                print(paths)
                result = paths
            elif selectedButtonInfo['buttonText']=='现有产品参考':
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username,
                        "selectedTexts": selectedTexts,
                        "selectedCanvasRecords":selectedCanvasRecords
                    }
                tmp=rendering_refine(json_in)
                paths = tmp['paths']
                print(paths)
                result = paths
            elif selectedButtonInfo['buttonText']=='扩展至场景':
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username,
                        "selectedTexts": selectedTexts,
                        "selectedCanvasRecords":selectedCanvasRecords
                    }
                tmp=rendering_extend(json_in)
                paths = tmp['paths']
                print(paths)
                result = paths
            elif selectedButtonInfo['buttonText']=='转化为渲染图':
                json_in = {
                        "designTask": designTask,
                        "num": num,
                        "username":username,
                        "selectedTexts": selectedTexts,
                        "selectedCanvasRecords":selectedCanvasRecords,
                        'userStage':currentStage
                    }
                tmp=rendering_toRendering(json_in)
                paths = tmp['paths']
                print(paths)
                result = paths
            else:
                raise BusinessException(BUSINESS_FAIL, '无效的任务类型')
        else:
            raise BusinessException(BUSINESS_FAIL, '无效的任务类型')
        return result

    except BusinessException as be:
        raise be
    except Exception as e:
        raise BusinessException(BUSINESS_FAIL, str(e))
