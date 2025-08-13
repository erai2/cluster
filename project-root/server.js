import express from "express";
import cors from "cors";
import aiRoutes from "./aiRoutes.js";

const app = express();
app.use(cors());
app.use(express.json());

app.use("/api", aiRoutes);

const PORT = process.env.PORT || 8000;
app.listen(PORT, () => {
  console.log(`✅ Server running on http://localhost:${PORT}`);
});
