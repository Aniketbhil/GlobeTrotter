import { useEffect, useState } from 'react';
import { Search, MapPin, Activity as ActivityIcon, Clock, DollarSign, TrendingUp, Globe } from 'lucide-react';
import { Card, CardContent } from '../../components/ui/Card';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { searchCities, searchActivities } from './exploreApi';

export const Explore = () => {
  const [activeTab, setActiveTab] = useState('cities'); // 'cities' or 'activities'
  const [searchQuery, setSearchQuery] = useState('');
  const [cities, setCities] = useState([]);
  const [activities, setActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    fetchData();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [activeTab]);

  const fetchData = async () => {
    setIsLoading(true);
    try {
      if (activeTab === 'cities') {
        const data = await searchCities(searchQuery);
        setCities(data.items || []);
      } else {
        const data = await searchActivities(searchQuery);
        setActivities(data.items || []);
      }
    } catch (error) {
      console.error("Failed to fetch explore data", error);
    } finally {
      setIsLoading(false);
    }
  };

  const handleSearch = (e) => {
    e.preventDefault();
    fetchData();
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6 animate-in fade-in duration-500 pb-16">
      
      {/* Header & Search */}
      <div className="mb-8">
        <h1 className="text-3xl font-bold font-manrope text-text-primary">Explore</h1>
        <p className="text-text-secondary mt-1">Discover popular destinations and exciting activities for your next trip.</p>
      </div>

      <div className="flex flex-col sm:flex-row gap-4 mb-6">
        <form onSubmit={handleSearch} className="relative flex-1">
          <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-text-muted" size={20} />
          <input 
            type="text"
            placeholder={`Search ${activeTab}...`}
            value={searchQuery}
            onChange={(e) => setSearchQuery(e.target.value)}
            className="h-12 w-full rounded-2xl border border-border-strong bg-surface pl-12 pr-4 text-base text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus shadow-sm transition-colors"
          />
        </form>
        <Button onClick={fetchData} size="lg" className="shrink-0">Search</Button>
      </div>

      {/* Tabs */}
      <div className="flex p-1 bg-surface-muted rounded-xl w-full sm:w-auto mb-6 border border-border-default">
        <button
          onClick={() => { setActiveTab('cities'); setSearchQuery(''); }}
          className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
            activeTab === 'cities' 
              ? 'bg-surface text-primary shadow-sm border border-border-subtle' 
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          <MapPin size={18} /> Cities
        </button>
        <button
          onClick={() => { setActiveTab('activities'); setSearchQuery(''); }}
          className={`flex-1 sm:flex-none flex items-center justify-center gap-2 px-6 py-2.5 rounded-lg text-sm font-semibold transition-all ${
            activeTab === 'activities' 
              ? 'bg-surface text-primary shadow-sm border border-border-subtle' 
              : 'text-text-secondary hover:text-text-primary'
          }`}
        >
          <ActivityIcon size={18} /> Activities
        </button>
      </div>

      {/* Results Grid */}
      {isLoading ? (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          {[1, 2, 3, 4, 5, 6, 7, 8].map(i => (
             <Card key={i} className="h-72 animate-pulse bg-surface-muted border-none" />
          ))}
        </div>
      ) : (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6">
          
          {/* CITIES TAB */}
          {activeTab === 'cities' && (
            cities.length === 0 ? (
              <div className="col-span-full py-16 flex flex-col items-center text-center border-2 border-dashed border-border-strong rounded-2xl bg-surface-muted/50">
                <Globe className="text-text-muted mb-3" size={40} />
                <h3 className="text-lg font-semibold text-text-primary">No cities found</h3>
                <p className="text-text-secondary mt-1">Try searching for a different location.</p>
              </div>
            ) : (
              cities.map(city => (
                <Card key={city.id} className="overflow-hidden hover:border-primary/40 hover:shadow-md transition-all group flex flex-col h-full">
                  <div className="h-40 bg-surface-muted relative overflow-hidden border-b border-border-subtle shrink-0">
                    {city.image_url ? (
                      <img src={city.image_url} alt={city.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-linear-to-br from-primary-soft to-surface-hover group-hover:scale-105 transition-transform duration-500">
                        <MapPin size={40} className="text-primary opacity-40" />
                      </div>
                    )}
                    <div className="absolute top-3 right-3 flex gap-2">
                      <Badge variant="success" className="shadow-sm border border-success/20">
                        <TrendingUp size={12} className="mr-1" /> {city.popularity_score}
                      </Badge>
                    </div>
                  </div>
                  <CardContent className="p-5 flex-1 flex flex-col justify-between">
                    <div>
                      <h3 className="font-manrope text-xl font-bold text-text-primary truncate">{city.name}</h3>
                      <p className="text-sm font-medium text-text-secondary mt-0.5">{city.country}</p>
                    </div>
                    <div className="mt-4 pt-4 border-t border-border-subtle flex items-center justify-between">
                      <span className="text-xs font-semibold text-text-muted uppercase tracking-wider">Cost Index</span>
                      <div className="flex gap-0.5 text-warning">
                        {/* Simple cost index visualizer (1 to 5 scale assumed) */}
                        {Array.from({ length: 5 }).map((_, i) => (
                          <DollarSign key={i} size={14} className={i < city.cost_index ? "opacity-100" : "opacity-30"} />
                        ))}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )
          )}

          {/* ACTIVITIES TAB */}
          {activeTab === 'activities' && (
            activities.length === 0 ? (
              <div className="col-span-full py-16 flex flex-col items-center text-center border-2 border-dashed border-border-strong rounded-2xl bg-surface-muted/50">
                <ActivityIcon className="text-text-muted mb-3" size={40} />
                <h3 className="text-lg font-semibold text-text-primary">No activities found</h3>
                <p className="text-text-secondary mt-1">Try adjusting your search criteria.</p>
              </div>
            ) : (
              activities.map(act => (
                <Card key={act.id} className="overflow-hidden hover:border-accent/40 hover:shadow-md transition-all group flex flex-col h-full">
                  <div className="h-40 bg-surface-muted relative overflow-hidden border-b border-border-subtle shrink-0">
                    {act.image_url ? (
                      <img src={act.image_url} alt={act.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
                    ) : (
                      <div className="w-full h-full flex items-center justify-center bg-linear-to-br from-accent-soft to-surface-hover group-hover:scale-105 transition-transform duration-500">
                        <ActivityIcon size={40} className="text-accent opacity-40" />
                      </div>
                    )}
                    <div className="absolute top-3 right-3">
                      <Badge variant="accent" className="shadow-sm border border-accent/20 capitalize">
                        {act.type}
                      </Badge>
                    </div>
                  </div>
                  <CardContent className="p-5 flex-1 flex flex-col justify-between">
                    <div>
                      <h3 className="font-manrope text-lg font-bold text-text-primary line-clamp-2 leading-tight">{act.name}</h3>
                      {act.description && (
                        <p className="text-sm text-text-secondary mt-2 line-clamp-2">{act.description}</p>
                      )}
                    </div>
                    
                    <div className="flex items-center justify-between mt-4 pt-4 border-t border-border-subtle">
                      <div className="flex items-center gap-1.5 text-sm font-medium text-text-secondary">
                        <Clock size={16} className="text-text-muted" />
                        {act.duration_mins} min
                      </div>
                      <div className="text-lg font-bold text-text-primary">
                        ${act.cost}
                      </div>
                    </div>
                  </CardContent>
                </Card>
              ))
            )
          )}

        </div>
      )}
    </div>
  );
};