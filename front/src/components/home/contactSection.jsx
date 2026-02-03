import { useState } from "react";
import { Send, Mail, User, MessageSquare, FileText } from "lucide-react";
// import { submitContactForm } from "@/lib/api";
// import { toast } from "@/hooks/use-toast";

const ContactSection = () => {
  const [isLoading, setIsLoading] = useState(false);
  const [formData, setFormData] = useState({
    name: "",
    email: "",
    subject: "",
    message: "",
  });

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsLoading(true);

    try {
      await submitContactForm(formData);
      toast({
        title: "Message Sent!",
        description: "Thank you for reaching out. We'll get back to you soon.",
      });
      setFormData({ name: "", email: "", subject: "", message: "" });
    } catch (error) {
      toast({
        title: "Error",
        description: "Failed to send message. Please try again.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <section id="contact" className="py-5">
      <div className="container">
        <div className="mx-auto" style={{ maxWidth: "600px" }}>
          <div className="text-center mb-5">
            <h2 className="h1 fw-bold mb-3">Get in Touch</h2>
            <p className="lead text-muted">
              Have questions or feedback? We'd love to hear from you.
            </p>
          </div>

          <div className="card glass-card">
            <div className="card-header">
              <h5 className="card-title mb-0 d-flex align-items-center gap-2">
                <Mail
                  style={{
                    width: "20px",
                    height: "20px",
                    color: "var(--primary)",
                  }}
                />
                Send us a Message
              </h5>
            </div>
            <div className="card-body">
              <form
                onSubmit={handleSubmit}
                className="needs-validation"
                noValidate
              >
                <div className="row g-3 mb-3">
                  <div className="col-md-6">
                    <label
                      htmlFor="name"
                      className="form-label d-flex align-items-center gap-2"
                    >
                      <User
                        style={{ width: "16px", height: "16px" }}
                        className="text-muted"
                      />
                      Name
                    </label>
                    <input
                      type="text"
                      className="form-control"
                      id="name"
                      placeholder="Your name"
                      value={formData.name}
                      onChange={(e) =>
                        setFormData({ ...formData, name: e.target.value })
                      }
                      required
                    />
                  </div>
                  <div className="col-md-6">
                    <label
                      htmlFor="email"
                      className="form-label d-flex align-items-center gap-2"
                    >
                      <Mail
                        style={{ width: "16px", height: "16px" }}
                        className="text-muted"
                      />
                      Email
                    </label>
                    <input
                      type="email"
                      className="form-control"
                      id="email"
                      placeholder="your@email.com"
                      value={formData.email}
                      onChange={(e) =>
                        setFormData({ ...formData, email: e.target.value })
                      }
                      required
                    />
                  </div>
                </div>

                <div className="mb-3">
                  <label
                    htmlFor="subject"
                    className="form-label d-flex align-items-center gap-2"
                  >
                    <FileText
                      style={{ width: "16px", height: "16px" }}
                      className="text-muted"
                    />
                    Subject
                  </label>
                  <input
                    type="text"
                    className="form-control"
                    id="subject"
                    placeholder="What's this about?"
                    value={formData.subject}
                    onChange={(e) =>
                      setFormData({ ...formData, subject: e.target.value })
                    }
                    required
                  />
                </div>

                <div className="mb-4">
                  <label
                    htmlFor="message"
                    className="form-label d-flex align-items-center gap-2"
                  >
                    <MessageSquare
                      style={{ width: "16px", height: "16px" }}
                      className="text-muted"
                    />
                    Message
                  </label>
                  <textarea
                    className="form-control"
                    id="message"
                    placeholder="Your message..."
                    rows={5}
                    value={formData.message}
                    onChange={(e) =>
                      setFormData({ ...formData, message: e.target.value })
                    }
                    required
                    style={{ resize: "none" }}
                  />
                </div>

                <button
                  type="submit"
                  className="btn btn-gradient w-100"
                  disabled={isLoading}
                >
                  {isLoading ? (
                    <span className="d-flex align-items-center justify-content-center gap-2">
                      <div
                        className="spinner-border spinner-border-sm"
                        role="status"
                      >
                        <span className="visually-hidden">Loading...</span>
                      </div>
                      Sending...
                    </span>
                  ) : (
                    <span className="d-flex align-items-center justify-content-center gap-2">
                      <Send style={{ width: "16px", height: "16px" }} />
                      Send Message
                    </span>
                  )}
                </button>
              </form>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
};

export default ContactSection;

<style jsx>{`
  .glass-card {
    background: rgba(255, 255, 255, 0.7);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(255, 255, 255, 0.2);
    border-radius: 12px;
  }

  .btn-gradient {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    border: none;
  }
`}</style>;
