"use client";

import React, { ReactNode, useEffect, useRef, useState } from "react";
import {
  Button,
  Input,
  Select,
  Radio,
  Alert,
  message,
  FloatButton,
} from "antd";
import { DownloadOutlined, CloudUploadOutlined } from "@ant-design/icons";
import classNames from "classnames";
import {
  ADD_SCHEME,
  SWITCH_STAGE,
  UPDATE_CURRENT_SCHEME,
  UPDATE_DESIGN_TASK,
  UPDATE_USER_NAME,
  UPDATE_NUM,
  usePaintContext,
} from "@/app/page/provider";
import "./page.css";
import {
  Stage,
  AIStage,
  AIAlertSetting,
  buttonsConfig,
  StageSwitchRecords,
  AIStageSwitchRecords,
  AIStageToStageMapping,
  BackendItem,
  backendContents as initialBackendContents,
} from "@/app/page/config";
import { LeftSide, LeftSideHandler } from "./(left-side)";

import NavBar from "@/components/NavBar";
import {
  start,
  submitSelection,
  handleSendTimingRecords,
} from "@/services/paint";
import BackendContentDisplay from "@/components/BackendContentDisplay";
import { imageUrlToBase64 } from "@/lib/utils";
import axios from "axios";
import { baseUrl } from "@/configs/env";

const { TextArea } = Input;
const { Option } = Select;

interface HeaderProps {
  children: ReactNode;
}

const Header: React.FC<HeaderProps> = ({ children }) => {
  return (
    <div className="relative flex items-center h-[50px] justify-between border-b border-[#F3F4F8]">
      {children}
    </div>
  );
};

// 重要的控制判断函数
export function isReady(stage: Stage) {
  return stage !== Stage.NotReady;
}

export function isAble(stage: Stage) {
  return stage !== Stage.Unable;
}

export function notFinish(stage: Stage) {
  return stage !== Stage.Finish;
}

export function isDrawing(stage: Stage) {
  return isReady(stage) && isAble(stage) && notFinish(stage);
}

