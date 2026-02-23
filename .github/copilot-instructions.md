# Sentinel-Net-SE Frontend - Development Guide

## Project Overview
Sentinel-Net-SE is a professional, high-fidelity React frontend dashboard for a software reliability system. It features a "Dark Cyber" aesthetic with a sleek, modern design built with React, Tailwind CSS, Recharts, and Lucide React icons.

## Technology Stack
- **Framework**: React 18+ with TypeScript
- **Build Tool**: Vite
- **Styling**: Tailwind CSS with custom Dark Cyber theme
- **Charts**: Recharts
- **Icons**: Lucide React
- **State Management**: React Hooks (useState, useCallback)
- **Development Server**: Vite (Port 5173)

## Project Structure

```
sentinel-net/
├── src/
│   ├── components/          # Reusable UI components
│   │   ├── Sidebar.tsx       # Navigation sidebar
│   │   ├── RiskScoreHero.tsx # Risk score gauge component
│   │   ├── SemanticSignalFeed.tsx # Signal list component
│   │   ├── TemporalChart.tsx # Line chart for trends
│   │   ├── AIInsightsPanel.tsx # AI predictions panel
│   │   ├── RefreshButton.tsx # Refresh analysis button
│   │   └── index.ts          # Component exports
│   ├── pages/                # Page layout components
│   │   ├── OverviewPage.tsx   # Main dashboard overview
│   │   ├── SignalsPage.tsx    # Micro-crisis signals view
│   │   ├── TrendsPage.tsx     # Temporal trends analysis
│   │   ├── ReportsPage.tsx    # Risk reports & export
│   │   └── index.ts           # Page exports
│   ├── hooks/                # Custom React hooks
│   │   ├── useSystemData.ts  # Mock data hook (easily swappable for API)
│   │   └── index.ts          # Hook exports
│   ├── types/                # TypeScript type definitions
│   │   └── index.ts          # All type interfaces
│   ├── data/                 # Mock data
│   │   └── mockData.ts       # Sample system data
│   ├── App.tsx               # Main application component
│   ├── App.css               # App-level styles
│   ├── main.tsx              # App entry point
│   └── index.css             # Global styles & Tailwind directives
├── tailwind.config.js        # Tailwind configuration with custom theme
├── postcss.config.js         # PostCSS configuration
├── vite.config.ts            # Vite configuration
├── tsconfig.json             # TypeScript configuration
└── package.json              # Dependencies and scripts
```

## Color Palette

### Dark Cyber Theme
- **Deep Charcoal**: `#1a1a2e` (Primary background)
- **Darker Charcoal**: `#0f0f1e` (Darker background)
- **Electric Blue**: `#00d4ff` (Primary accent, interactive)
- **Electric Blue Dark**: `#0099cc` (Hover/darker state)
- **Warning Orange**: `#ff6b35` (Alert/warning color)
- **Cyber Gray**: `#16213e` (Borders, subtle backgrounds)

## Key Components

### 1. **Sidebar Navigation**
- Fixed sidebar with collapsible menu
- Navigation items: Overview, Micro-Crisis Signals, Temporal Trends, Risk Reports
- Responsive design with status indicator
- **Path**: [src/components/Sidebar.tsx](src/components/Sidebar.tsx)

### 2. **Risk Score Hero**
- Central gauge showing "Software Failure Risk Score" (0-100)
- Radial progress visualization with color-coded health status
- Supporting metrics (Bug Growth, Dev Irregularity, Critical Issues)
- Real-time updates with hover effects
- **Path**: [src/components/RiskScoreHero.tsx](src/components/RiskScoreHero.tsx)

### 3. **Semantic Signal Feed**
- Dynamic list of recent signals (commits, issues, alerts)
- Status badges: Neutral (green), Urgent (red), Negative (orange)
- Timestamps with relative time formatting
- Source indicators (Commit, Issue, Alert)
- Hover effects for better interactivity
- **Path**: [src/components/SemanticSignalFeed.tsx](src/components/SemanticSignalFeed.tsx)

### 4. **Temporal Chart**
- Line chart visualization using Recharts
- Tracks "Bug Growth" and "Development Irregularity" metrics
- Custom styling with gradients and animations
- Interactive tooltips and legend
- **Path**: [src/components/TemporalChart.tsx](src/components/TemporalChart.tsx)

### 5. **AI Insights Panel**
- Explainable GenAI predictions
- Displays contributing factors in human-readable format
- Provides actionable recommendations
- Shows AI confidence score and last analysis timestamp
- **Path**: [src/components/AIInsightsPanel.tsx](src/components/AIInsightsPanel.tsx)

