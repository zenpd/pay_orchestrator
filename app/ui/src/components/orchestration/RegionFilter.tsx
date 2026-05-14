import React, { useEffect, useState } from 'react'
import { Globe } from 'lucide-react'

interface RegionFilterProps {
  selectedRegion: string
  onRegionChange: (region: string) => void
}

export const RegionFilter: React.FC<RegionFilterProps> = ({ selectedRegion, onRegionChange }) => {
  const [regions, setRegions] = useState<{ name: string; label: string }[]>([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    setLoading(true)
    fetch(`${import.meta.env.VITE_API_BASE_URL ?? ''}/api/v1/payment/regions`)
      .then(res => res.json())
      .then(data => {
        const regionList = (data.regions || ['US', 'UK', 'SA', 'EUR']).map((r: string) => ({
          name: r,
          label: data.descriptions?.[r] || r,
        }))
        setRegions(regionList)
      })
      .catch(() => {
        setRegions([
          { name: 'US', label: 'United States' },
          { name: 'UK', label: 'United Kingdom' },
          { name: 'SA', label: 'South Africa' },
          { name: 'EUR', label: 'Europe' },
        ])
      })
      .finally(() => setLoading(false))
  }, [])

  return (
    <div className="card mb-4">
      <div className="card-header flex items-center justify-between">
        <div className="flex items-center gap-2">
          <Globe className="w-4 h-4 text-indigo-600" />
          <h3 className="font-semibold">Region Selection</h3>
        </div>
      </div>
      <div className="card-body">
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          {regions.map(region => (
            <button
              key={region.name}
              onClick={() => onRegionChange(region.name)}
              className={`p-2 rounded-lg transition-all text-sm font-medium ${
                selectedRegion === region.name
                  ? 'bg-indigo-600 text-white shadow-lg'
                  : 'bg-gray-100 text-gray-700 hover:bg-gray-200'
              }`}
            >
              {region.name}
            </button>
          ))}
        </div>
        <p className="text-xs text-gray-500 mt-3">Selected: <span className="font-semibold">{regions.find(r => r.name === selectedRegion)?.label || selectedRegion}</span></p>
      </div>
    </div>
  )
}