export default function Page() {
  // 获取全局状态数据
  const { state: paintContext, dispatch } = usePaintContext();
  const {
    username,
    currentStage,
    currentAIStage,
    designTask,
    designSchemes,
    // num,
    selectedTexts,
    selectedCanvasRecords,
  } = paintContext;

  // 页面用到的内容 / 辅助变量
  const [currentUsername, setCurrentUsername] = useState(username);
  const [currentDesignTaskInput, setCurrentDesignTaskInput] =
    useState(designTask);
  const [currentNum, setCurrentNum] = useState(1);

  const leftSideRef = useRef(null);
  const leftSideContainerRef = useRef<LeftSideHandler | null>(null);
  const [showLeftAlert, setShowLeftAlert] = useState(true);

  const [currentAIMessage, setCurrentAIMessage] = useState<string | null>(null);
  const [messageApi, messageHolder] = message.useMessage();

  const [showPopover, setShowPopover] = useState(false);
  const [clickedImgUrl, setClickedImgUrl] = useState("");
  const [aiStageCopied, setAIStageCopied] = useState("");

  const [selectedButtonInfo, setSelectedButtonInfo] = useState({
    buttonText: "",
    aiStage: "",
  });

  const [backendContents, setBackendContents] = useState<
    Record<AIStage, BackendItem[]>
  >(initialBackendContents);
  const [submissionMarkers, setSubmissionMarkers] = useState([0]); // 默认第一次提交为0

  // 处理图片点击
  const handleImageClick = (imgUrl: React.SetStateAction<string>) => {
    // 设置被点击的图片 URL
    setClickedImgUrl(imgUrl);
    // 显示 Popover
    setShowPopover(true);
    // 设置延时关闭
    setTimeout(() => {
      setShowPopover(false);
    }, 2000); // 2秒后关闭
  };

  // 放至工作区
  const handleSendToWorkSpace = async () => {
    const currentAIStage = paintContext.currentAIStage;
    const mappedStage = AIStageToStageMapping[paintContext.currentAIStage];
    if (mappedStage) {
      const newIndex = paintContext.designSchemes[mappedStage]?.length ?? 0;

      dispatch({ type: "ADD_SCHEME", payload: { stage: mappedStage } });
      dispatch({
        type: "UPDATE_CURRENT_SCHEME",
        payload: { index: newIndex, stage: mappedStage },
      });
      dispatch({
        type: "UPDATE_SCHEME_BACKGROUND_IMG_URL",
        payload: {
          stage: mappedStage,
          index: newIndex,
          backgroundImageUrl: await imageUrlToBase64(clickedImgUrl),
        },
      });
      console.log(
        `在 ${mappedStage} 阶段中新建了一个 scheme 并为其设置了背景图像 ${clickedImgUrl}`
      );
      setAIStageCopied(currentAIStage);
    } else {
      console.error("未找到对应的 Stage，无法添加新 scheme");
    }

    switchStage(mappedStage);

    setShowPopover(false);
  };

  //计时用参数
  // 定义全局计时起点状态
  const [globalStartTime, setGlobalStartTime] = useState<number | null>(null);
  // 状态初始化
  const [stageSwitchRecords, setStageSwitchRecords] =
    useState<StageSwitchRecords>({});
  const [aiStageSwitchRecords, setAIStageSwitchRecords] =
    useState<AIStageSwitchRecords>({});
  // 当用户满足 isReady(currentStage) 条件时初始化全局计时和第一个 Stage/AIStage 的计时
  useEffect(() => {
    if (isReady(currentStage) && globalStartTime === null) {
      const now = Date.now();
      setGlobalStartTime(now);

      // 初始化当前 Stage 和 AIStage 的计时记录
      setStageSwitchRecords({
        [currentStage]: [{ startTime: now }],
      });
      setAIStageSwitchRecords({
        [currentAIStage]: [{ startTime: now }],
      });
    }
  }, [currentStage, currentAIStage, globalStartTime]);

  // FloatButton组件的onClick处理器
  const handleSubmitTime = async () => {
    try {
      await handleSendTimingRecords({
        username,
        stageSwitchRecords,
        aiStageSwitchRecords,
      });
      console.log("提交！用户的设计环境", stageSwitchRecords);
      console.log("提交！AI辅助的设计环境", aiStageSwitchRecords);
      message.success("提交计时成功", 2.5);
    } catch (error) {
      console.error("提交计时记录时出错:", error);
      message.error("提交计时失败", 2.5);
    }
  };

  // 切换当前阶段
  const switchStage = async (toStage: Stage) => {
    const now = Date.now();

    // 如果当前在画画，保存当前进度
    if (isDrawing(currentStage)) {
      if (leftSideContainerRef.current) {
        await leftSideContainerRef.current?.saveImage();
      }
    }

    // 直接切换
    if (
      toStage === Stage.DesignBrief ||
      toStage === Stage.Sketch ||
      toStage === Stage.ModelImage ||
      toStage === Stage.Rendering
    ) {
      // 更新当前 Stage 的结束时间
      setStageSwitchRecords((prevRecords) => {
        const currentRecords = prevRecords[currentStage];
        if (currentRecords && currentRecords.length > 0) {
          // 更新最后一个记录的持续时间
          currentRecords[currentRecords.length - 1].duration =
            now - currentRecords[currentRecords.length - 1].startTime;
        }

        // 为新的 Stage 添加新的计时记录
        const newRecord = { startTime: now };
        const updatedRecords = {
          ...prevRecords,
          [toStage]: [...(prevRecords[toStage] || []), newRecord],
        };

        return updatedRecords;
      });

      dispatch({
        type: SWITCH_STAGE,
        payload: {
          stage: toStage,
        },
      });
    }
  };

  // 检查计时
  // useEffect(() => {
  //   // 遍历所有阶段的记录
  //   Object.entries(stageSwitchRecords).forEach(([stage, records]) => {
  //     console.log(`阶段 ${stage} 的切换记录:`);
  //     records.forEach((record, index) => {
  //       console.log(`第 ${index + 1} 次切换：开始时间 ${new Date(record.startTime).toLocaleTimeString()}，持续时间 ${record.duration ? `${record.duration} 毫秒` : '正在计时...'}`);
  //     });
  //   });
  // }, [stageSwitchRecords]);

  // 切换阶段后
  useEffect(() => {
    if (isDrawing(currentStage)) {
      // 如果目标阶段方案数量为0（第一次切换到该阶段），加入一个方案
      if (designSchemes[currentStage]?.length === 0) {
        dispatch({
          type: ADD_SCHEME,
          payload: {
            stage: currentStage,
          },
        });
      }
      dispatch({
        type: UPDATE_CURRENT_SCHEME,
        payload: { index: 0, stage: currentStage },
      });
    }
  }, [currentStage]);

  // 用户信息填写
  const handleClickInputUsernameButton = async () => {
    if (currentUsername && currentUsername.length > 0) {
      // 改变设计任务
      dispatch({
        type: UPDATE_USER_NAME,
        payload: {
          username: currentUsername,
        },
      });
      console.log("当前的实验编号：", currentUsername);
      // 获取用户信息
      // const userInfo = await start({ username: currentUsername });
      // 更新操作信息
      // if (userInfo) {
      //   dispatch({
      //     type: LOAD_STATE,
      //     payload: {
      //       username: currentUsername,
      //       data: userInfo,
      //     },
      //   });
      // }
    }
  };
  // 设计目标填写
  const handleClickFinishInputButton = async () => {
    if (currentDesignTaskInput && currentDesignTaskInput.length > 0) {
      // 改变阶段
      await switchStage(Stage.DesignBrief);
      // 改变设计任务
      dispatch({
        type: UPDATE_DESIGN_TASK,
        payload: {
          designTask: currentDesignTaskInput,
        },
      });
      console.log("当前的设计任务：", currentDesignTaskInput);
    }
  };

  useEffect(() => {
    if (designTask && designTask.length) {
      switchStage(Stage.DesignBrief);
    }
  }, [designTask]);

  // AI生成的刺激个数
  const handleClickRadioButton = async (selectedNum: number) => {
    dispatch({
      type: UPDATE_NUM,
      payload: {
        num: selectedNum,
      },
    });
    setCurrentNum(selectedNum);
  };

  useEffect(() => {
    console.log("当前的刺激个数：", currentNum);
  }, [currentNum]);

  // 更新AIStage的函数
  const switchAIStage = (newAIStage: any) => {
    const now = Date.now();

    // 先更新当前 AIStage 的结束时间
    setAIStageSwitchRecords((prevRecords) => {
      const currentRecords = prevRecords[paintContext.currentAIStage];
      if (currentRecords && currentRecords.length > 0) {
        // 更新最后一个记录的持续时间
        currentRecords[currentRecords.length - 1].duration =
          now - currentRecords[currentRecords.length - 1].startTime;
      }

      // 为新的 AIStage 添加新的计时记录
      const newRecord = { startTime: now };
      const updatedRecords = {
        ...prevRecords,
        [newAIStage]: [...(prevRecords[newAIStage] || []), newRecord],
      };

      return updatedRecords;
    });

    dispatch({ type: "UPDATE_ACTIVE_BUTTON", payload: null });
    setCurrentAIMessage(null); // 清空当前消息，显示默认消息
    dispatch({
      type: "UPDATE_CURRENT_AISTAGE",
      payload: newAIStage,
    });
    console.log("当前的AI阶段：", newAIStage);
  };

  const getNewMessageForButtonId = (
    buttonId: string,
    currentAIStage?: keyof typeof buttonsConfig
  ) => {
    console.log(
      "Getting message for buttonId:",
      buttonId,
      "in AIStage:",
      currentAIStage
    );
    if (!currentAIStage || !buttonsConfig[currentAIStage]) {
      console.error(`No buttons config found for stage: ${currentAIStage}`);
      return null; // 返回一个默认值或者错误提示
    }

    const button = buttonsConfig[currentAIStage].find(
      (button) => button.id === buttonId
    );
    return button ? button.message : null;
  };

  // 工具按钮
  const handleButtonClick = (
    buttonText: string,
    aiStage: AIStage,
    buttonId: string
  ) => {
    console.log(
      "buttonText:",
      buttonText,
      "aiStage:",
      aiStage,
      "buttonId:",
      buttonId
    );

    // 使用全局状态中的activeButton来决定是否取消选择或选择新按钮
    if (paintContext.activeButton === buttonId) {
      // 如果当前点击的按钮已经是激活状态，则取消选择
      dispatch({ type: "UPDATE_ACTIVE_BUTTON", payload: null });
      setCurrentAIMessage(null); // 清空当前消息，显示默认消息
      setSelectedButtonInfo({ buttonText: "", aiStage: "" });
    } else {
      // 否则，设置为新的激活按钮
      dispatch({ type: "UPDATE_ACTIVE_BUTTON", payload: buttonId });
      setSelectedButtonInfo({ buttonText, aiStage });

      // 根据buttonId获取新的消息
      const newMessage = getNewMessageForButtonId(buttonId, currentAIStage);
      setCurrentAIMessage(newMessage);

      // 如果满足特定条件，设置currentNum为1
      if (currentAIStage === AIStage.DesignBrief && buttonId === "extend") {
        setCurrentNum(1);
      }
      if (currentAIStage === AIStage.Sketch && buttonId === "refine") {
        setCurrentNum(1);
      }
    }
  };

  // 取消选择的处理函数
  const handleCancel = () => {
    dispatch({ type: "UPDATE_ACTIVE_BUTTON", payload: null });
    setCurrentAIMessage(null);
    // 清空选中的文本索引和文本内容
    dispatch({
      type: "UPDATE_SELECTED_TEXTS_AND_INDICES",
      payload: { selectedIndices: [], selectedTexts: [] },
    });
    dispatch({ type: "UPDATE_SELECTED_CANVAS_RECORDS", payload: [] });

    console.log("取消操作");
  };

  // 提交按钮
  const handleSubmit = async () => {
    dispatch({ type: "UPDATE_ACTIVE_BUTTON", payload: null });
    setCurrentAIMessage(null);

    // 显示加载中的消息，并保存返回的隐藏函数
    const hideLoadingMessage = message.loading("生成中...", 0);

    try {
      // 调用 submitSelection 发送数据到后端
      const submitResult = await submitSelection({
        username,
        currentNum,
        designTask,
        currentAIStage,
        currentStage,
        selectedTexts,
        selectedCanvasRecords,
        selectedButtonInfo,
      });
      console.log("提交成功，后端返回的数据：", submitResult);

      // 更新内容显示
      updateBackendContents(submitResult);

      message.success("生成成功", 2.5);
    } catch (error) {
      console.error("提交失败：", error);
      message.error("生成失败，请稍后再试", 2.5);
    } finally {
      // 无论成功还是失败，都隐藏加载中的消息
      hideLoadingMessage();
    }
  };

  // 控制台检验
  useEffect(() => {
    console.log("当前的实验编号：", username);
    console.log("当前的设计任务：", designTask);
    console.log("当前的刺激个数：", currentNum);
    console.log("当前选中的文本:", selectedTexts);
    console.log("当前选中的画布记录:", selectedCanvasRecords);
  }, [selectedTexts, selectedCanvasRecords]);

  useEffect(() => {
    // 这里的代码会在 backendContents 更新后执行
    console.log("Updated backendContents:", backendContents);
  }, [backendContents]); // 依赖项数组中添加 backendContents

  // 更新后端内容
  const updateBackendContents = (newContents: any) => {
    // 判断 newContents 是否为数组类型，从而确定是否包含多条内容
    const isMultiple = Array.isArray(newContents);

    // 生成当前时间戳
    const timestamp = new Date().toISOString();

    // 初始化一个空数组来存储拆分后的内容
    let newBackendItems: BackendItem[] = [];

    // 定义一个检查是否为图片对象的函数
    const isImageObject = (data: any) => {
      return (
        typeof data === "object" &&
        Object.values(data).every(
          (item) =>
            typeof item === "string" && item.match(/\.(jpeg|jpg|gif|png)$/)
        )
      );
    };

    // 根据内容是单条还是多条进行处理
    if (isMultiple) {
      // 处理多条内容
      newContents.forEach((content: any) => {
        // 判断内容类型
        const dataType = isImageObject(content) ? "image" : "json";
        newBackendItems.push({
          type: dataType,
          timestamp: timestamp,
          data: content,
          aiStage: currentAIStage,
        });
      });
    } else {
      // 处理单条内容
      const dataType = isImageObject(newContents) ? "image" : "json";
      newBackendItems.push({
        type: dataType,
        timestamp: timestamp,
        data: newContents,
        aiStage: currentAIStage,
      });
    }

    // 更新内容状态
    setBackendContents((prevContents) => {
      const updatedContents = { ...prevContents };

      // 直接为当前AIStage添加内容到数组的开头
      updatedContents[currentAIStage] = [
        ...newBackendItems, // 将新内容添加到开头
        ...updatedContents[currentAIStage], // 然后是旧内容
      ];

      return updatedContents;
    });

    // 更新分隔线位置，仅对当前AIStage操作
    setSubmissionMarkers((prevMarkers) => [
      ...prevMarkers,
      prevMarkers[prevMarkers.length - 1] + newBackendItems.length, // 根据添加的新项目数量更新分隔线位置
    ]);
  };

  const renderButtons = () => {
    return buttonsConfig[currentAIStage].map(
      ({ id, text, svgPath, disabled }) => (
        <Button
          key={id}
          className={`customButton ${
            paintContext.activeButton === id ? "active" : ""
          }`}
          onClick={() =>
            !disabled && handleButtonClick(text, currentAIStage, id)
          }
          disabled={disabled}
        >
          <svg
            width="33"
            height="24"
            viewBox="0 0 33 33"
            fill="none"
            xmlns="http://www.w3.org/2000/svg"
          >
            <path
              d={svgPath}
              fill={
                disabled
                  ? "#D8D8D8"
                  : paintContext.activeButton === id
                  ? "var(--primary-color)"
                  : "#444444"
              }
            />
          </svg>
          <span
            className="buttonText"
            style={{
              color: disabled
                ? "#D8D8D8"
                : paintContext.activeButton === id
                ? "var(--primary-color)"
                : "#444444",
            }}
          >
            {text}
          </span>
        </Button>
      )
    );
  };

  // 放至工作区
  const handleSendToWorkSpace2 = async (uploadImgUrl: string) => {
    const newIndex = paintContext.designSchemes[currentStage]?.length ?? 0;

    dispatch({ type: "ADD_SCHEME", payload: { stage: currentStage } });
    dispatch({
      type: "UPDATE_CURRENT_SCHEME",
      payload: { index: newIndex, stage: currentStage },
    });
    dispatch({
      type: "UPDATE_SCHEME_BACKGROUND_IMG_URL",
      payload: {
        stage: currentStage,
        index: newIndex,
        backgroundImageUrl: await imageUrlToBase64(uploadImgUrl), // 直接使用URL
      },
    });
    console.log(
      `在 ${currentStage} 阶段中新建了一个 scheme 并为其设置了背景图像 ${uploadImgUrl}`
    );
};

const handleFileUpload = (event) => {
  const file = event.target.files[0]; // 获取文件
  const formData = new FormData();
  formData.append("file", file); 

  // 发送请求到后端
  axios
    .post(`${baseUrl}/uploadImage`, formData, 
    // {
    //   headers: {
    //     "Content-Type": "multipart/form-data",
    //   },
    // }
    )
    .then((response) => {
      // 处理成功的情况
      console.log("File uploaded successfully:", response.data);
      // 更新背景图
      const uploadImgUrl = response.data.url; // 修改这里，使用正确的键 'url'
      console.log(uploadImgUrl);
      handleSendToWorkSpace2(uploadImgUrl); // 调用函数更新背景图
    })
    .catch((error) => {
      // 处理错误的情况
      console.error("Error uploading file:", error);
    });
};



  return (
    <div className="flex flex-col w-[100%] md:flex-row mt-[2%] mb-[2%] bg-white">
      {messageHolder}

      {/* Left Navigation */}
      <div className="md:w-[15%] md:mr-[0.75%] border-r border-ebecf2 rounded-r-lg shadow-custom">
        <NavBar />
        <div className="p-[12px]">
          <span className="sub-title mb-[12px]">实验编号</span>
          {!username?.length ? (
            <>
              <TextArea
                className="rounded-md border border-[#F3F4F8] text-2 w-[100%]"
                value={currentUsername}
                onChange={(e) => setCurrentUsername(e.target.value)}
                placeholder="请输入实验编号"
                variant="borderless"
                style={{
                  height: "28px",
                  resize: "none",
                  backgroundColor: "#F4F5F8",
                }}
              />
              <Button
                // style={{
                //   borderRadius: "6px",
                //   border: "1px solid #DFDFDF",
                //   background: "#FFF",
                //   color: "#444444",
                // }}
                // size={"small"}
                onClick={handleClickInputUsernameButton}
                className="w-[100%] text-2 mt-2 mb-[48px]"
              >
                确认
              </Button>
            </>
          ) : (
            <div className="text-2 text-[#8F949B] mt-[12px] mb-[48px]">
              {username}
            </div>
          )}
          <span className="sub-title mb-[12px]">设计任务描述</span>
          {currentStage === Stage.NotReady && !designTask?.length ? (
            <>
              <TextArea
                className="rounded-md border border-[#F3F4F8] text-2 w-[100%]"
                value={currentDesignTaskInput}
                onChange={(e) => setCurrentDesignTaskInput(e.target.value)}
                placeholder="请输入设计任务"
                variant="borderless"
                style={{
                  height: "120px",
                  resize: "none",
                  backgroundColor: "#F4F5F8",
                }}
              />
              <Button
                // style={{
                //   borderRadius: "6px",
                //   border: "1px solid #444444",
                //   background: "#FFF",
                //   color: "#444444",
                // }}
                onClick={handleClickFinishInputButton}
                className="w-[100%] text-2 mt-2"
              >
                完成
              </Button>
            </>
          ) : (
            <div className="text-2 text-[#8F949B] mt-[12px] mb-[48px]">
              {designTask}
            </div>
          )}
          {isReady(currentStage) && (
            <span className="text-2 text-[#444444] mt-[12px] mb-[48px]">
              <div
                className="sub-title mb-[12px]"
                style={{ textAlign: "left" }}
              >
                AI生成刺激的个数
              </div>
              <div className="flex flex-row justify-start items-center mb-4">
                <Radio.Group
                  defaultValue={1}
                  value={currentNum}
                  buttonStyle="solid"
                  onChange={(e) =>
                    handleClickRadioButton(Number(e.target.value))
                  }
                >
                  <Radio.Button value={1}>1</Radio.Button>
                  <Radio.Button value={2}>2</Radio.Button>
                  <Radio.Button value={3}>3</Radio.Button>
                </Radio.Group>
              </div>
            </span>
          )}
        </div>
      </div>

      {/* Right Content */}
      <div className="flex flex-col md:flex-row w-full">
        {/* Drawing Canvas */}
        <div className="flex-1 flex flex-col border border-ebecf2 rounded-lg shadow-custom">
          <Header>
            <div className="flex items-center justify-center pl-[22px]">
              <span
                className={classNames("title", {
                  "text-grey": !isReady(currentStage),
                })}
              >
                工作区
              </span>
            </div>
            {isReady(currentStage) && (
              <div className="absolute right-[20px] flex items-center justify-center">
                <Select
                  value={currentStage}
                  style={{ width: 200 }}
                  onChange={(value) => {
                    console.log(value); // 这里可以看到选中项的值
                    switchStage(value);
                  }}
                >
                  <Option value={Stage.DesignBrief}>{Stage.DesignBrief}</Option>
                  <Option value={Stage.Sketch}>{Stage.Sketch}</Option>
                  <Option value={Stage.ModelImage}>{Stage.ModelImage}</Option>
                  <Option value={Stage.Rendering}>{Stage.Rendering}</Option>
                </Select>
              </div>
            )}
          </Header>

          <LeftSide
            ref={leftSideContainerRef}
            leftSideRef={leftSideRef}
            setShowLeftAlert={setShowLeftAlert}
            showLeftAlert={showLeftAlert}
          />
        </div>

        {/* Backend Output */}
        <div className="flex-1 flex flex-col border border-ebecf2 rounded-lg shadow-custom md:ml-[0.75%]">
          <Header>
            <div className="flex items-center justify-center pl-[22px]">
              <span
                className={classNames("title", {
                  "text-grey": !isReady(currentStage),
                })}
              >
                AI灵感助手
              </span>
            </div>
            {/*AIStage切换*/}
            {isReady(currentStage) && (
              <div className="absolute right-[20px] flex items-center justify-center">
                <Select
                  defaultValue={AIStage.DesignBrief}
                  style={{ width: 180 }}
                  onChange={switchAIStage}
                >
                  <Option value={AIStage.DesignBrief}>
                    {AIStage.DesignBrief}
                  </Option>
                  <Option value={AIStage.Sketch}>{AIStage.Sketch}</Option>
                  <Option value={AIStage.ModelImage}>
                    {AIStage.ModelImage}
                  </Option>
                  <Option value={AIStage.Rendering}>{AIStage.Rendering}</Option>
                </Select>
              </div>
            )}
          </Header>

          {/* 提示文本 */}
          <div className="flex flex-row items-center space-x-2 mt-3 px-5">
            {isReady(currentStage) && (
              <div className="alert-animation">
                <Alert
                  type="info"
                  message={
                    currentAIMessage ||
                    AIAlertSetting[
                      currentAIStage as keyof typeof AIAlertSetting
                    ]?.message
                  }
                  showIcon={true}
                  icon={
                    AIAlertSetting[
                      currentAIStage as keyof typeof AIAlertSetting
                    ].icon
                  }
                  style={{
                    display: "inline-flex",
                    alignItems: "flex-start",
                    borderRadius: "10px",
                    border: `1px solid ${
                      currentAIStage === AIStage.DesignBrief
                        ? "var(--DB-color)"
                        : currentAIStage === AIStage.Sketch
                        ? "var(--S-color)"
                        : currentAIStage === AIStage.ModelImage
                        ? "var(--MI-color)"
                        : currentAIStage === AIStage.Rendering
                        ? "var(--R-color)"
                        : "#444444"
                    }`,
                    background:
                      currentAIStage === AIStage.DesignBrief
                        ? "--DB-background"
                        : currentAIStage === AIStage.Sketch
                        ? "--S-background"
                        : currentAIStage === AIStage.ModelImage
                        ? "--MI-background"
                        : currentAIStage === AIStage.Rendering
                        ? "--R-background"
                        : "#FFFFFF",
                    width: "100%",
                  }}
                  className="tip-text"
                />
              </div>
            )}
          </div>

          {/* 功能按钮 */}
          {isReady(currentStage) && (
            <div className="flex flex-row items-center justify-between space-x-2 px-5">
              {currentAIStage === AIStage.DesignBrief && (
                <>
                  <div className="flex flex-row items-center space-x-2 mt-3">
                    <div className="flex flex-row items-center space-x-2">
                      {renderButtons()}
                    </div>
                    <div className="flex flex-col space-y-2">
                      {/* 提交按钮 */}
                      <Button
                        type="primary"
                        onClick={handleSubmit}
                        disabled={!paintContext.activeButton}
                        style={{
                          width: "180px",
                          height: "50px",
                          borderRadius: "8px 8px 0 0", // 设置上面的圆角
                          marginBottom: "0", // 移除按钮之间的默认间距
                        }}
                      >
                        提交
                      </Button>
                      {/* 取消按钮 */}
                      <Button
                        onClick={handleCancel}
                        disabled={!paintContext.activeButton}
                        style={{
                          width: "180px",
                          height: "30px",
                          borderRadius: "0 0 8px 8px", // 设置下面的圆角
                          marginTop: "-1px", // 重叠边界以移除间距
                        }}
                      >
                        取消
                      </Button>
                    </div>
                  </div>
                </>
              )}
              {currentAIStage === AIStage.Sketch && (
                <>
                  <div className="flex flex-row items-center space-x-2 mt-3">
                    <div className="flex flex-row items-center space-x-2">
                      {renderButtons()}
                    </div>
                    <div className="flex flex-col space-y-2">
                      {/* 提交按钮 */}
                      <Button
                        type="primary"
                        onClick={handleSubmit}
                        disabled={!paintContext.activeButton}
                        style={{
                          width: "180px",
                          height: "50px",
                          borderRadius: "8px 8px 0 0", // 设置上面的圆角
                          marginBottom: "0", // 移除按钮之间的默认间距
                        }}
                      >
                        提交
                      </Button>
                      {/* 取消按钮 */}
                      <Button
                        onClick={handleCancel}
                        disabled={!paintContext.activeButton}
                        style={{
                          width: "180px",
                          height: "30px",
                          borderRadius: "0 0 8px 8px", // 设置下面的圆角
                          marginTop: "-1px", // 重叠边界以移除间距
                        }}
                      >
                        取消
                      </Button>
                    </div>
                  </div>
                </>
              )}
              {currentAIStage === AIStage.ModelImage && (
                <>
                  <div className="flex flex-row items-center space-x-2 mt-3">
                    <div className="flex flex-row items-center space-x-2">
                      {renderButtons()}
                    </div>
                    <div className="flex flex-col space-y-2">
                      {/* 提交按钮 */}
                      <Button
                        type="primary"
                        onClick={handleSubmit}
                        disabled={!paintContext.activeButton}
                        style={{
                          width: "180px",
                          height: "50px",
                          borderRadius: "8px 8px 0 0", // 设置上面的圆角
                          marginBottom: "0", // 移除按钮之间的默认间距
                        }}
                      >
                        提交
                      </Button>
                      {/* 取消按钮 */}
                      <Button
                        onClick={handleCancel}
                        disabled={!paintContext.activeButton}
                        style={{
                          width: "180px",
                          height: "30px",
                          borderRadius: "0 0 8px 8px", // 设置下面的圆角
                          marginTop: "-1px", // 重叠边界以移除间距
                        }}
                      >
                        取消
                      </Button>
                    </div>
                  </div>
                </>
              )}
              {currentAIStage === AIStage.Rendering && (
                <>
                  <div className="flex flex-row items-center space-x-2 mt-3">
                    <div className="flex flex-row items-center space-x-2">
                      {renderButtons()}
                    </div>
                    <div className="flex flex-col space-y-2">
                      {/* 提交按钮 */}
                      <Button
                        type="primary"
                        onClick={handleSubmit}
                        disabled={!paintContext.activeButton}
                        style={{
                          width: "180px",
                          height: "50px",
                          borderRadius: "8px 8px 0 0", // 设置上面的圆角
                          marginBottom: "0", // 移除按钮之间的默认间距
                        }}
                      >
                        提交
                      </Button>
                      {/* 取消按钮 */}
                      <Button
                        onClick={handleCancel}
                        disabled={!paintContext.activeButton}
                        style={{
                          width: "180px",
                          height: "30px",
                          borderRadius: "0 0 8px 8px", // 设置下面的圆角
                          marginTop: "-1px", // 重叠边界以移除间距
                        }}
                      >
                        取消
                      </Button>
                    </div>
                  </div>
                </>
              )}
            </div>
          )}

          {/* 生成内容显示 */}
          <div className="mt-4 mb-4 px-5 overflow-y-auto max-h-[calc(100%-32px)]">
            {isReady(currentStage) && (
              <>
                <BackendContentDisplay
                  contents={backendContents[currentAIStage]}
                  submissionMarkers={submissionMarkers}
                  handleSendToWorkSpace={handleSendToWorkSpace}
                  handleImageClick={handleImageClick}
                  showPopover={showPopover}
                  setShowPopover={setShowPopover}
                  clickedImgUrl={clickedImgUrl}
                />
              </>
            )}
          </div>

          <input
            type="file"
            id="fileInput"
            style={{ display: "none" }}
            onChange={handleFileUpload}
            accept="image/*"
          />

          <FloatButton.Group shape="circle" style={{ right: 24 }}>
            <FloatButton
              icon={<CloudUploadOutlined />}
              onClick={() => document.getElementById("fileInput").click()}
            />
            {/* <FloatButton icon={<DownloadOutlined />} /> */}
            <FloatButton
              type="primary"
              onClick={handleSubmitTime}
            ></FloatButton>
          </FloatButton.Group>

        </div>
      </div>
    </div>
  );
}
