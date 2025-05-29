import { useEffect } from 'react';
import Layout from '../components/layout/Layout';
import SearchBar from '../components/search/SearchBar';
import ResponseArea from '../components/search/ResponseArea';
import CitationsSection from '../components/search/CitationsSection';
import ProductGrid from '../components/product/ProductGrid';
import { useProductStore } from '../store/productStore';

const HomePage = () => {
  const { loadAllProducts } = useProductStore();
  
  // Load all products when the page loads
  useEffect(() => {
    loadAllProducts();
  }, [loadAllProducts]);
  
  return (
    <Layout>
      <div className="flex flex-col items-center">
        {/* Hero Section */}
        <div className="w-full bg-background dark:bg-gray-900 py-16">
          <div className="w-full max-w-6xl mx-auto text-center px-4">
            <h1 className="text-4xl md:text-5xl font-bold text-primary dark:text-leaf mb-6">
              EverGlow Labs
            </h1>
            <p className="text-text-secondary dark:text-gray-300 text-xl md:text-2xl max-w-3xl mx-auto mb-8">
              Where nature and science co-author skincare that actually works.
            </p>
            <div className="flex flex-col sm:flex-row justify-center gap-4 mb-8">
              <button className="bg-primary hover:bg-evergreen text-white font-medium py-3 px-6 rounded-md transition-colors">
                Shop Products
              </button>
              <button className="bg-transparent border border-primary text-primary hover:bg-primary/10 font-medium py-3 px-6 rounded-md transition-colors">
                Learn More
              </button>
            </div>
          </div>
        </div>
        
        {/* Philosophy Section */}
        <section className="w-full py-16 bg-white dark:bg-gray-800">
          <div className="w-full max-w-6xl mx-auto px-4">
            <h2 className="text-3xl font-bold text-primary dark:text-white text-center mb-12">
              Our Philosophy
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div className="bg-background dark:bg-gray-700 p-6 rounded-lg shadow-sm">
                <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-primary dark:text-white mb-3">Plant-Powered, Clinically Proven</h3>
                <ul className="text-text-secondary dark:text-gray-300 space-y-2">
                  <li className="flex items-start">
                    <span className="text-accent mr-2">•</span>
                    <span>100% vegan, cruelty-free, and silicone-free</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-accent mr-2">•</span>
                    <span>High-potency botanicals paired with gold-standard actives</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-accent mr-2">•</span>
                    <span>Third-party tested for efficacy and safety</span>
                  </li>
                </ul>
              </div>
              
              <div className="bg-background dark:bg-gray-700 p-6 rounded-lg shadow-sm">
                <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-primary dark:text-white mb-3">Radical Transparency</h3>
                <ul className="text-text-secondary dark:text-gray-300 space-y-2">
                  <li className="flex items-start">
                    <span className="text-accent mr-2">•</span>
                    <span>Full-dose percentages of hero ingredients on every carton</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-accent mr-2">•</span>
                    <span>Carbon-neutral supply chain; FSC-certified packaging</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-accent mr-2">•</span>
                    <span>Real, verified customer reviews only—no paid placements</span>
                  </li>
                </ul>
              </div>
              
              <div className="bg-background dark:bg-gray-700 p-6 rounded-lg shadow-sm">
                <div className="w-12 h-12 bg-primary/20 rounded-full flex items-center justify-center mb-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M3.055 11H5a2 2 0 012 2v1a2 2 0 002 2 2 2 0 012 2v2.945M8 3.935V5.5A2.5 2.5 0 0010.5 8h.5a2 2 0 012 2 2 2 0 104 0 2 2 0 012-2h1.064M15 20.488V18a2 2 0 012-2h3.064M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
                <h3 className="text-xl font-semibold text-primary dark:text-white mb-3">Barrier-First, Planet-First</h3>
                <ul className="text-text-secondary dark:text-gray-300 space-y-2">
                  <li className="flex items-start">
                    <span className="text-accent mr-2">•</span>
                    <span>pH-optimized, microbiome-friendly formulas</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-accent mr-2">•</span>
                    <span>Cold-processed where possible to preserve phyto-nutrients</span>
                  </li>
                  <li className="flex items-start">
                    <span className="text-accent mr-2">•</span>
                    <span>1% of revenue funds reef-safe sunscreen education</span>
                  </li>
                </ul>
              </div>
            </div>
          </div>
        </section>
        
        {/* Search Section */}
        <section className="w-full py-16 bg-background dark:bg-gray-900">
          <div className="w-full max-w-4xl mx-auto px-4">
            <h2 className="text-3xl font-bold text-primary dark:text-white text-center mb-8">
              Find Your Perfect Match
            </h2>
            <p className="text-text-secondary dark:text-gray-300 text-lg text-center mb-8">
              Discover products tailored to your unique needs through our conversational search
            </p>
            <SearchBar />
            <ResponseArea />
            <CitationsSection />
          </div>
        </section>
        
        {/* Products Section */}
        <section className="w-full py-16 bg-white dark:bg-gray-800">
          <div className="w-full max-w-6xl mx-auto px-4">
            <h2 className="text-3xl font-bold text-primary dark:text-white text-center mb-8">
              Featured Products
            </h2>
            <ProductGrid />
          </div>
        </section>
      </div>
    </Layout>
  );
};

export default HomePage;
