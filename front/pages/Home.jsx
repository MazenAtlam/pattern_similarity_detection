import HeroSection from "../src/components/home/heroSection";
import AboutSection from "../src/components/home/aboutSection";
import ContactSection from "../src/components/home/contactSection";
import Navbar from "../src/components/home/Navbar.jsx";
import React from "react";

const Home = () => {
    return (
        <div>
            <Navbar />
            <HeroSection />
            <AboutSection />
            <ContactSection />
        </div>
    );
}

export default Home;