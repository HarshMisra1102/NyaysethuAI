import Link from "next/link";

export function Footer() {
  return (
    <footer className="footer">
      <div className="shell footer-marketing">
        <div>
          <strong>Nyaysethu</strong>
          <p>A bridge to clearer, more accessible justice.</p>
        </div>
        <div>
          <b>Explore</b>
          <Link href="/">Home</Link>
          <Link href="/#about">About</Link>
          <Link href="/#pricing">Pricing</Link>
          <Link href="/#contact">Contact</Link>
        </div>
        <div>
          <b>Resources</b>
          <a href="#">Blog</a>
          <a href="#">Changelog</a>
          <a href="#">Privacy policy</a>
          <a href="#">Terms</a>
        </div>
        <div>
          <b>Follow</b>
          <a href="#">Instagram</a>
          <a href="#">X / Twitter</a>
          <a href="#">LinkedIn</a>
        </div>
      </div>
      <div className="shell footer-bottom">
        © 2026 Nyaysethu. All rights reserved.
        <span>Guidance is informational, not legal advice.</span>
      </div>
    </footer>
  );
}
