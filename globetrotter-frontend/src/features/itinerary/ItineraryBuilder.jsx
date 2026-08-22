import { useEffect, useState, useCallback } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Map, Clock, Plus, Calendar, Share2, Trash2 } from 'lucide-react';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { getItinerary, deleteStop, deleteTripActivity } from './itineraryApi';
import { AddStopModal } from './AddStopModal';
import { AddActivityModal } from './AddActivityModal';
import { ShareTripModal } from '../sharing/ShareTripModal';
import { getCityImage } from '../../utils/imageResolver';

export const ItineraryBuilder = () => {
  const { tripId } = useParams();
  const [itinerary, setItinerary] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  
  const [isAddStopModalOpen, setIsAddStopModalOpen] = useState(false);
  const [isShareModalOpen, setIsShareModalOpen] = useState(false);
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

  const handleDeleteStop = async (stopId) => {
    if (window.confirm("Are you sure you want to remove this entire section and all its activities?")) {
      try {
        await deleteStop(tripId, stopId);
        fetchItinerary();
      } catch (error) {
        alert("Failed to delete section.");
      }
    }
  };

  const handleDeleteActivity = async (stopId, activityId) => {
    if (window.confirm("Remove this activity?")) {
      try {
        await deleteTripActivity(tripId, stopId, activityId);
        fetchItinerary();
      } catch (error) {
        alert("Failed to delete activity.");
      }
    }
  };

  if (isLoading) return <div className="p-12 text-center text-text-muted animate-pulse">Loading itinerary details...</div>;
  if (!itinerary) return <div className="p-12 text-center text-error">Failed to load trip.</div>;

  // Group the days by stop_id so one "Section" = one "Stop"
  const sections = [];
  let currentSection = null;

  itinerary?.days?.forEach(day => {
    if (!currentSection || currentSection.stop_id !== day.stop_id) {
      currentSection = {
        stop_id: day.stop_id,
        city: day.city,
        start_date: day.date,
        end_date: day.date,
        section_total_cost: day.day_total_cost,
        days: [day]
      };
      sections.push(currentSection);
    } else {
      currentSection.end_date = day.date;
      currentSection.section_total_cost += day.day_total_cost;
      currentSection.days.push(day);
    }
  });

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
        
        <div className="flex gap-3 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0">
          <Button variant="secondary" onClick={() => setIsShareModalOpen(true)} className="gap-2 shrink-0">
            <Share2 size={18} /> Share
          </Button>
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

      {sections.length === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 text-center border-dashed border-2 border-border-strong rounded-2xl bg-surface-muted/50">
          <Map className="text-text-muted/50 mb-4" size={48} />
          <h3 className="text-lg font-semibold text-text-primary">No sections added yet</h3>
          <p className="text-text-secondary mt-1 mb-6">Build your itinerary sections by adding travel stops.</p>
          <Button onClick={() => setIsAddStopModalOpen(true)}>+ Add First Section</Button>
        </Card>
      ) : (
        <div className="relative space-y-8 pb-4">
          {/* Continuous Line */}
          <div className="absolute left-[15px] sm:left-[23px] top-10 bottom-14 w-[2px] bg-border-strong -z-10" />
          
          {sections.map((section, index) => (
            <div key={section.stop_id} className="relative flex gap-4 sm:gap-6">
              {/* Timeline Dot Area */}
              <div className="relative flex-none w-8 sm:w-12 flex justify-center mt-10">
                <div className="w-3 h-3 rounded-full bg-primary ring-4 ring-surface shadow-sm z-10" />
              </div>
              
              {/* Card Area */}
              <div className="flex-1 min-w-0">
                <Card className="overflow-hidden border-border-default shadow-md">
                  
                  {/* Card Header */}
                  <div
                    className="relative p-5 sm:p-8 flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4 overflow-hidden rounded-t-xl"
                  >
                    {/* Absolute Background Image with Gradient Overlay */}
                    <img
                      src={getCityImage(section.city?.name, section.city?.image_url)}
                      alt={section.city?.name || 'Destination'}
                      className="absolute inset-0 w-full h-full object-cover"
                    />
                    <div className="absolute inset-0 bg-gradient-to-t from-black/90 via-black/50 to-black/20" />

                    {/* Header Content (Make text white to contrast with image overlay) */}
                    <div className="relative z-10 text-white">
                      <div className="flex items-center gap-3">
                        <h3 className="text-2xl font-bold font-manrope">
                          Section {index + 1}: {section.city?.name}
                        </h3>
                        <button onClick={() => handleDeleteStop(section.stop_id)} aria-label="Delete Section" className="text-white/60 hover:text-error transition-colors p-1" title="Delete Section"><Trash2 size={18} /></button>
                      </div>
                      <p className="text-sm font-medium text-white/80 mt-1">
                        Date Range: {new Date(section.start_date).toLocaleDateString()} to {new Date(section.end_date).toLocaleDateString()}
                      </p>
                    </div>

                    <div className="relative z-10 sm:text-right bg-black/30 backdrop-blur-md px-4 py-2 rounded-xl border border-white/10 shadow-sm">
                      <p className="text-xs font-semibold text-white/70 uppercase tracking-wider">Budget of this section</p>
                      <p className="text-lg font-bold text-white mt-0.5">${section.section_total_cost || "0.00"}</p>
                    </div>
                  </div>
                  
                  {/* Days inside the Section */}
                  <CardContent className="p-0">
                    <div className="divide-y divide-border-subtle">
                      {section.days.map((day) => (
                        <div key={day.date} className="p-5">
                          <div className="flex justify-between items-center mb-4">
                            <h4 className="text-sm font-bold text-text-primary uppercase tracking-wider">
                              {new Date(day.date).toLocaleDateString(undefined, { weekday: 'long', month: 'short', day: 'numeric' })}
                            </h4>
                            <button 
                              onClick={() => setActivityModalData({ isOpen: true, day })}
                              aria-label="Add Activity"
                              className="p-1.5 text-text-muted hover:text-primary hover:bg-primary-soft rounded-lg transition-colors"
                              title="Add Activity"
                            >
                              <Plus size={20} />
                            </button>
                          </div>
                          
                          <div className="space-y-2">
                            {day.activities && day.activities.length > 0 ? (
                              day.activities.map(act => (
                                <div key={act.id} className="flex items-center justify-between bg-surface-hover p-3 rounded-xl border border-border-subtle group">
                                  <div className="flex items-center gap-3">
                                    <Clock size={16} className="text-accent shrink-0" />
                                    <span className="text-text-primary font-medium">{act.activity?.name}</span>
                                  </div>
                                  <div className="flex items-center gap-4 shrink-0">
                                    <span className="text-text-secondary text-sm font-semibold">${act.effective_cost}</span>
                                    <button 
                                      onClick={() => handleDeleteActivity(section.stop_id, act.id)} 
                                      aria-label="Delete Activity"
                                      className="text-text-muted hover:text-error transition-colors opacity-0 group-hover:opacity-100 p-1"
                                      title="Delete Activity"
                                    >
                                      <Trash2 size={16} />
                                    </button>
                                  </div>
                                </div>
                              ))
                            ) : (
                              <div className="text-sm font-medium text-text-muted/70 bg-surface-muted/30 p-4 rounded-xl text-center">
                                Free time to explore
                              </div>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </CardContent>
                </Card>
              </div>
            </div>
          ))}
          
          <div className="relative flex gap-4 sm:gap-6 pt-4">
            <div className="relative flex-none w-8 sm:w-12 flex justify-center mt-6">
              <div className="w-3 h-3 rounded-full bg-border-strong ring-4 ring-surface z-10" />
            </div>
            <div className="flex-1 min-w-0">
              <Button onClick={() => setIsAddStopModalOpen(true)} className="w-full py-6 text-lg rounded-2xl border-2 border-dashed border-primary bg-primary-soft text-primary hover:bg-primary/10 hover:border-primary hover:text-primary-active transition-all">
                + Add another Section
              </Button>
            </div>
          </div>
        </div>
      )}

      <AddStopModal isOpen={isAddStopModalOpen} onClose={() => setIsAddStopModalOpen(false)} tripId={tripId} onStopAdded={fetchItinerary} />
      <AddActivityModal isOpen={activityModalData.isOpen} onClose={() => setActivityModalData({ isOpen: false, day: null })} tripId={tripId} selectedDay={activityModalData.day} onActivityAdded={fetchItinerary} />
      <ShareTripModal isOpen={isShareModalOpen} onClose={() => setIsShareModalOpen(false)} tripId={tripId} />
    </div>
  );
};