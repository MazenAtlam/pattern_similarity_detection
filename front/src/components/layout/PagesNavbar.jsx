import { Link } from "react-router-dom";
import { ArrowLeft, Trophy, Music } from "lucide-react";
import "../../../styles/PagesNavbar.css"

const PagesNavbar = ({
    pageName,
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
                            {(pageName === "fifa") ?
                                <Trophy className="fifa-icon" />
                                :
                                <Music
                                    style={{
                                        width: "20px",
                                        height: "20px",
                                        color: "white"
                                    }}
                                />
                            }
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