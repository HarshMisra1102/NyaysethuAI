"use client";
import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname, useRouter } from "next/navigation";
import { auth } from "@/lib/auth";
const publicLinks = [["Legal Solutions", "/#solutions"], ["About", "/#about"], ["Pricing", "/#pricing"], ["Contact", "/#contact"]] as const;
const workspaceLinks = [["Workspace", "/dashboard"], ["Cases", "/cases"], ["Assistant", "/chat"], ["Documents", "/documents"]] as const;
export function Navbar() {
  const router = useRouter(); const path = usePathname();
  const [signed, setSigned] = useState(false); const [open, setOpen] = useState(false);
  useEffect(() => setSigned(Boolean(auth.token())), [path]);
  const close = () => setOpen(false);
  return <header className="nav"><div className="shell navin">
    <Link className="brand" href="/" onClick={close}><i className="brand-mark">N</i>Nyaya<span>Setu</span><small>-AI</small></Link>
    <button className="btn secondary nav-toggle" type="button" aria-label="Toggle navigation" aria-expanded={open} onClick={() => setOpen(!open)}>Menu</button>
    <nav className={`links ${open ? "open" : ""}`} aria-label="Main navigation">
      {signed ? workspaceLinks.map(([label, href]) => <Link key={href} className={path === href || (href !== "/dashboard" && path.startsWith(`${href}/`)) ? "active" : ""} href={href} onClick={close}>{label}</Link>) : publicLinks.map(([label, href]) => <Link key={href} href={href} onClick={close}>{label}</Link>)}
      {signed ? <button className="btn secondary" onClick={() => { auth.clear(); close(); router.push("/"); }}>Log out</button> : <Link className="btn" href="/register" onClick={close}>Get started</Link>}
    </nav>
  </div></header>;
}
