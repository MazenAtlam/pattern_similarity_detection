import PagesNavbar from '../layout/PagesNavbar';

const Layout = ({ pageTitle, pageDescription, children }) => {
    return (
        <div className="min-h-screen flex flex-col bg-background">
            <PagesNavbar
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