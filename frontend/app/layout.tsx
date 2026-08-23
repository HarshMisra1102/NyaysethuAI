import type { Metadata } from "next";
import "./globals.css";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
export const metadata: Metadata = { title: "NyayaSetu | Civic & Legal Guidance", description: "Understand Your Rights. Take the Right Step." };
export default function RootLayout({ children }: Readonly<{ children: React.ReactNode }>) { return <html lang="en"><body><Navbar />{children}<Footer /></body></html>; }
