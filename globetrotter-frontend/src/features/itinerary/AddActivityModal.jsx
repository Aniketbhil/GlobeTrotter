import { useState, useEffect } from 'react';
import { Search, Clock, MapPin } from 'lucide-react';
import { Modal } from '../../components/ui/Modal';
import { Button } from '../../components/ui/Button';
import { Badge } from '../../components/ui/Badge';
import { getActivities, addTripActivity } from './itineraryApi';

export const AddActivityModal = ({ isOpen, onClose, tripId, selectedDay, onActivityAdded }) => {
  const [activities, setActivities] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [searchQuery, setSearchQuery] = useState("");
  const [globalError, setGlobalError] = useState("");
  const [addingId, setAddingId] = useState(null);

  useEffect(() => {
    if (isOpen && selectedDay?.city?.id) fetchActivities();
  }, [isOpen, selectedDay]);

  const fetchActivities = async () => {
    setIsLoading(true);
    setGlobalError("");
    try {
      const data = await getActivities(selectedDay.city.id, searchQuery);
      setActivities(data.items || []);
    } catch (error) {
      setGlobalError("Failed to load activities.");
    } finally {
      setIsLoading(false);
    }
  };

  const handleAddActivity = async (activityId) => {
    try {
      setAddingId(activityId);
      setGlobalError("");
      await addTripActivity(tripId, selectedDay.stop_id, {
        activity_id: activityId,
        scheduled_date: selectedDay.date,
      });
      onActivityAdded();
      onClose();
    } catch (error) {
      setGlobalError(error.response?.data?.detail?.[0]?.msg || "Failed to add activity.");
    } finally {
      setAddingId(null);
    }
  };

  return (
    <Modal isOpen={isOpen} onClose={onClose} title={`Add Activity to Section`}>
      <div className="space-y-4">
        <div className="flex gap-2">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-text-muted" size={18} />
            <input 
              type="text"
              placeholder="Search activities..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && fetchActivities()}
              className="h-10 w-full rounded-xl border border-border-strong bg-input-background pl-10 pr-3 text-sm text-text-primary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-border-focus"
            />
          </div>
          <Button onClick={fetchActivities} variant="secondary">Filter</Button>
        </div>

        {globalError && <div className="bg-error-soft text-error px-3 py-2 rounded-xl text-sm border border-error/20">{globalError}</div>}

        <div className="space-y-3 max-h-[50vh] overflow-y-auto pr-1">
          {isLoading ? (
            <div className="text-center text-text-muted py-8 animate-pulse">Searching activities...</div>
          ) : activities.length === 0 ? (
            <div className="text-center text-text-muted py-8 border border-dashed rounded-xl">
              No activities found in DB for this city. Please ask backend to add some!
            </div>
          ) : (
            activities.map(act => (
              <div key={act.id} className="flex gap-4 p-3 rounded-xl border border-border-default bg-background hover:bg-surface-hover transition-colors">
                <div className="w-20 h-20 bg-surface-muted rounded-lg shrink-0 overflow-hidden">
                  {act.image_url ? <img src={act.image_url} alt={act.name} className="w-full h-full object-cover" /> : <div className="w-full h-full flex items-center justify-center bg-primary-soft text-primary"><MapPin size={24} /></div>}
                </div>
                <div className="flex-1 min-w-0 flex flex-col justify-between">
                  <div>
                    <h4 className="font-semibold text-text-primary truncate">{act.name}</h4>
                    <div className="flex items-center gap-2 mt-1">
                      <Badge variant="primary">{act.type}</Badge>
                      <span className="text-xs text-text-muted flex items-center gap-1"><Clock size={12} /> {act.duration_mins} min</span>
                    </div>
                  </div>
                  <div className="flex justify-between items-center mt-2">
                    <span className="text-sm font-medium text-text-secondary">${act.cost}</span>
                    <Button size="sm" onClick={() => handleAddActivity(act.id)} isLoading={addingId === act.id}>Add</Button>
                  </div>
                </div>
              </div>
            ))
          )}
        </div>
      </div>
    </Modal>
  );
};