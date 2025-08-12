import React, { useEffect, useState } from "react";
import RuleTable from "./components/RuleTable";
import ExportMenu from "./components/ExportMenu";
import ImageUploader from "./components/ImageUploader";

export default function App() {
  const [rules, setRules] = useState([]);

  useEffect(() => {
    fetch("/rules").then(res => res.json()).then(setRules);
  }, []);

  // 파일 업로드로 규칙 자동추출
  const handleExtract = async (e) => {
    const file = e.target.files[0];
    const form = new FormData();
    form.append("file", file);
    const res = await fetch("/extract_rules", {method: "POST", body: form});
    const data = await res.json();
    setRules(rules.concat(data.rules));
  };

  return (
    <div className="min-h-screen bg-gray-50 p-8">
      <div className="max-w-4xl mx-auto bg-white shadow-lg rounded-lg p-8">
        <h1 className="text-3xl font-bold mb-6 text-blue-700">규칙 관리 시스템</h1>
        <ExportMenu />

        {/* 규칙 테이블 */}
        <div className="mb-6">
          <RuleTable rules={rules} setRules={setRules} />
        </div>

        {/* AI 규칙 자동추출 */}
        <div className="border-t pt-6 mt-6 space-y-4">
          <div>
            <h3 className="text-lg font-semibold mb-2 text-blue-800">AI 규칙 자동추출 (파일 업로드)</h3>
            <input type="file" className="border rounded px-3 py-1" onChange={handleExtract} />
          </div>

          <div>
            <h3 className="text-lg font-semibold mb-2 text-blue-800">이미지 업로드 예제</h3>
            <ImageUploader />
          </div>
        </div>
      </div>
    </div>
  );
}
