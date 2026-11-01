import type { Metadata } from "next";
import type { ReactNode } from "react";
import "./globals.css";
import "./psychology.css";
import "./share.css";
import "./polish.css";

export const metadata: Metadata = {
  title: "Feminism Dating — Connect with confidence",
  description: "A safety-first dating experience with relationship coaching, love and intimacy reflections, Iranian diaspora identity exploration, and practical safety tools.",
  keywords: ["safer dating", "relationship coaching", "dating safety", "personality quiz", "feminism dating"],
};

export default function RootLayout({ children }: { children: ReactNode }) {
  return <html lang="en"><body>{children}</body></html>;
}
