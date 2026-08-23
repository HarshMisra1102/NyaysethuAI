"use client";
import { useEffect } from "react"; import { useRouter } from "next/navigation"; import { auth } from "@/lib/auth";
export function Protected({children}:{children:React.ReactNode}){const router=useRouter();useEffect(()=>{if(!auth.token())router.replace("/login")},[router]);if(!auth.token())return <main className="page"><div className="shell">Loading your secure workspace…</div></main>;return <>{children}</>}