### 6. **Refresh Button**
- Triggers system data refresh with loading state
- Displays "Analyzing..." while loading
- Shows timestamp of last update
- Disabled state during loading
- **Path**: [src/components/RefreshButton.tsx](src/components/RefreshButton.tsx)

## Custom Hook: useSystemData

The `useSystemData` hook is designed to be easily swappable with your future REST API endpoints.

### Current Implementation
- Returns mock data from [src/data/mockData.ts](src/data/mockData.ts)
- Provides `refreshData` callback with simulated 1.5s delay
- Manages loading state automatically

### For Future API Integration
Replace the mock data with actual API calls:

```typescript
const refreshData = useCallback(async () => {
  setIsLoading(true);
  try {
    // Your FastAPI or Spring Boot endpoint
    const response = await fetch('/api/system-data');
    const newData = await response.json();
    setData(newData);
  } catch (error) {
    console.error('Failed to refresh data:', error);
  } finally {
    setIsLoading(false);
  }
}, []);
```

**Path**: [src/hooks/useSystemData.ts](src/hooks/useSystemData.ts)

## Pages

### Overview Page
Dashboard entry point with Risk Score Hero and Signal Feed

### Signals Page
Categorized view of all signals (Urgent, Negative, Neutral)

### Trends Page
Temporal analysis with AI insights panel

### Reports Page
Data export (JSON/CSV) and actionable recommendations

## Getting Started

### Prerequisites
- Node.js 16+ and npm

### Installation
```bash
npm install
```

### Development
```bash
npm run dev
```
Opens at `http://localhost:5173`

### Build
```bash
npm run build
```

### Preview Built Version
```bash
npm run preview
```

## Responsive Design

The dashboard is fully responsive:
- **Desktop (1440px+)**: Full sidebar + content layout
- **Tablet (1024px-1439px)**: Collapsible sidebar
- **Mobile (<1024px)**: Stack layout with mobile-optimized navigation

## Tailwind Custom Configuration

Custom utilities and colors are defined in [tailwind.config.js](tailwind.config.js):
- `bg-dark-charcoal`, `bg-cyber-gray-light`
- `text-electric-blue`, `text-warning-orange`
- `shadow-cyber-glow`, `shadow-cyber-intense`

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+

## Future Backend Integration

### For Spring Boot Integration
Create a REST endpoint in Spring Boot:
```java
@GetMapping("/api/system-data")
public ResponseEntity<SystemData> getSystemData() {
    // Return SystemData matching the TypeScript interface
}
```

### For FastAPI Integration
Create a FastAPI endpoint:
```python
@app.get("/api/system-data")
async def get_system_data():
    # Return SystemData JSON matching the TypeScript interface
```

### Mock Data Operations
The mock data in [src/data/mockData.ts](src/data/mockData.ts) simulates realistic failure scenarios and can be updated to test different dashboard states.

## Performance Optimizations

- Component-level code splitting via React.lazy (can be added)
- Tailwind CSS purging in production
- Vite's efficient bundling and HMR
- Memoized components using React.memo (can be added)

## Development Tips

1. **Adding New Components**: Create in `src/components/`, export via `index.ts`
2. **Modifying Data**: Update mock data types in `src/types/` and data in `src/data/mockData.ts`
3. **Styling**: Use Tailwind classes; add custom styles in `src/index.css`
4. **API Integration**: Modify `useSystemData` hook to call your backend
5. **Testing**: Create `.test.tsx` files alongside components

## Security Considerations

- Input validation on API responses
- XSS protection via React's default escaping
- CORS configuration for API endpoints (when backend is ready)
- Environment variables for API endpoints (.env)

## Accessibility

- Semantic HTML structure
- Color contrast meets WCAG AA standards
- Keyboard navigation support via Tailwind's focus states
- ARIA labels on interactive elements (can be enhanced)

## Known Limitations & Future Enhancements

- Mock data is static; replace with real API calls
- Chart currently shows 7 data points; extend with pagination
- Signals are not filterable; add filtering UI
- No authentication/authorization layer (add when needed)
- Export functionality is client-side; move to backend for large datasets

## Troubleshooting

### Port 5173 Already in Use
```bash
npm run dev -- --port 3000
```

### TypeScript Errors
Ensure `verbatimModuleSyntax` is true in tsconfig - all type imports must use `type` keyword

### Styling Not Applied
Check that Tailwind CSS is properly built:
```bash
npm run dev
```

## Support & Contributions

For issues or improvements, create detailed descriptions with:
- Affected component(s)
- Expected vs actual behavior
- Steps to reproduce
- Browser/OS information

## License

Project developed for Sentinel-Net-SE software reliability system.

---

**Last Updated**: February 17, 2026
**Status**: Production Ready
