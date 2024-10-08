import { Input } from "antd";
const { TextArea } = Input;
import { EllipseIcon } from "../../../../public/icons";
import { designTextInputW } from "@/app/page/config";
import { ReactSketchCanvas } from "react-sketch-canvas";
import React, { useEffect, useLayoutEffect, useState } from "react";
import { isReady } from "@/app/page/Main";
import {
  ADD_DESIGN_TEXT,
  DesignTextType,
  REMOVE_DESIGN_TEXT,
  TextPosition,
  UPDATE_PATHS,
  usePaintContext,
} from "@/app/page/provider";
import { CanvasPath } from "react-sketch-canvas/src/types";
import { Tools, useCanvasContext } from "@/app/page/(left-side)";
import { isDrawing } from "@/app/page/Main";

export interface ReactSketchCanvasProps {
  id?: string;
  ref?: React.MutableRefObject<any>;
  width?: string;
  height?: string;
  className?: string;
  strokeColor?: string;
  canvasColor?: string;
  backgroundImage?: string;
  exportWithBackgroundImage?: boolean;
  preserveBackgroundImageAspectRatio?: string;
  strokeWidth?: number;
  eraserWidth?: number;
  allowOnlyPointerType?: string;
  onChange?: (updatedPaths: CanvasPath[]) => void;
  onStroke?: (path: CanvasPath, isEraser: boolean) => void;
  style?: React.CSSProperties;
  svgStyle?: React.CSSProperties;
  withTimestamp?: boolean;

  readOnly?: boolean;
}

export type CanvasProps = {
  wrapperRef: React.MutableRefObject<any>;
};

