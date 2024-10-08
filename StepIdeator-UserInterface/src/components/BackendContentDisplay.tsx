import React from "react";
import { Row, Col, Popover, Button, Divider } from "antd";
import renderJSONObject from "./RenderJSONObject";

const BackendContentDisplay = ({
  contents,
  handleSendToWorkSpace,
  handleImageClick,
  submissionMarkers,
  showPopover,
  setShowPopover,
  clickedImgUrl,
}) => {
  // 辅助函数来解析可能是字符串形式的 JSON 数据
  const parseJSONData = (data) => {
    try {
      // 尝试直接解析整个字符串
      return [JSON.parse(data)]; // 如果是单个有效的 JSON 对象，直接返回
    } catch (error) {
      try {
        // 如果直接解析失败，尝试按正则表达式拆分并解析
        const jsonStrings = data.match(/{[^}]*}/g);
        if (jsonStrings) {
          return jsonStrings.map((jsonStr) => JSON.parse(jsonStr));
        }
      } catch (nestedError) {
        console.error("Parsing nested JSON error:", nestedError);
      }
      console.error("Parsing JSON error:", error);
      return []; // 如果都失败了，返回空数组
    }
  };

  // // 检查 JSON 数据是否只有一个顶级键
  // const isSingleKeyJSON = (data) => {
  //   const jsonData = parseJSONData(data);
  //   return Object.keys(jsonData).length === 1;
  // };

  return (
    <Row gutter={[16, 16]}>
      {contents.map(
        (
          content: { type: string; data: any; timestamp: string },
          index: React.Key
        ) => (
          <React.Fragment key={index}>
            {submissionMarkers.includes(index) && (
              <Divider style={{ fontSize: "12px", color: "#D9D9D9" }}>
                {new Date(content.timestamp).toLocaleString()}
              </Divider>
            )}
            <Col span={12}>
              <div className="content-display" style={{ marginBottom: "10px" }}>
                {content.type === "json" &&
                  Object.values(content.data).map((value, index) => {
                    const parsedData = parseJSONData(value);
                    return parsedData ? (
                      <div
                        key={index}
                        className="content-card"
                        style={{ marginBottom: "20px", color: "black" }}
                      >
                        {renderJSONObject(parsedData)}{" "}
                      </div>
                    ) : null;
                  })}
                {content.type === "image" &&
                  Object.values(content.data).map((value, index) => (
                    <Popover
                      key={index}
                      content={
                        <Button
                          type="text"
                          onClick={() =>
                            handleSendToWorkSpace({ ...content, data: value })
                          }
                        >
                          放至工作区
                        </Button>
                      }
                      trigger="click"
                      open={showPopover && clickedImgUrl === value}
                      onOpenChange={(open) => setShowPopover(open)}
                    >
                      <img
                        src={value}
                        alt={`Content ${index}`}
                        onClick={() => handleImageClick(value)}
                        style={{
                          maxWidth: "100%",
                          height: "auto",
                          borderRadius: "10px",
                          marginBottom: "20px",
                        }}
                      />
                    </Popover>
                  ))}
              </div>
            </Col>
          </React.Fragment>
        )
      )}
    </Row>
  );
};

export default BackendContentDisplay;
