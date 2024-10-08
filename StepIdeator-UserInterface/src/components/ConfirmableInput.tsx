import React, { useState } from 'react';
import { Button, Input } from 'antd';

const { TextArea } = Input;

interface ConfirmableInputProps {
  initialValue: string;
  placeholder: string;
  onConfirm: (value: string) => void;
}

const ConfirmableInput: React.FC<ConfirmableInputProps> = ({ initialValue, placeholder, onConfirm }) => {
  const [value, setValue] = useState(initialValue);
  const [isConfirmed, setIsConfirmed] = useState(false);

  const handleConfirmClick = () => {
    setIsConfirmed(true);
    onConfirm(value);
  };

  return (
    <>
      {!isConfirmed ? (
        <>
          <TextArea
            className="rounded-md border border-[#F3F4F8] text-2 w-[100%]"
            value={value}
            onChange={(e) => setValue(e.target.value)}
            placeholder={placeholder}
            style={{
              height: "28px",
              resize: "none",
              backgroundColor: "#F4F5F8",
            }}
          />
          <Button
            style={{
              borderRadius: "6px",
              border: "1px solid #444444",
              background: "#FFF",
              color: "#444444",
            }}
            className="w-[100%] text-2 mt-2 mb-[48px]"
            onClick={handleConfirmClick}
          >
            确认
          </Button>
        </>
      ) : (
        <div className="text-2 text-[#8F949B] mt-[12px] mb-[48px]">
          {value}
        </div>
      )}
    </>
  );
};

export default ConfirmableInput;
