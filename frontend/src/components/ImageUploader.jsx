import { useState } from 'react';

// 이미지 업로드 컴포넌트
export default function ImageUploader() {
  const [file, setFile] = useState(null); // 선택된 파일 상태
  const [preview, setPreview] = useState(null); // 미리보기 URL

  // 파일 선택 시 상태 업데이트
  const handleChange = (e) => {
    const selected = e.target.files[0];
    setFile(selected);
    setPreview(selected ? URL.createObjectURL(selected) : null);
  };

  // 서버로 업로드
  const handleUpload = async () => {
    if (!file) return;
    const formData = new FormData();
    formData.append('file', file);

    await fetch('http://localhost:8000/upload-image', {
      method: 'POST',
      body: formData,
    });
  };

  return (
    <div className="p-4 border rounded">
      {/* 파일 입력 */}
      <input type="file" accept="image/*" onChange={handleChange} />

      {/* 미리보기 */}
      {preview && (
        <img src={preview} alt="preview" className="mt-2 max-w-xs" />
      )}

      {/* 업로드 버튼 */}
      <button
        className="mt-2 px-4 py-2 bg-blue-500 text-white"
        onClick={handleUpload}
      >
        서버로 전송
      </button>
    </div>
  );
}
