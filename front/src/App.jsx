import HeroSection from "../src/components/home/heroSection";
import AboutSection from "../src/components/home/aboutSection";
import ContactSection from "../src/components/home/contactSection";
import "../styles/App.css";

const App = () => {
  return (
    <div>
      <HeroSection />
      <AboutSection />
      <ContactSection />
    </div>
  );
};

export default App;
