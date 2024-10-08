import {
  AIStageSwitchRecords,
  BackendItem,
  StageSwitchRecords,
} from "@/app/page/config";
// import { BackendContentItem } from "@/app/page/provider";
import { baseUrl } from "@/configs/env";
import axios from "axios";

const PAINT_APP_ID = 0;

export async function start({ username }: { username: string }) {
  try {
    const res = await fetch(`${baseUrl}/paint/start`, {
      method: "POST",
      body: JSON.stringify({
        username,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const result = await res.json();
    if (!result.success) return undefined;
    return result.data;
  } catch (error: any) {
    throw new Error(`获取用户信息失败: ${error.message}`);
  }
}

export async function save({
  username,
  data,
}: {
  username: string;
  data: object;
}) {
  try {
    const res = await fetch(`${baseUrl}/paint/save`, {
      method: "POST",
      body: JSON.stringify({
        username,
        data,
      }),
      headers: {
        "Content-Type": "application/json",
      },
    });

    const result = await res.json();
    if (!result.success) {
      throw new Error("保存数据失败：" + result.message);
    }
  } catch (error: any) {
    throw new Error(`${error.message}`);
  }
}

// export async function submitSelection({
//   username,
//   currentNum,
//   designTask,
//   currentAIStage,
//   currentStage,
//   selectedTexts,
//   selectedCanvasRecords,
//   selectedButtonInfo,
// }: {
//   username: string;
//   designTask: string;
//   currentNum: number;
//   currentAIStage: string;
//   currentStage: string;
//   selectedTexts: string[];
//   selectedCanvasRecords: string[];
//   selectedButtonInfo: { buttonText: string; aiStage: string };
// }): Promise<BackendItem[]> {
//   try {
//     const response = await fetch(`${baseUrl}/generate`, {
//       method: "POST",
//       headers: {
//         "Content-Type": "application/json",
//       },
//       body: JSON.stringify({
//         username,
//         designTask,
//         currentNum,
//         currentAIStage,
//         currentStage,
//         selectedTexts,
//         selectedCanvasRecords,
//         selectedButtonInfo,
//       }),
//     });

//     if (!response.ok) { // 检查响应状态
//       throw new Error(`服务器错误: 状态码 ${response.status}`);
//     }

//     const result = await response.json();
//     if (!result.success) {
//       throw new Error(`提交内容失败: ${result.message}`);
//     }

//     return result.data;
//   } catch (error) {
//     // 检查不同的错误类型并打印更详细的信息
//     if (error instanceof TypeError) {
//       console.error(`网络请求问题: ${error.message}`);
//     } else if (error.message.startsWith('服务器错误')) {
//       console.error(error.message); // 服务器响应状态码错误
//     } else {
//       console.error(`未知错误: ${error.message}`);
//     }
//     throw error; // 抛出错误让调用者处理
//   }
// }

// export async function submitSelection({
//   username,
//   currentNum,
//   designTask,
//   currentAIStage,
//   currentStage,
//   selectedTexts,
//   selectedCanvasRecords,
//   selectedButtonInfo,
// }: {
//   username: string;
//   designTask: string;
//   currentNum: number;
//   currentAIStage: string;
//   currentStage: string;
//   selectedTexts: string[];
//   selectedCanvasRecords: string[];
//   selectedButtonInfo: { buttonText: string; aiStage: string };
// }): Promise<BackendItem[]> {
//   try {
//     const response = await axios({
//       method: 'post',
//       url: `${baseUrl}/generate`,
//       data: {
//         username,
//         designTask,
//         currentNum,
//         currentAIStage,
//         currentStage,
//         selectedTexts,
//         selectedCanvasRecords,
//         selectedButtonInfo,
//       },
//       headers: {
//         'Content-Type': 'application/json', // 明确设置Content-Type为application/json
//       },
//     });

//     const result = response.data;
//     if (!result.success) {
//       throw new Error(`提交内容失败: ${result.message}`);
//     }

//     return result.data;
//   } catch (error) {
//     // 使用axios时，错误处理有所不同
//     if (error.response) {
//       // 服务器响应了状态码不在2xx的范围
//       console.error(`服务器错误: 状态码 ${error.response.status}`);
//     } else if (error.request) {
//       // 请求已经发出，但没有收到响应
//       console.error(`网络请求问题: ${error.message}`);
//     } else {
//       // 发送请求时出了点问题
//       console.error(`未知错误: ${error.message}`);
//     }
//     throw error; // 抛出错误让调用者处理
//   }
// }

function dataURItoBlob(dataURI: string) {
  // 分割数据字符串获取，编码类型和数据本身
  var binary = atob(dataURI.split(",")[1]);
  var array = [];
  for (var i = 0; i < binary.length; i++) {
    array.push(binary.charCodeAt(i));
  }
  var type = dataURI.split(",")[0].split(":")[1].split(";")[0];

  return new Blob([new Uint8Array(array)], { type: type });
}

export async function submitSelection({
  username,
  currentNum,
  designTask,
  currentAIStage,
  currentStage,
  selectedTexts,
  selectedCanvasRecords,
  selectedButtonInfo,
}: {
  username: string;
  designTask: string;
  currentNum: number;
  currentAIStage: string;
  currentStage: string;
  selectedTexts: string[];
  selectedCanvasRecords: string[];
  selectedButtonInfo: { buttonText: string; aiStage: string };
}): Promise<BackendItem[]> {
  try {
    // 如果selectedCanvasRecords数组不为空，则上传画布数据
    if (selectedCanvasRecords.length > 0) {
      const base64Data = selectedCanvasRecords[0];
      let formData = new FormData();
      // 将Base64字符串转换为文件对象
      const blob = dataURItoBlob(base64Data); // 假设你有一个转换Base64到Blob的函数
      console.log("blob done.");
      formData.append("file", blob, "canvas.png"); // 添加文件到表单数据中

      // const uploadResponse = await axios.post(`${baseUrl}/upload`, formData, {
      //   headers: {
      //     "Content-Type": "multipart/form-data",
      //   },
      // });
      const uploadResponse = await axios.post(`${baseUrl}/upload`, formData);

      // 更新画布记录的URL
      selectedCanvasRecords[0] = uploadResponse.data.url; // 假设后端返回的新URL字段名为url
    }

    // 提交更新后的信息到后端
    // const submitResponse = await axios.post(
    //   `${baseUrl}/generate`,
    //   {
    //     username,
    //     designTask,
    //     currentNum,
    //     currentAIStage,
    //     currentStage,
    //     selectedTexts,
    //     selectedCanvasRecords,
    //     selectedButtonInfo,
    //   },
    //   {
    //     headers: {
    //       "Content-Type": "application/json",
    //     },
    //   }
    // );
    const submitResponse = await axios.post(`${baseUrl}/generate`, {
      username,
      designTask,
      currentNum,
      currentAIStage,
      currentStage,
      selectedTexts,
      selectedCanvasRecords,
      selectedButtonInfo,
    });

    const result = submitResponse.data;
    if (!result.success) {
      throw new Error(`提交内容失败: ${result.message}`);
    }

    return result.data;
  } catch (error) {
    // 错误处理: axios捕获错误的方式与原生fetch不同
    if (error.response) {
      // 请求已发出，但服务器以状态码之外的2xx响应
      console.error(`服务器错误: 状态码 ${error.response.status}`);
    } else if (error.request) {
      // 请求已经发出，但没有收到响应
      console.error(`网络请求问题: ${error.message}`);
    } else {
      // 发送请求时出了点问题
      console.error(`未知错误: ${error.message}`);
    }
    throw error;
  }
}

// 发送计时记录
export const handleSendTimingRecords = async ({
  username,
  stageSwitchRecords,
  aiStageSwitchRecords,
}: {
  username: string;
  stageSwitchRecords: StageSwitchRecords;
  aiStageSwitchRecords: AIStageSwitchRecords;
}) => {
  try {
    const response = await fetch(`${baseUrl}/timeRecord`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        username,
        stageSwitchRecords,
        aiStageSwitchRecords,
      }),
    });

    const result = await response.json();
    if (result.success) {
      console.log("计时记录发送成功", result);
      // 处理成功的逻辑
    } else {
      console.error("发送失败:", result.message);
      // 处理错误的逻辑
    }
  } catch (error) {
    console.error("请求错误:", error);
    // 处理请求错误的逻辑
  }
};
