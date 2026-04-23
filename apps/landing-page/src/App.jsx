import Header from './components/Header'
import Hero from './components/Hero'
import Features from './components/Features'
import SocialProof from './components/SocialProof'
import SecondaryCTA from './components/SecondaryCTA'
import Footer from './components/Footer'

export default function App() {
  return (
    <div className="bg-base-bg min-h-screen flex flex-col items-center">
      <Header />
      <Hero />
      <Features />
      <SocialProof />
      <SecondaryCTA />
      <Footer />
    </div>
  )
}
