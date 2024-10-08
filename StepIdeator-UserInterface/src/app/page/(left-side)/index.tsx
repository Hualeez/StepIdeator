"use client";

import React, {
  createContext,
  Dispatch,
  forwardRef,
  useContext,
  useEffect,
  useImperativeHandle,
  useRef,
  useState,
} from "react";
import { isReady } from "@/app/page/Main";
import {
  AlertSetting,
  eraseDefaultSize,
  Stage,
  strokeDefaultSize,
} from "@/app/page/config";
import {
  ADD_SCHEME,
  DesignSchemeType,
  UPDATE_CURRENT_SCHEME,
  UPDATE_IMG,
  usePaintContext,
} from "@/app/page/provider";

import { ReactSketchCanvasRef, CanvasPath } from "react-sketch-canvas";
import { Alert, Image } from "antd";
import {
  LeftOutlined,
  PlusCircleOutlined,
  RightOutlined,
} from "@ant-design/icons/lib/icons";
import classNames from "classnames";
import { Canvas, ReactSketchCanvasProps } from "@/app/page/(left-side)/canvas";
import { Toolbox } from "@/app/page/(left-side)/tools";

const CanvasContext = createContext<CanvasContextType | undefined>(undefined);

export const useCanvasContext = (): CanvasContextType => {
  return useContext(CanvasContext) as CanvasContextType;
};

export type CanvasContextType = {
  canvasRef: React.MutableRefObject<ReactSketchCanvasRef | undefined>;
  canvasProps: Partial<ReactSketchCanvasProps>;
  setCanvasProps: React.Dispatch<
    React.SetStateAction<Partial<ReactSketchCanvasProps>>
  >;
  strokeSize: number;
  setStrokeSize: React.Dispatch<React.SetStateAction<number>>;
  strokeColor: string; // 添加的部分
  setStrokeColor: Dispatch<React.SetStateAction<string>>; // 添加的部分
  eraseSize: number;
  setEraseSize: React.Dispatch<React.SetStateAction<number>>;
  selectedTool: Tools;
  setSelectedTool: React.Dispatch<React.SetStateAction<Tools>>;
};

export type LeftSideProps = {
  leftSideRef: React.MutableRefObject<any>;
  showLeftAlert: boolean;
  setShowLeftAlert: React.Dispatch<React.SetStateAction<boolean>>;
};

export interface LeftSideHandler {
  saveImage: () => Promise<void>;
}

export enum Tools {
  Unable,
  Pen,
  StrokeColor,
  Text,
  Erase,
  Others,
}

