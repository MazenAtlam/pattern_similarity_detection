import { Activity } from 'lucide-react';
import '../../../styles/Footer.css';

const Footer = () => {
    return (
        <footer className="footer-custom">
            <div className="footer-content">
                <div className="footer-inner">
                    <div className="footer-brand">
                        <div className="footer-logo">
                            <Activity className="footer-logo-icon" />
                        </div>
                        <span className="footer-brand-text">
              Fourier Similarity Detector
            </span>
                    </div>
                    <p className="footer-copyright">
                        © 2025 Fourier Similarity Detector. All rights reserved.
                    </p>
                </div>
            </div>
        </footer>
    );
};

export default Footer;