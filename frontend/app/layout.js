import "./globals.css";

export const metadata = {
  title: "Resume & Profile Analyzer",
  description:
    "Review profile quality, detect skills, and predict a resume category.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