export const LeftSide = forwardRef<LeftSideHandler, LeftSideProps>(
  (props: LeftSideProps, ref) => {
    const { state: paintContext, dispatch } = usePaintContext();
    const { currentScheme, currentStage, designSchemes } = paintContext;

    let paths: CanvasPath[];
    // if (currentScheme) {
    //   // @ts-ignore
    //   const scheme = designSchemes[currentScheme.stage][
    //     currentScheme.index
    //   ] as DesignSchemeType;
    //   paths = scheme.paths;
    // }
    if (currentScheme) {
      const stageSchemes = designSchemes[currentScheme.stage];
      if (stageSchemes) {
        const scheme = stageSchemes[currentScheme.index];
        if (scheme) {
          const typedScheme = scheme as DesignSchemeType;
          paths = typedScheme.paths;
        } else {
          console.error(`Invalid index: ${currentScheme.index}`);
        }
      } else {
        console.log(designSchemes); // 查看完整的对象
        console.log(designSchemes["设计摘要的环境"]); // 查看特定键的值

        console.log("Available stages:", Object.keys(designSchemes));
        console.log(`Current stage: ${currentScheme.stage}`);
        console.error(`Invalid stage: ${currentScheme.stage}`);
      }
    }

    const { leftSideRef: leftSideRef, showLeftAlert } = props;

    // 画布相关状态
    const [selectedTool, setSelectedTool] = useState(Tools.Text);
    const canvasWrapperRef = useRef(null);
    const canvasRef = useRef<ReactSketchCanvasRef>();
    const [canvasProps, setCanvasProps] = React.useState<
      Partial<ReactSketchCanvasProps>
    >({
      strokeWidth: strokeDefaultSize,
      eraserWidth: eraseDefaultSize,
      strokeColor: "#444444",
      canvasColor: "#FFFFFF",
      allowOnlyPointerType: "all",
    });
    const [strokeSize, setStrokeSize] = useState(strokeDefaultSize);
    const [eraseSize, setEraseSize] = useState(eraseDefaultSize);
    const [strokeColor, setStrokeColor] = useState("#444444"); // 默认黑色

    const stageAbbreviations: Partial<{ [K in Stage]: string }> = {
      设计摘要的环境: "设计摘要",
      草图的环境: "草图",
      模型图的环境: "模型",
      场景与产品渲染图的环境: "渲染",
    };

    // 当组件初始化时设置画布的初始属性
    useEffect(() => {
      // console.log(strokeColor);
      setCanvasProps({
        ...canvasProps,
        strokeColor: strokeColor, // 确保画布颜色随状态更新
      });
    }, [strokeColor]); // 当 strokeColor 改变时重新设置画布属性

    // 缩略图相关事件
    const saveImage = async () => {
      const exportImage = canvasRef.current?.exportImage;

      if (exportImage) {
        const imageData = await exportImage("png");
        dispatch({
          type: UPDATE_IMG,
          payload: {
            stage: currentScheme?.stage,
            schemeIndex: currentScheme?.index,
            imageData,
          },
        });
      }
    };
    // 将该方法暴露给父组件
    useImperativeHandle(ref, () => ({
      saveImage,
    }));
    const switchCurrentScheme = async (stage: Stage, index: number) => {
      // 保存当前的方案
      await saveImage();
      // 切换上下文到当前方案
      dispatch({
        type: UPDATE_CURRENT_SCHEME,
        payload: { index, stage },
      });
    };
    // 切换当前画布
    // 根据当前阶段和当前方案更新方案的上下文
    useEffect(() => {
      // 清除画布
      canvasRef.current?.resetCanvas();
      // 更新画布和文本。只需要导入画布内容。
      if (paths) {
        canvasRef.current?.loadPaths(paths);
      }
    }, [currentStage, currentScheme]);

    const handleClickAddSchemes = async (stage: Stage) => {
      // 必须为当前阶段
      if (stage === currentStage) {
        // 保存当前的方案
        await saveImage();
        // 计算新的索引
        const index = designSchemes[currentStage]?.length ?? 0;
        // 加入新的方案
        dispatch({
          type: ADD_SCHEME,
          payload: {
            stage: stage,
          },
        });
        // 切换上下文到最新方案
        dispatch({
          type: UPDATE_CURRENT_SCHEME,
          payload: { index, stage },
        });
      }
    };

    return (
      <CanvasContext.Provider
        value={{
          canvasRef,
          canvasProps,
          setCanvasProps,
          strokeSize,
          setStrokeSize,
          eraseSize,
          setEraseSize,
          selectedTool,
          setSelectedTool,
          strokeColor,
          setStrokeColor,
        }}
      >
        <div className="flex-grow relative" ref={leftSideRef}>
          <div className="absolute top-[16px] left-[10px] max-w-[52%] z-10">
            {showLeftAlert && (
              <div className="alert-animation">
                <Alert
                  type="info"
                  message={
                    AlertSetting[currentStage as keyof typeof AlertSetting]
                      .message
                  }
                  showIcon={true}
                  icon={
                    AlertSetting[currentStage as keyof typeof AlertSetting].icon
                  }
                  style={{
                    borderRadius: "10px",
                    border: "1px solid #D9D9D9",
                    background: "#FFF",
                    boxShadow: "0px 3px 10px -6px rgba(0, 0, 0, 0.10)",
                    height: "auto",
                  }}
                  className="tip-text"
                />
              </div>
            )}
          </div>

          <div className="absolute top-[0px] right-[0px] ">
            <Toolbox />
          </div>

          {/* 画布 */}
          <div
            className="absolute"
            ref={canvasWrapperRef}
            style={{
              top: "17%",
              left: "6%",
              // left: "50%", // 改变左边距为50%
              // transform: "translateX(-50%)",
              width: "512px", // 设置固定宽度
              height: "512px", // 设置固定高度

              overflow: "hidden",
            }}
          >
            {isReady(currentStage) && currentScheme && (
              <Canvas wrapperRef={canvasWrapperRef} />
            )}
          </div>

          {isReady(currentStage) && (
            <div className="absolute bottom-[16px] left-[20px] right-[20px] flex items-center justify-between">
              <LeftOutlined style={{ fontSize: "18px", color: "#D8D8D8" }} />

              <div className="flex flex-1 justify-start items-center w-[80%] ml-1 mr-1">
                <div
                  className="flex overflow-x-auto overflow-y-hidden justify-start items-center space-x-2 mr-2"
                  style={{ scrollbarWidth: "none", msOverflowStyle: "none" }}
                >
                  {[
                    Stage.DesignBrief,
                    Stage.Sketch,
                    Stage.ModelImage,
                    Stage.Rendering,
                  ].map((stage, index) =>
                    designSchemes[stage]?.length ? (
                      <>
                        <div
                          key={index}
                          className={classNames(
                            "flex-shrink-0 w-[40px] h-[40px] flex items-center justify-center rounded-md",
                            {
                              "bg-[var(--DB-color)]": currentStage === stage && stage === Stage.DesignBrief,
                              "bg-[var(--S-color)]": currentStage === stage && stage === Stage.Sketch,
                              "bg-[var(--MI-color)]": currentStage === stage && stage === Stage.ModelImage,
                              "bg-[var(--R-color)]": currentStage === stage && stage === Stage.Rendering,
                              "bg-[#F3F4F8]": currentStage !== stage, 
                            }
                          )}
                          style={{ textAlign: "center", padding: "5px" }}
                        >
                          <span
                            className={classNames("badge-text", {
                              "text-[#FFFFFF]": currentStage === stage,
                              "text-[#8F949B]": currentStage !== stage,
                            })}
                            style={{ textAlign: "center" }}
                          >
                            {stageAbbreviations[stage]}
                          </span>
                        </div>
                        {designSchemes[stage]?.map((scheme, index) => (
                          <div
                            key={`scheme-${stage}-${index}`}
                            className={classNames(
                              "relative flex-shrink-0 border-[1.5px] w-[40px] h-[40px] rounded-md",
                              {
                                "border-[#0061DF]":
                                  currentScheme &&
                                  currentScheme.stage === stage &&
                                  currentScheme.index === index,
                              }
                            )}
                            onClick={() => switchCurrentScheme(stage, index)}
                          >
                            <div
                              className={classNames(
                                "absolute z-[5] top-0 left-0 p-0.5 rounded-tl-md flex items-center justify-center",
                                {
                                  "bg-[#F3F4F8]":
                                    currentScheme &&
                                    currentScheme.stage === stage &&
                                    currentScheme.index === index,
                                  "bg-[#F3F4F8]": !(
                                    currentScheme &&
                                    currentScheme.stage === stage &&
                                    currentScheme.index === index
                                  ),
                                }
                              )}
                            >
                              <span
                                className={classNames("text-[8px]", {
                                  "text-[#444444]":
                                    currentScheme &&
                                    currentScheme.stage === stage &&
                                    currentScheme.index === index,
                                  "text-[#8F949B]": !(
                                    currentScheme &&
                                    currentScheme.stage === stage &&
                                    currentScheme.index === index
                                  ),
                                })}
                                style={{
                                  lineHeight: "normal",
                                  textAlign: "center",
                                }}
                              >
                                {index + 1}
                              </span>
                            </div>
                            <div className="w-full h-full overflow-hidden flex items-center justify-center rounded-md">
                              <Image
                                height="100%"
                                src={scheme.canvasImage}
                                preview={false}
                              />
                            </div>
                          </div>
                        ))}
                        {currentStage === stage && (
                          <div onClick={() => handleClickAddSchemes(stage)}>
                            <PlusCircleOutlined
                              style={{ fontSize: "18px", color: "#D8D8D8" }}
                            />
                          </div>
                        )}
                      </>
                    ) : (
                      <></>
                    )
                  )}
                </div>
              </div>
              <RightOutlined style={{ fontSize: "18px", color: "#D8D8D8" }} />
            </div>
          )}
        </div>
      </CanvasContext.Provider>
    );
  }
);
