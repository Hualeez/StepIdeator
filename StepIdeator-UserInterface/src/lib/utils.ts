import {Stage} from "../app/page/config";
import {DesignSchemeType} from "../app/page/provider";

// export const getSelectSchemeInfo = (index: number, designSchemes: {
//     [key in Stage]: DesignSchemeType[] | null;
// }): { stage: Stage, schemeIdx: number } => {
//     const rapidLength = designSchemes[Stage.DesignBrief]?.length;
//     if (index < (rapidLength as number)) {
//         return {
//             stage: Stage.Sketch,
//             schemeIdx: index
//         }
//     } else {
//         return {
//             stage: Stage.ModelImage,
//             schemeIdx: index - (rapidLength as number)
//         }
//     }
// }


export const imageUrlToBase64 = (url: string) => {
    return new Promise((resolve, reject) => {
        // 使用 fetch 获取图像数据
        fetch(url)
            .then(response => {
                if (!response.ok) {
                    throw new Error('网络请求失败');
                }
                return response.blob();
            })
            .then(blob => {
                // 使用 FileReader 将 Blob 转换为 base64
                const reader = new FileReader();
                reader.onload = () => {
                    const base64Data = (reader.result as string).split(',')[1];
                    resolve(`data:image/jpeg;base64,${base64Data}`);
                };
                reader.onerror = function (error) {
                    reject('转换为 base64 时出错：' + error);
                };
                reader.readAsDataURL(blob);
            })
            .catch(error => reject('获取图像数据时出错：' + error));
    });
}
