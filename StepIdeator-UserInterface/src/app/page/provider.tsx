"use client";

import {
  createContext,
  Dispatch,
  useContext,
  useReducer,
  ReactNode,
} from "react";
import { CreativeType, Stage, UserStage, AIStage } from "@/app/page/config";
import { CanvasPath } from "react-sketch-canvas";

export type TextPosition = {
  x: number;
  y: number;
};

export type DesignTextType = {
  text: string;
  position: TextPosition;
};

export type DesignSchemeType = {
  name: string; // 方案名字
  canvasSvg?: string; // SVG code
  canvasImage?: string; // image type的URI
  paths: CanvasPath[]; // 当前绘画内容
  texts: DesignTextType[]; // 用户文本输入
  backgroundImageUrl?: string;
};

// export type DesignCreativeItem = {
//   type:
//     | "abstractText"
//     | "concreteText"
//     | "abstractImage"
//     | "concreteImage"
//     | "groupTypeOne"
//     | "groupTypeTwo";
//   text?: string;
//   image?: string;
//   combinations?: DesignCreativeItem[];
// };

// export type DesignCreativeType = {
//   type: CreativeType;
//   items: DesignCreativeItem[]; // 内部包含的item
//   displayType: "sequence" | "direct"; // 展示的方式
//   displayed: boolean; // 是否被使用进行展示
//   displayIndex: number; // 当前展示的item
//   relatedScheme?: number; // 当前刺激关联的方案
// };

// export type ImageContent = {
//   type: "image";
//   url: string; // 图片的URL地址
// };

// export type JSONContent = {
//   type: "json";
//   data: any; // JSON内容，可以是任意类型
// };

// export type BackendContentItem = ImageContent | JSONContent;

export type PaintState = {
  // 用户信息
  username: string;
  currentScheme?: {
    index: number;
    stage: UserStage;
  };
  currentStage: Stage; // TODO 每次切换后，传输当前阶段数据给后端，用于生成图像时判断阶段。
  // 用户输入的任务目标
  designTask?: string; // TODO 传输设计任务给后端
  // 所有方案
  designSchemes: {
    [key in UserStage]: DesignSchemeType[];
  };
  // // AI生成的刺激个数
  // num: number;
  //AI灵感助手的阶段
  currentAIStage: AIStage;

  // 用户最终选择的方案，只能从前两个阶段的方案中选
  // 保存方案的idx，两个阶段的方案会以接连的形式表达
  selectedSchemes: number[];

  activeButton: string | null;

  selectedTextIndices: number[]; // 新增状态
  selectedTexts: string[];
  selectedCanvasRecords: string[]; // 新状态，用于记录点击信息
  backgroundImageUrl: string;
};

export type PaintContextType = {
  state: PaintState;
  dispatch: Dispatch<PaintAction>;
};

export const ADD_SCHEME = "ADD_SCHEME",
  SWITCH_STAGE = "SWITCH_STAGE",
  ADD_DESIGN_TEXT = "ADD_DESIGN_TEXT",
  REMOVE_DESIGN_TEXT = "REMOVE_DESIGN_TEXT",
  UPDATE_DESIGN_TASK = "UPDATE_DESIGN_TASK",
  UPDATE_PATHS = "UPDATE_PATHS",
  UPDATE_SVG = "UPDATE_SVG",
  UPDATE_IMG = "UPDATE_IMG",
  NEXT_CREATIVE_ITEM = "NEXT_CREATIVE_ITEM",
  NEXT_CREATIVE = "NEXT_CREATIVE",
  CLEAR_DESIGN_TEXTS = "CLEAR_DESIGN_TEXTS",
  UPDATE_SELECTED_SCHEMES = "UPDATE_SELECTED_SCHEMES",
  UPDATE_CURRENT_SCHEME = "UPDATE_CURRENT_SCHEME",
  ADD_CREATIVES = "ADD_CREATIVES",
  UPDATE_SCHEMES_NAME = "UPDATE_SCHEMES_NAME",
  UPDATE_USER_NAME = "UPDATE_USER_NAME",
  LOAD_STATE = "LOAD_STATE",
  UPDATE_USER_STAGE = "UPDATE_USER_STAGE",
  UPDATE_NUM = "UPDATE_NUM",
  UPDATE_ACTIVE_BUTTON = "UPDATE_ACTIVE_BUTTON",
  UPDATE_SELECTED_TEXTS_AND_INDICES = "UPDATE_SELECTED_TEXTS_AND_INDICES",
  UPDATE_SELECTED_CANVAS_RECORDS = "UPDATE_SELECTED_CANVAS_RECORDS",
  UPDATE_SCHEME_BACKGROUND_IMG_URL = "UPDATE_SCHEME_BACKGROUND_IMG_URL",
  UPDATE_CURRENT_AISTAGE = "UPDATE_CURRENT_AISTAGE";