export const Canvas = (props: CanvasProps) => {
  const { state: paintContext, dispatch } = usePaintContext();
  const {
    currentScheme,
    activeButton,
    selectedTextIndices,
    selectedCanvasRecords,
    currentStage,
    designSchemes,
  } = paintContext;

  const backgroundImageUrl = currentScheme
    ? designSchemes[currentScheme.stage]?.[currentScheme.index]
        ?.backgroundImageUrl
    : undefined;

  const {
    selectedTool,
    canvasRef,
    canvasProps,
    setSelectedTool,
    setCanvasProps,
  } = useCanvasContext();
  const { texts = [] } =
    designSchemes[currentScheme!.stage]?.[currentScheme!.index] || {};
  const { wrapperRef: canvasWrapperRef } = props;

  const [canvasH, setCanvasH] = useState<number | undefined>();
  useLayoutEffect(() => {
    const updateCanvasH = () => {
      if (canvasWrapperRef.current) {
        const height = canvasWrapperRef.current.getBoundingClientRect().height;
        setCanvasH(height);
      }
    };
    updateCanvasH();
    window.addEventListener("resize", updateCanvasH);
    return () => {
      window.removeEventListener("resize", updateCanvasH);
    };
  }, []);

  // 输入文本功能
  const [showDesignTextInput, setShowDesignTextInput] = useState<
    boolean | null
  >(false); // 控制文本输入
  const [currentDesignTextInputValue, setCurrentDesignTextInputValue] =
    useState("");
  const [currentDesignTextInputPosition, setCurrentDesignTextInputPosition] =
    useState<TextPosition>({ x: 0, y: 0 });

  const handleClickCanvas = async (e: any) => {
    if (activeButton !== null && !showDesignTextInput) {
      if (canvasRef.current) {
        try {
          // 调用exportImage方法导出画布为base64字符串
          const base64Data = await canvasRef.current.exportImage("png");

          // 检查base64Data是否已经存在于selectedCanvasRecords中
          const index = selectedCanvasRecords.indexOf(base64Data);
          let newSelectedCanvasRecords = [];

          if (index === -1) {
            // 如果base64Data不存在于数组中，添加它
            newSelectedCanvasRecords = [...selectedCanvasRecords, base64Data];
          } else {
            // 如果base64Data已存在于数组中，从数组中删除它
            newSelectedCanvasRecords = selectedCanvasRecords.filter(
              (_, i) => i !== index
            );
          }
          // 更新selectedCanvasRecords状态
          dispatch({
            type: "UPDATE_SELECTED_CANVAS_RECORDS",
            payload: newSelectedCanvasRecords,
          });
          //控制台检查Selected Canvas
          console.log(
            "dispatch更新成功！Selected Canvas:",
            newSelectedCanvasRecords
          );
        } catch (error) {
          console.error("Error exporting canvas image:", error);
        }
      }
    } else if (
      isReady(currentStage) &&
      selectedTool === Tools.Text &&
      !showDesignTextInput
    ) {
      // 当前可以输入，且没有正在进行的输入
      if (!canvasWrapperRef.current) {
        return;
      }

      const { left, width } = canvasWrapperRef.current.getBoundingClientRect();
      // 判断当前点击区域生成的输入框是否会超过画布
      const minX = left + designTextInputW / 2;
      const maxX = left + width - designTextInputW / 2;
      if (e.clientX >= minX && e.clientX <= maxX) {
        const x = e.clientX; // x position relative to the viewport
        const y = e.clientY; // y position relative to the viewport
        setCurrentDesignTextInputPosition({ x, y });
        setShowDesignTextInput(true);
      }
    } else if (showDesignTextInput) {
      if (currentDesignTextInputValue === "") {
        handleCancelTextInput();
      } else {
        handleConfirmTextInput();
      }
    }
  };

  const addDesignText = (newText: DesignTextType) => {
    dispatch({
      type: ADD_DESIGN_TEXT,
      payload: {
        stage: currentScheme?.stage,
        schemeIndex: currentScheme?.index,
        text: newText,
      },
    });
  };
  const removeDesignText = (index: number) => {
    dispatch({
      type: REMOVE_DESIGN_TEXT,
      payload: {
        stage: currentScheme?.stage,
        schemeIndex: currentScheme?.index,
        textIndex: index,
      },
    });
  };
  const handleConfirmTextInput = () => {
    // 如果是新的文本，将文字保存到状态中
    addDesignText({
      text: currentDesignTextInputValue,
      position: currentDesignTextInputPosition,
    });
    setShowDesignTextInput(false);
    setCurrentDesignTextInputPosition({ x: 0, y: 0 });
    setCurrentDesignTextInputValue("");
  };
  const handleCancelTextInput = () => {
    setShowDesignTextInput(false);
    setCurrentDesignTextInputPosition({ x: 0, y: 0 });
    setCurrentDesignTextInputValue("");
  };

  const handleClickTexts = (index: number, text: DesignTextType) => {
    const isActiveButtonNotNull = activeButton !== null;

    if (isActiveButtonNotNull) {
      const newSelectedTextIndices = selectedTextIndices.includes(index)
        ? selectedTextIndices.filter((i) => i !== index) // 取消选中
        : [...selectedTextIndices, index]; // 添加到选中列表

      // 根据新的 selectedTextIndices 准备 selectedTexts
      const newSelectedTexts = newSelectedTextIndices.map((i) => texts[i].text);

      // 使用单个 dispatch 来同时更新 selectedTextIndices 和 selectedTexts
      dispatch({
        type: "UPDATE_SELECTED_TEXTS_AND_INDICES", // 使用新定义的 action 类型
        payload: {
          selectedIndices: newSelectedTextIndices,
          selectedTexts: newSelectedTexts,
        },
      });
    } else {
      // 首先去除正在编辑的文本框
      removeDesignText(index);
      setCurrentDesignTextInputValue(text.text);
      setCurrentDesignTextInputPosition(text.position);
      setShowDesignTextInput(true);
    }
  };

  // useEffect(() => {
  //   // 使用更新后的selectedTextIndices来映射文本
  //   // console.log("dispatch更新后！Selected texts:", selectedTexts);
  // }, [selectedTextIndices, texts]);

  // 绘画
  const onSketchCanvasChange = (updatedPaths: CanvasPath[]): void => {
    dispatch({
      type: UPDATE_PATHS,
      payload: {
        stage: currentScheme?.stage,
        schemeIndex: currentScheme?.index,
        updatedPaths,
      },
    });
  };
  useEffect(() => {
    // 根据activeButton的状态决定是否禁用画布绘制
    const isReadOnly = activeButton !== null;

    if (!isDrawing(currentStage) || isReadOnly) {
      // 如果当前阶段不是绘制状态或activeButton非空，则禁用绘制
      setSelectedTool(Tools.Others);
      setCanvasProps((prevCanvasProps: Partial<ReactSketchCanvasProps>) => ({
        ...prevCanvasProps,
        allowOnlyPointerType: "touch",
        readOnly: isReadOnly, // 根据isReadOnly动态设置readOnly属性
      }));
    } else {
      // 否则，允许绘制
      setSelectedTool(Tools.Pen);
      setCanvasProps((prevCanvasProps: Partial<ReactSketchCanvasProps>) => ({
        ...prevCanvasProps,
        allowOnlyPointerType: "all",
        readOnly: false, // 确保画布处于可绘制状态
      }));
    }
  }, [currentStage, activeButton]);

  return (
    <div className="h-full w-full" onClick={handleClickCanvas}>
      <ReactSketchCanvas
        style={{
          border: `1px dashed ${
            selectedCanvasRecords.length > 0 ? "var(--primary-color)" : "#D8D8D8"
          }`,
          borderBottom: `1px dashed ${
            selectedCanvasRecords.length > 0 ? "var(--primary-color)" : "#D8D8D8"
          }`,
          borderLeft: `1px dashed ${
            selectedCanvasRecords.length > 0 ? "var(--primary-color)" : "#D8D8D8"
          }`,
          borderRight: `1px dashed ${
            selectedCanvasRecords.length > 0 ? "var(--primary-color)" : "#D8D8D8"
          }`,
        }}
        ref={canvasRef}
        onChange={onSketchCanvasChange}
        height={`${canvasH}px`}
        backgroundImage={backgroundImageUrl}
        exportWithBackgroundImage = {true}
        preserveBackgroundImageAspectRatio="xMidYMid"
        {...canvasProps}
      />
      {showDesignTextInput && (
        <div
          style={{
            top: `${currentDesignTextInputPosition.y}px`,
            left: `${currentDesignTextInputPosition.x}px`,
            maxWidth: `${designTextInputW}px`,
          }}
          className="fixed transform -translate-x-1/2 -translate-y-1/2 ]"
          onClick={(e) => {
            // 点击事件将不会影响父节点
            e.stopPropagation();
          }}
        >
          <div className="absolute left-[-6px] top-1/2 transform -translate-y-1/2 z-10">
            <EllipseIcon
              style={{
                width: "12px",
                height: "12px",
                fill: "var(--primary-color)",
              }}
            />
          </div>
          <div className="absolute right-[-6px] top-1/2 transform -translate-y-1/2 z-10">
            <EllipseIcon
              style={{
                width: "12px",
                height: "12px",
                fill: "var(--primary-color)",
              }}
            />
          </div>
          <TextArea
            value={currentDesignTextInputValue}
            onChange={(e) => setCurrentDesignTextInputValue(e.target.value)}
            autoSize={{ minRows: 1, maxRows: 4 }}
            className="design-text my-design-text-textarea"
          />
        </div>
      )}
      {texts.map((text, index) => (
        <div
          key={index}
          onClick={(e) => {
            // 点击事件将不会影响父节点
            e.stopPropagation();
            handleClickTexts(index, text);
          }}
          className="design-text fixed transform -translate-x-1/2 -translate-y-1/2
                                                 border border-dashed px-[11px] py-[4px]"
          style={{
            borderRadius: "10px",
            borderColor: selectedTextIndices.includes(index)
              ? "var(--primary-color)"
              : "#8F949B", // 条件式边框颜色
            background: selectedTextIndices.includes(index)
              ? "var(--primary-background)"
              : "", // 条件式背景颜色
            top: `${text.position.y}px`,
            left: `${text.position.x}px`,
            minWidth: `${designTextInputW / 2}px`,
            maxWidth: `${designTextInputW}px`,
          }}
        >
          {text.text}
        </div>
      ))}
    </div>
  );
};
