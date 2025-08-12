import { useState } from 'react';

// 규칙을 표 형태로 관리하는 컴포넌트
export default function RuleTable({ rules, setRules }) {
  const [newRule, setNewRule] = useState({ condition: "", action: "" });

  // 추가
  const addRule = async () => {
    const res = await fetch("/rules", {
      method: "POST",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify({...newRule, id: Date.now()})
    });
    if(res.ok) setRules(r => [...r, {...newRule, id: Date.now()}]);
    setNewRule({condition:"", action:""});
  };

  // 삭제
  const deleteRule = async (id) => {
    await fetch(`/rules/${id}`, {method:"DELETE"});
    setRules(rules.filter(r => r.id !== id));
  };

  // 편집
  const editRule = async (id, field, value) => {
    const idx = rules.findIndex(r => r.id === id);
    const updated = [...rules];
    updated[idx][field] = value;
    await fetch(`/rules/${id}`, {
      method: "PUT",
      headers: {"Content-Type":"application/json"},
      body: JSON.stringify(updated[idx])
    });
    setRules(updated);
  };

  return (
    <div className="overflow-x-auto">
      <table className="min-w-full bg-white border border-gray-200 rounded-lg shadow-sm">
        <thead>
          <tr className="bg-blue-100 text-blue-800">
            <th className="py-3 px-5 text-left">조건</th>
            <th className="py-3 px-5 text-left">액션</th>
            <th className="py-3 px-5">삭제</th>
          </tr>
        </thead>
        <tbody>
          {rules.map(rule => (
            <tr key={rule.id} className="hover:bg-blue-50 transition">
              <td className="border-t px-5 py-2">
                <input
                  className="border border-gray-300 rounded px-2 py-1 w-full focus:ring-2 focus:ring-blue-200"
                  value={rule.condition}
                  onChange={e => editRule(rule.id, "condition", e.target.value)}
                />
              </td>
              <td className="border-t px-5 py-2">
                <input
                  className="border border-gray-300 rounded px-2 py-1 w-full focus:ring-2 focus:ring-blue-200"
                  value={rule.action}
                  onChange={e => editRule(rule.id, "action", e.target.value)}
                />
              </td>
              <td className="border-t px-5 py-2 text-center">
                <button
                  className="bg-red-500 hover:bg-red-700 text-white px-3 py-1 rounded transition"
                  onClick={()=>deleteRule(rule.id)}
                >삭제</button>
              </td>
            </tr>
          ))}
          {/* 추가 입력 */}
          <tr>
            <td className="border-t px-5 py-2">
              <input
                className="border border-gray-300 rounded px-2 py-1 w-full focus:ring-2 focus:ring-blue-200"
                placeholder="새 조건"
                value={newRule.condition}
                onChange={e=>setNewRule({...newRule, condition:e.target.value})}
              />
            </td>
            <td className="border-t px-5 py-2">
              <input
                className="border border-gray-300 rounded px-2 py-1 w-full focus:ring-2 focus:ring-blue-200"
                placeholder="새 액션"
                value={newRule.action}
                onChange={e=>setNewRule({...newRule, action:e.target.value})}
              />
            </td>
            <td className="border-t px-5 py-2 text-center">
              <button
                className="bg-green-600 hover:bg-green-800 text-white px-3 py-1 rounded transition"
                onClick={addRule}
              >추가</button>
            </td>
          </tr>
        </tbody>
      </table>
    </div>
  );
}
