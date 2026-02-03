import { useState } from 'react';
import { Link, useLocation } from 'react-router-dom';
import { Menu, X, Activity } from 'lucide-react';
import "../../../styles/Navbar.css"

const Navbar = () => {
    const [isOpen, setIsOpen] = useState(false);
    const location = useLocation();

    const navLinks = [
        { name: 'Home', path: '/' },
        { name: 'About', path: '/#about' },
        { name: 'Contact', path: '/#contact' },
    ];

    const isActive = (path) => {
        if (path === '/') return location.pathname === '/';
        return location.pathname === path || location.hash === path.replace('/', '');
    };

    return (
        <nav className="navbar-custom">
            <div className="container py-2">
                <div className="d-flex align-items-center justify-content-between h-100">
                    {/* Brand */}
                    <Link to="/" className="navbar-brand-container">
                        <div className="navbar-logo">
                            <Activity className="navbar-logo-icon" />
                        </div>
                        <span className="navbar-brand-text">
              Fourier Similarity Detector
            </span>
                    </Link>

                    {/* Desktop Navigation */}
                    <div className="d-none d-md-flex align-items-center">
                        {navLinks.map((link) => (
                            <Link
                                key={link.name}
                                to={link.path}
                                className={`nav-link-custom ${isActive(link.path) ? 'active' : ''}`}
                            >
                                {link.name}
                            </Link>
                        ))}
                    </div>

                    {/* Mobile Menu Button */}
                    <button
                        type="button"
                        className="navbar-toggler-custom d-md-none"
                        onClick={() => setIsOpen(!isOpen)}
                        aria-expanded={isOpen}
                        aria-label="Toggle navigation"
                    >
                        {isOpen ? <X className="navbar-toggler-icon-custom" /> : <Menu className="navbar-toggler-icon-custom" />}
                    </button>
                </div>

                {/* Mobile Navigation */}
                {isOpen && (
                    <div className="mobile-nav d-md-none">
                        {navLinks.map((link) => (
                            <Link
                                key={link.name}
                                to={link.path}
                                onClick={() => setIsOpen(false)}
                                className={`mobile-nav-link ${isActive(link.path) ? 'active' : ''}`}
                            >
                                {link.name}
                            </Link>
                        ))}
                    </div>
                )}
            </div>
        </nav>
    );
};

export default Navbar;