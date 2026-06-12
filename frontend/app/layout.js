import "./globals.css";

export const metadata = {
  title: "Resume & Profile Analyzer",
  description:
    "Identify skill gaps, match roles, and build a clearer career path.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
