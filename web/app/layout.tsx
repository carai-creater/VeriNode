import type { Metadata } from "next";
import { JetBrains_Mono, Noto_Sans_JP } from "next/font/google";
import "./globals.css";

const noto = Noto_Sans_JP({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
  variable: "--font-geist-sans",
});

const jetbrains = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["400", "500"],
  variable: "--font-geist-mono",
});

export const metadata: Metadata = {
  title: "VeriNode — AI ファクトチェック API",
  description:
    "AIの回答に、確かな根拠を。リアルタイムのウェブ検索と信頼性スコア、引用エビデンスを API で提供。",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="ja" className={`${noto.variable} ${jetbrains.variable}`}>
      <body className="min-h-screen bg-[rgb(9,11,16)] font-sans antialiased">
        {children}
      </body>
    </html>
  );
}