export type PaintAction = { type: string; payload: any };

const initialState: PaintState = {
  username: "",
  selectedSchemes: [],

  currentStage: Stage.NotReady,
  designSchemes: {
    // [Stage.NotReady]: null,
    [Stage.DesignBrief]: [],
    [Stage.Sketch]: [],
    [Stage.ModelImage]: [],
    [Stage.Rendering]: [],
    // [Stage.Finish]: null,
    // [Stage.Unable]: null,
  },
  designTask: "",
  currentAIStage: AIStage.DesignBrief,
  // num: 1,
  activeButton: null,
  selectedTextIndices: [],
  selectedTexts: [],
  selectedCanvasRecords: [],
  backgroundImageUrl: "",
};

function paintReducer(state: PaintState, action: PaintAction): PaintState {
  switch (action.type) {
    case ADD_SCHEME: {
      const newScheme: DesignSchemeType = {
        name: "",
        paths: [],
        texts: [],
        backgroundImageUrl: "", // 初始化为空字符串
      };
      const updatedDesignSchemes = { ...state.designSchemes };
      const stageKey: UserStage = action.payload.stage;
      return {
        ...state,
        designSchemes: {
          ...updatedDesignSchemes,
          [stageKey]: updatedDesignSchemes[stageKey]
            ? [...updatedDesignSchemes[stageKey], newScheme]
            : [newScheme],
        },
      };
    }
    case UPDATE_CURRENT_SCHEME:
      return {
        ...state,
        currentScheme: action.payload,
      };
    case UPDATE_DESIGN_TASK:
      return {
        ...state,
        designTask: action.payload.designTask,
      };
    case SWITCH_STAGE:
      return {
        ...state,
        currentStage: action.payload.stage,
      };
    case ADD_DESIGN_TEXT: {
      const updatedDesignSchemes = { ...state.designSchemes };
      const stageKey: UserStage = action.payload.stage;
      const updatedStageSchemes: DesignSchemeType[] = [
        ...(updatedDesignSchemes[stageKey] ?? []),
      ];
      if (updatedStageSchemes.length <= action.payload.schemeIndex) {
        return state;
      }
      const updatedScheme: DesignSchemeType = {
        ...updatedStageSchemes[action.payload.schemeIndex],
      };
      updatedScheme.texts = [...updatedScheme.texts, action.payload.text]; // 添加新文本
      updatedStageSchemes[action.payload.schemeIndex] = updatedScheme; // 更新方案
      updatedDesignSchemes[stageKey] = updatedStageSchemes; // 注意这里也应使用 stageKey
      return { ...state, designSchemes: updatedDesignSchemes };
    }
    case REMOVE_DESIGN_TEXT: {
      const updatedDesignSchemes = { ...state.designSchemes };
      const stageKey: UserStage = action.payload.stage; // 确保这是一个 Stage 枚举的值
      const updatedStageSchemes: DesignSchemeType[] = [
        // 使用枚举值作为键，并处理 undefined 的情况
        ...(updatedDesignSchemes[stageKey] ?? []),
      ];
      if (updatedStageSchemes.length <= action.payload.schemeIndex) {
        return state;
      }
      const updatedScheme: DesignSchemeType = {
        ...updatedStageSchemes[action.payload.schemeIndex],
      };
      updatedScheme.texts.splice(action.payload.textIndex, 1); // 移除指定文本
      updatedStageSchemes[action.payload.schemeIndex] = updatedScheme; // 更新方案
      updatedDesignSchemes[stageKey] = updatedStageSchemes; // 使用 stageKey 更新
      return { ...state, designSchemes: updatedDesignSchemes };
    }
    case CLEAR_DESIGN_TEXTS: {
      const updatedDesignSchemes = { ...state.designSchemes };
      const stageKey: UserStage = action.payload.stage; // 确保这是一个 Stage 枚举的值
      const updatedStageSchemes: DesignSchemeType[] = [
        // 使用枚举值作为键，并处理 undefined 的情况
        ...(updatedDesignSchemes[stageKey] ?? []),
      ];
      if (updatedStageSchemes.length <= action.payload.schemeIndex) {
        return state;
      }
      const updatedScheme: DesignSchemeType = {
        ...updatedStageSchemes[action.payload.schemeIndex],
      };
      // 直接清空 texts 数组
      updatedScheme.texts = [];
      updatedStageSchemes[action.payload.schemeIndex] = updatedScheme; // 更新方案
      updatedDesignSchemes[stageKey] = updatedStageSchemes; // 使用 stageKey 更新
      return { ...state, designSchemes: updatedDesignSchemes };
    }
    case UPDATE_PATHS: {
      const updatedDesignSchemes = { ...state.designSchemes };
      const stageKey: UserStage = action.payload.stage; // 确保这是一个 Stage 枚举的值
      const updatedStageSchemes: DesignSchemeType[] = [
        // 使用枚举值作为键，并处理 undefined 的情况
        ...(updatedDesignSchemes[stageKey] ?? []),
      ];
      if (updatedStageSchemes.length <= action.payload.schemeIndex) {
        return state;
      }
      const updatedScheme: DesignSchemeType = {
        ...updatedStageSchemes[action.payload.schemeIndex],
      };
      // 更新 paths 数组
      updatedScheme.paths = action.payload.updatedPaths;
      updatedStageSchemes[action.payload.schemeIndex] = updatedScheme; // 更新方案
      updatedDesignSchemes[stageKey] = updatedStageSchemes; // 使用 stageKey 更新
      return { ...state, designSchemes: updatedDesignSchemes };
    }
    case UPDATE_SVG: {
      const updatedDesignSchemes = { ...state.designSchemes };
      const stageKey: UserStage = action.payload.stage; // 确保这是一个 Stage 枚举的值
      const updatedStageSchemes: DesignSchemeType[] = [
        // 使用枚举值作为键，并处理 undefined 的情况
        ...(updatedDesignSchemes[stageKey] ?? []),
      ];
      if (updatedStageSchemes.length <= action.payload.schemeIndex) {
        return state;
      }
      const updatedScheme: DesignSchemeType = {
        ...updatedStageSchemes[action.payload.schemeIndex],
      };
      // 更新 SVG 代码
      updatedScheme.canvasSvg = action.payload.svgCode;
      updatedStageSchemes[action.payload.schemeIndex] = updatedScheme; // 更新方案
      updatedDesignSchemes[stageKey] = updatedStageSchemes; // 使用 stageKey 更新
      return { ...state, designSchemes: updatedDesignSchemes };
    }
    case UPDATE_IMG: {
      const updatedDesignSchemes = { ...state.designSchemes };
      const stageKey: UserStage = action.payload.stage; // 确保这是一个 Stage 枚举的值
      const updatedStageSchemes: DesignSchemeType[] = [
        // 使用枚举值作为键，并处理 undefined 的情况
        ...(updatedDesignSchemes[stageKey] ?? []),
      ];
      if (updatedStageSchemes.length <= action.payload.schemeIndex) {
        return state;
      }
      const updatedScheme: DesignSchemeType = {
        ...updatedStageSchemes[action.payload.schemeIndex],
      };
      // 更新图像数据
      updatedScheme.canvasImage = action.payload.imageData;
      updatedStageSchemes[action.payload.schemeIndex] = updatedScheme; // 更新方案
      updatedDesignSchemes[stageKey] = updatedStageSchemes; // 使用 stageKey 更新
      return { ...state, designSchemes: updatedDesignSchemes };
    }
    case UPDATE_SELECTED_SCHEMES: {
      return {
        ...state,
        selectedSchemes: action.payload.schemes,
      };
    }

    case "UPDATE_CURRENT_AISTAGE": {
      return {
        ...state,
        currentAIStage: action.payload,
      };
    }
    case UPDATE_USER_NAME: {
      return {
        ...state,
        username: action.payload.username,
      };
    }
    case LOAD_STATE: {
      // 在修改之前打印出传入的数据
      console.log(
        "Before loading state, action.payload.data:",
        action.payload.data
      );

      // 创建新的状态
      const newState = {
        ...state,
        ...action.payload.data,
        username: action.payload.username,
        designSchemes: {
          [Stage.NotReady]: null,
          [Stage.DesignBrief]: action.payload.data.designBriefSchemes,
          [Stage.Sketch]: action.payload.data.sketchSchemes,
          [Stage.ModelImage]: action.payload.data.modelImageSchemes,
          [Stage.Rendering]: action.payload.data.renderingSchemes,
          [Stage.Finish]: null,
          [Stage.Unable]: null,
        },
      };

      // 在修改之后打印出新的状态
      console.log("After loading state, newState:", newState);

      // 返回新的状态
      return newState;
    }

    case "UPDATE_ACTIVE_BUTTON":
      // 如果activeButton从null变为id，保持selectedTextIndices和selectedCanvasRecords不变
      // 如果activeButton从id变为null（意味着取消或提交），则清空selectedTextIndices和selectedCanvasRecords
      const shouldClear =
        state.activeButton !== null || action.payload === null;
      return {
        ...state,
        activeButton: action.payload,
        selectedTextIndices: shouldClear ? [] : state.selectedTextIndices,
        selectedTexts: shouldClear ? [] : state.selectedTexts,
        selectedCanvasRecords: shouldClear ? [] : state.selectedCanvasRecords,
      };
    // case "UPDATE_SELECTED_TEXT_INDICES":
    //   return {
    //     ...state,
    //     selectedTextIndices: action.payload,
    //   };
    // case "UPDATE_SELECTED_TEXT":
    //   return {
    //     ...state,
    //     selectedText: action.payload,
    //   };
    case "UPDATE_SELECTED_TEXTS_AND_INDICES":
      const { selectedIndices, selectedTexts } = action.payload;
      return {
        ...state,
        selectedTextIndices: selectedIndices,
        selectedTexts: selectedTexts,
      };
    case "UPDATE_SELECTED_CANVAS_RECORDS":
      return { ...state, selectedCanvasRecords: action.payload };
    case "UPDATE_SCHEME_BACKGROUND_IMG_URL": {
      const { stage, index, backgroundImageUrl } = action.payload;
      const updatedSchemes = [...state.designSchemes[stage]];
      if (updatedSchemes[index]) {
        updatedSchemes[index] = {
          ...updatedSchemes[index],
          backgroundImageUrl: backgroundImageUrl,
        };
      }
      return {
        ...state,
        designSchemes: {
          ...state.designSchemes,
          [stage]: updatedSchemes,
        },
      };
    }

    default:
      return state;
  }
}

const PaintContext = createContext<PaintContextType | undefined>(undefined);

type PaintProviderProps = {
  children?: ReactNode;
};

export const PaintProvider: React.FC<PaintProviderProps> = ({ children }) => {
  const [state, dispatch] = useReducer(paintReducer, initialState);

  return (
    <PaintContext.Provider value={{ state, dispatch }}>
      {children}
    </PaintContext.Provider>
  );
};

export const usePaintContext = (): PaintContextType => {
  const context = useContext(PaintContext);
  return context as PaintContextType;
};
