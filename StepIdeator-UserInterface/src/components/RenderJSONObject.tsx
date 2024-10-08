import React from "react";

export default function renderJSONObject(
  obj: object | null,
  depth = 0
): JSX.Element | null {
  if (obj === null || typeof obj !== "object") {
    return null; // 直接返回null，如果对象不存在或不是一个对象
  }

  const cardStyle: React.CSSProperties = {
    background: "#ECEFF4",
    padding: "10px",
    borderRadius: "5px",
    overflowX: "auto",
    marginBottom: "10px",
  };

  const keyStyle: React.CSSProperties = {
    fontWeight: "bold",
    fontSize: "16px", // 增加所有键的字号
  };

  const listStyle: React.CSSProperties = {
    paddingLeft: "20px", // 为列表添加左边距，使圆点可见
  };

  return (
    <div style={cardStyle}>
      {Object.entries(obj).map(([key, value]) => {

        // 对于数组，渲染为列表项
        if (Array.isArray(value)) {
          return (
            <div key={key}>
              <span style={keyStyle}>{key}:</span>
              <ul style={listStyle}>
                {value.map((item, index) => (
                  <li key={index}>
                    {typeof item === "object" && item !== null
                      ? renderJSONObject(item, depth + 1)
                      : item.toString()}
                  </li>
                ))}
              </ul>
            </div>
          );
        } else if (typeof value === "object" && value !== null) {
          // 对于对象，递归渲染
          return (
            <div key={key}>
              <span style={keyStyle}>{key}:</span>
              {renderJSONObject(value, depth + 1)}
            </div>
          );
        } else {
          // 对于基础类型，直接渲染
          return (
            <div key={key}>
              <span style={keyStyle}>{key}:</span> {value.toString()}
            </div>
          );
        }
      })}
    </div>
  );
}
