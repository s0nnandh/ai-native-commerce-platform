const Footer = () => {
  const currentYear = new Date().getFullYear();
  
  return (
    <footer className="bg-white dark:bg-gray-800 shadow-inner mt-auto">
      <div className="container mx-auto px-4 py-8">
        <div className="grid grid-cols-1 md:grid-cols-4 gap-8">
          <div>
            <h3 className="text-primary font-semibold mb-4">EverGlow Labs</h3>
            <p className="text-text-secondary dark:text-gray-400 text-sm mb-4">
              Nature and science co-authoring skincare that actually works.
            </p>
            <p className="text-text-secondary dark:text-gray-400 text-sm">
              &copy; {currentYear} EverGlow Labs. All rights reserved.
            </p>
          </div>
          
          <div>
            <h3 className="text-primary font-semibold mb-4">Shop</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Skincare
                </a>
              </li>
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Body Care
                </a>
              </li>
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Hair Care
                </a>
              </li>
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Gift Sets
                </a>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-primary font-semibold mb-4">About</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Our Philosophy
                </a>
              </li>
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Sustainability
                </a>
              </li>
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Ingredients
                </a>
              </li>
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Our Story
                </a>
              </li>
            </ul>
          </div>
          
          <div>
            <h3 className="text-primary font-semibold mb-4">Legal</h3>
            <ul className="space-y-2">
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Privacy Policy
                </a>
              </li>
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Terms of Service
                </a>
              </li>
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Contact
                </a>
              </li>
              <li>
                <a href="#" className="text-text-secondary dark:text-gray-400 hover:text-primary dark:hover:text-white text-sm">
                  Shipping & Returns
                </a>
              </li>
            </ul>
          </div>
        </div>
        
        <div className="mt-8 pt-6 border-t border-gray-200 dark:border-gray-700">
          <p className="text-text-secondary dark:text-gray-400 text-xs text-center">
            Carbon-neutral supply chain | FSC-certified packaging | 1% of revenue funds reef-safe sunscreen education
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;
