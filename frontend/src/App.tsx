import React from "react";
import { Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import Dashboard from "./pages/Dashboard";
import Assets from "./pages/Assets";
import AssetDetailPage from "./pages/AssetDetail";
import Risks from "./pages/Risks";
import AIAdvisor from "./pages/AIAdvisor";
import Simulation from "./pages/Simulation";
import Optimization from "./pages/Optimization";

export default function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/assets" element={<Assets />} />
        <Route path="/assets/:id" element={<AssetDetailPage />} />
        <Route path="/risks" element={<Risks />} />
        <Route path="/advisor" element={<AIAdvisor />} />
        <Route path="/simulation" element={<Simulation />} />
        <Route path="/optimization" element={<Optimization />} />
      </Routes>
    </Layout>
  );
}
