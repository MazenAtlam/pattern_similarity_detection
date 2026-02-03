import { Routes, Route } from "react-router-dom";
import Home from "../pages/Home";
import Fifa from "../pages/fifa";
import Songs from "../pages/songs";
import Footer from "./components/layout/Footer";
import "../styles/App.css";

const App = () => {
  return (
    <div className="app">
      <main className="main-content">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/songs" element={<Songs />} />
          <Route path="/fifa" element={<Fifa />} />
        </Routes>
      </main>
      <Footer />
    </div>
  );
};

export default App;
