export default function RuleCards({ rules }) {
  return (
    <div className="grid gap-4">
      {rules.map(r => (
        <div key={r.id} className="p-4 border rounded shadow-sm">
          <p className="font-semibold">조건: {r.condition}</p>
          <p>동작: {r.action}</p>
        </div>
      ))}
    </div>
  );
}
