import { useEffect, useState } from 'react';
import { Plus, MapPin, Calendar, ArrowRight, Trash2 } from 'lucide-react';
import { Link, useNavigate } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { getGroupedTrips, deleteTrip } from './tripsApi';
import { useAuthStore } from '../../store/authStore';
import { getTripCoverImage } from '../../utils/imageResolver';

export const Dashboard = () => {
  const { user } = useAuthStore();
  const navigate = useNavigate();
  const [groupedTrips, setGroupedTrips] = useState({ ongoing: [], upcoming: [], completed: [] });
  const [isLoading, setIsLoading] = useState(true);

  const fetchTrips = async () => {
    setIsLoading(true);
    try {
      const data = await getGroupedTrips();
      setGroupedTrips(data);
    } catch (error) {
      console.error("Failed to load trips", error);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchTrips();
  }, []);

  const totalTrips = groupedTrips.ongoing.length + groupedTrips.upcoming.length + groupedTrips.completed.length;

  const handleDeleteTrip = async (e, tripId) => {
    e.preventDefault(); 
    e.stopPropagation();
    if (window.confirm("Are you sure you want to delete this trip?")) {
      try {
        await deleteTrip(tripId);
        fetchTrips(); // Refresh the dashboard after deletion
      } catch (error) {
        alert("Failed to delete trip.");
      }
    }
  };

  const TripCard = ({ trip }) => (
    <div 
      onClick={() => navigate(`/trips/${trip.id}/itinerary`)} 
      className="block h-full outline-none rounded-2xl cursor-pointer focus-visible:ring-2 focus-visible:ring-border-focus"
    >
      <Card className="hover:border-primary/50 hover:shadow-lg hover:-translate-y-1 transition-all duration-300 ease-in-out group h-full relative">
        <div className="h-32 bg-surface-muted rounded-t-2xl relative overflow-hidden">
          <img src={getTripCoverImage(trip.name, trip.cover_photo_url)} alt={trip.name} className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-500" />
          <div className="absolute top-3 left-3">
            <Badge className="shadow-sm backdrop-blur-sm" variant={trip.status === 'ongoing' ? 'warning' : trip.status === 'upcoming' ? 'primary' : 'success'}>
              {trip.status.charAt(0).toUpperCase() + trip.status.slice(1)}
            </Badge>
          </div>
          
          {/* Delete Button */}
          <button 
            onClick={(e) => handleDeleteTrip(e, trip.id)}
            aria-label="Delete Trip"
            className="absolute top-3 right-3 p-1.5 bg-surface/80 hover:bg-error hover:text-white text-error rounded-lg backdrop-blur-sm transition-colors opacity-0 group-hover:opacity-100"
            title="Delete Trip"
          >
            <Trash2 size={16} />
          </button>
        </div>
        <CardContent className="pt-4">
          <h3 className="font-manrope text-lg font-semibold text-text-primary truncate">{trip.name}</h3>
          <div className="flex items-center gap-2 mt-2 text-sm text-text-secondary">
            <Calendar size={14} />
            <span>{new Date(trip.start_date).toLocaleDateString()} - {new Date(trip.end_date).toLocaleDateString()}</span>
          </div>
        </CardContent>
      </Card>
    </div>
  );

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold font-manrope text-text-primary">
            {user ? `Hello, ${user.first_name}!` : 'Welcome back!'}
          </h1>
          <p className="text-text-secondary mt-1">Here is the latest overview of your travel plans.</p>
        </div>
        <Link to="/trips/new">
          <Button className="gap-2">
            <Plus size={18} />
            Plan New Trip
          </Button>
        </Link>
      </div>

      {isLoading ? (
        <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
          {[1, 2, 3].map(i => (
             <Card key={i} className="h-57.5 animate-pulse bg-surface-muted border-none" />
          ))}
        </div>
      ) : totalTrips === 0 ? (
        <Card className="flex flex-col items-center justify-center py-16 text-center border-dashed border-2 border-border-strong rounded-2xl bg-surface-muted/50">
          <MapPin className="text-text-muted/50 mb-4" size={48} />
          <h3 className="text-lg font-semibold text-text-primary font-manrope">No trips planned yet</h3>
          <p className="text-text-secondary max-w-sm mt-2 mb-6">
            The world is waiting for you. Start building your personalized multi-city itinerary today.
          </p>
          <Link to="/trips/new">
            <Button className="gap-2">
              Start Planning <ArrowRight size={18} />
            </Button>
          </Link>
        </Card>
      ) : (
        <div className="space-y-8">
          {groupedTrips.ongoing.length > 0 && (
            <section>
              <h2 className="text-xl font-semibold font-manrope text-text-primary mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-warning inline-block"></span>
                Ongoing Trips
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {groupedTrips.ongoing.map(trip => <TripCard key={trip.id} trip={trip} />)}
              </div>
            </section>
          )}

          {groupedTrips.upcoming.length > 0 && (
            <section>
              <h2 className="text-xl font-semibold font-manrope text-text-primary mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-primary inline-block"></span>
                Upcoming Trips
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                {groupedTrips.upcoming.map(trip => <TripCard key={trip.id} trip={trip} />)}
              </div>
            </section>
          )}
          
          {groupedTrips.completed.length > 0 && (
            <section>
              <h2 className="text-xl font-semibold font-manrope text-text-primary mb-4 flex items-center gap-2">
                <span className="w-2 h-2 rounded-full bg-success inline-block"></span>
                Completed Trips
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 opacity-75 hover:opacity-100 transition-opacity">
                {groupedTrips.completed.map(trip => <TripCard key={trip.id} trip={trip} />)}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
};