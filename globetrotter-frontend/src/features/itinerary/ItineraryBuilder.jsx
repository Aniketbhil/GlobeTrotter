import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Map, Clock, Plus, Calendar, MapPin } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { getItinerary } from './itineraryApi';
import { AddStopModal } from './AddStopModal';
import { AddActivityModal } from './AddActivityModal';

export const ItineraryBuilder = () => {
  const { tripId } = useParams();
  const [itinerary, setItinerary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const [isAddStopModalOpen, setIsAddStopModalOpen] = useState(false);
  const [activityModalData, setActivityModalData] = useState({ isOpen: false, day: null });

  const fetchItinerary = useCallback(async () => {
    setIsLoading(true);
    try {
      const data = await getItinerary(tripId);
      setItinerary(data);
    } catch (error) {
      console.error("Failed to load itinerary", error);
    } finally {
      setIsLoading(false);
    }
  }, [tripId]);

  useEffect(() => {
    fetchItinerary();
  }, [fetchItinerary]);

  if (isLoading) return <div className="p-12 text-center text-text-muted animate-pulse">Loading itinerary details...</div>;
  if (!itinerary) return <div className="p-12 text-center text-error">Failed to load trip.</div>;

  const hasDays = itinerary.days && itinerary.days.length > 0;

  return (
    <div className="max-w-4xl mx-auto space-y-6 animate-in fade-in duration-500 pb-16">
      
      <Link to="/dashboard" className="inline-flex items-center text-sm font-medium text-text-secondary hover:text-primary transition-colors">
        <ArrowLeft size={16} className="mr-2" /> Back to Dashboard
      </Link>
      
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 bg-surface p-6 rounded-2xl border border-border-default shadow-sm">
        <div>
          <h1 className="text-3xl font-bold font-manrope text-text-primary">{itinerary.trip_name}</h1>
          <div className="flex items-center gap-2 mt-2 text-sm text-text-secondary">
            <Calendar size={16} className="text-primary" />
            <span>{new Date(itinerary.start_date).toLocaleDateString()} - {new Date(itinerary.end_date).toLocaleDateString()}</span>
          </div>
        </div>
        
        {/* Updated Header Actions (Includes Budget Link) */}
        <div className="flex gap-3 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <Link to={`/trips/${tripId}/budget`}>
            <Button variant="secondary" className="gap-2 shrink-0">
               View Budget
            </Button>
          </Link>
          <Button onClick={() => setIsAddStopModalOpen(true)} className="gap-2 shrink-0">
            <Plus size={18} /> Add Section
          </Button>
        </div>
      </div>

      {/* Screen 5 Layout Implementation */}
      {!hasDays ? (
        <Card className="flex flex-col items-center justify-center py-20 text-center border-dashed border-2 bg-surface-muted/50">
          <div className="w-16 h-16 bg-primary-soft rounded-full flex items-center justify-center mb-4 text-primary">
            <Map size={32} />
          </div>
          <h3 className="text-xl font-semibold text-text-primary font-manrope">No sections added yet</h3>
          <p className="text-text-secondary max-w-sm mt-2 mb-6">Build your itinerary sections by adding travel stops.</p>
          <Button onClick={() => setIsAddStopModalOpen(true)}>+ Add First Section</Button>
        </Card>
      ) : (
        <div className="space-y-6">
          {itinerary.days.map((day, index) => (
            <Card key={day.date} className="overflow-hidden border-border-strong shadow-sm hover:border-primary/40 transition-colors">
              {/* Card Header matching Screen 5 */}
              <div className="bg-surface-muted p-5 border-b border-border-subtle flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
                <div>
                  <h3 className="text-xl font-bold font-manrope text-text-primary">
                    Section {index + 1}: {day.city?.name}
                  </h3>
                  <p className="text-sm text-text-secondary mt-2">
                    <span className="font-medium text-text-primary">Date Range:</span> {new Date(day.date).toLocaleDateString()}
                  </p>
                </div>
                <div className="sm:text-right bg-surface px-4 py-2 rounded-xl border border-border-default shadow-sm">
                  <p className="text-xs font-semibold text-text-secondary uppercase tracking-wider">Budget of this section</p>
                  <p className="text-lg font-bold text-warning mt-0.5">${day.day_total_cost || "0.00"}</p>
                </div>
              </div>
              
              {/* Activities Content Area */}
              <CardContent className="p-5">
                <p className="text-sm font-medium text-text-secondary mb-3">All the necessary information about this section. This can be anything like travel section, hotel or any other activity.</p>
                
                <div className="space-y-2 mb-4">
                  {day.activities && day.activities.length > 0 ? (
                    day.activities.map(act => (
                      <div key={act.id} className="flex items-center justify-between bg-surface-hover p-3 rounded-xl border border-border-subtle">
                        <div className="flex items-center gap-3">
                          <Clock size={16} className="text-accent" />
                          <span className="text-text-primary font-medium">{act.activity?.name}</span>
                        </div>
                        <span className="text-text-secondary text-sm font-semibold">${act.effective_cost}</span>
                      </div>
                    ))
                  ) : (
                    <div className="text-sm text-text-muted italic bg-surface-muted p-3 rounded-xl border border-dashed border-border-strong text-center">
                      No activities added to this section yet.
                    </div>
                  )}
                </div>

                <Button 
                  variant="secondary" 
                  size="sm" 
                  onClick={() => setActivityModalData({ isOpen: true, day })}
                  className="w-full sm:w-auto"
                >
                  <Plus size={16} className="mr-2" /> Add Activity
                </Button>
              </CardContent>
            </Card>
          ))}
          
          {/* Add Another Section Button */}
          <Button onClick={() => setIsAddStopModalOpen(true)} className="w-full py-6 text-lg rounded-2xl border-2 border-dashed border-primary bg-primary-soft text-primary hover:bg-primary/10 hover:border-primary hover:text-primary-active transition-all">
            + Add another Section
          </Button>
        </div>
      )}

      {/* Modals */}
      <AddStopModal 
        isOpen={isAddStopModalOpen} 
        onClose={() => setIsAddStopModalOpen(false)} 
        tripId={tripId} 
        onStopAdded={fetchItinerary} 
      />
      
      <AddActivityModal 
        isOpen={activityModalData.isOpen}
        onClose={() => setActivityModalData({ isOpen: false, day: null })}
        tripId={tripId}
        selectedDay={activityModalData.day}
        onActivityAdded={fetchItinerary}
      />
    </div>
  );
};