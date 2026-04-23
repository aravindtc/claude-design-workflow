const columns = [
  {
    title: 'Product',
    links: ['Features', 'Pricing', 'Integrations', 'Changelog', 'API'],
  },
  {
    title: 'Company',
    links: ['About', 'Blog', 'Careers', 'Press', 'Contact'],
  },
  {
    title: 'Resources',
    links: ['Documentation', 'Help Center', 'Community', 'Status', 'Security'],
  },
  {
    title: 'Legal',
    links: ['Privacy', 'Terms', 'Cookie Policy'],
  },
]

export default function Footer() {
  return (
    <footer className="bg-base-surface border-t border-base-border flex flex-col gap-12 w-full px-6 lg:px-16 pt-16 pb-12">
      {/* Footer Top */}
      <div className="flex flex-col lg:flex-row items-start justify-between gap-12">
        {/* Brand */}
        <div className="flex flex-col gap-4 w-full lg:w-[280px]">
          <span className="text-2xl font-semibold text-white tracking-tight">
            NeuralFlow
          </span>
          <p className="text-base text-text-muted leading-normal">
            AI-powered productivity<br />for modern teams.
          </p>
        </div>

        {/* Link Columns */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-10 lg:gap-16">
          {columns.map((col) => (
            <div key={col.title} className="flex flex-col gap-4">
              <span className="text-xs font-semibold text-white tracking-[0.04em]">
                {col.title}
              </span>
              {col.links.map((link) => (
                <a
                  key={link}
                  href="#"
                  className="text-sm font-medium text-text-muted leading-normal hover:text-text-secondary transition-colors"
                >
                  {link}
                </a>
              ))}
            </div>
          ))}
        </div>
      </div>

      {/* Divider */}
      <div className="w-full h-px bg-base-border" />

      {/* Copyright */}
      <span className="text-sm font-medium text-text-muted">
        &copy; 2026 NeuralFlow, Inc. All rights reserved.
      </span>
    </footer>
  )
}
