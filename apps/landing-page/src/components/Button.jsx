export function ButtonPrimary({ children, size = 'md', className = '' }) {
  const sizes = {
    sm: 'px-6 py-3 text-sm',
    md: 'px-8 py-4 text-base',
    lg: 'px-10 py-5 text-lg',
  }

  return (
    <button
      className={`bg-cta-primary rounded-full font-semibold text-white shadow-cta-glow
        transition-all duration-200 hover:brightness-110 hover:shadow-[0_4px_40px_rgba(124,58,237,0.65)]
        ${sizes[size]} ${className}`}
    >
      {children}
    </button>
  )
}

export function ButtonGhost({ children, size = 'md', className = '' }) {
  const sizes = {
    sm: 'px-6 py-3 text-sm',
    md: 'px-8 py-4 text-base',
  }

  return (
    <button
      className={`bg-glass-fill border border-glass-border rounded-full font-semibold text-white
        transition-all duration-200 hover:bg-glass-fill-strong
        ${sizes[size]} ${className}`}
    >
      {children}
    </button>
  )
}
