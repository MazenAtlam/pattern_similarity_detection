import PagesNavbar from '../layout/PagesNavbar';

const Layout = ({ pageName, pageTitle, pageDescription, children }) => {
    return (
        <div className="min-h-screen flex flex-col bg-background">
            <PagesNavbar
                pageName={pageName}
                pageTitle={pageTitle}
                pageDescription={pageDescription}
            />
            <main className="flex-1 pt-16">
                {children}
            </main>
        </div>
    );
};

export default Layout;