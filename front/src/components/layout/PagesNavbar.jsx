import {Link} from "react-router-dom";
import {ArrowLeft, Trophy} from "lucide-react";
import "../../../styles/PagesNavbar.css"

const PagesNavbar = ({
    pageTitle,
    pageDescription,
                     }) => {
    return (
        <div className="fifa-header pt-3">
            <div className="fifa-header-left ms-3">
                <Link to="/" className="my-auto">
                    <button className="back-button">
                        <ArrowLeft className="back-icon" />
                    </button>
                </Link>
                <div>
                    <div className="fifa-title-container">
                        <div className="fifa-icon-container">
                            <Trophy className="fifa-icon" />
                        </div>
                        <h1 className="fifa-title">
                            {pageTitle}
                        </h1>
                    </div>
                    <p className="fifa-subtitle">
                        {pageDescription}
                    </p>
                </div>
            </div>
        </div>
    );
}

export default PagesNavbar;