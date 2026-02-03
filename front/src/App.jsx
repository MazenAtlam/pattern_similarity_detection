import { Routes, Route } from "react-router-dom";
import HeroSection from "./components/home/heroSection";
import AboutSection from "./components/home/aboutSection";
import ContactSection from "./components/home/contactSection";
import Fifa from "./components/pages/Fifa";
import Songs from "./components/pages/Songs";
import Layout from "./components/layout/Layout";
import "./styles/App.css";

const App = () => {
  return (
    <Routes>
      {/* Home page with Layout wrapper */}
      <Route
        path="/"
        element={
          <Layout>
            <HeroSection />
            <AboutSection />
            <ContactSection />
          </Layout>
        }
      />

      {/* Fifa page */}
      <Route path="/fifa" element={<Fifa />} />

      {/* Songs page */}
      <Route path="/songs" element={<Songs />} />
    </Routes>
  );
};

export default App;
