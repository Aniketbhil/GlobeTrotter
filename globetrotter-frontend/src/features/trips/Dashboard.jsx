import { useEffect, useState } from 'react';
import { Plus, MapPin, Calendar, ArrowRight } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Button } from '../../components/ui/Button';
import { Card, CardContent } from '../../components/ui/Card';
import { Badge } from '../../components/ui/Badge';
import { getGroupedTrips } from './tripsApi';
import { useAuthStore } from '../../store/authStore';

export const Dashboard = () => {
  const { user } = useAuthStore();
  const [groupedTrips, setGroupedTrips] = useState({ ongoing: [], upcoming: [], completed: [] });
  const [isLoading, setIsLoading] = useState(true);

  useEffect(() => {
    const fetchTrips = async () => {
      try {
        const data = await getGroupedTrips();
        setGroupedTrips(data);
      } catch (error) {
        console.error("Failed to load trips", error);
      } finally {
        setIsLoading(false);
      }
    };
    fetchTrips();
  }, []);

  const totalTrips = groupedTrips.ongoing.length + groupedTrips.upcoming.length + groupedTrips.completed.length;

  const TripCard = ({ trip }) => (
    <Card className="hover:border-primary/50 transition-colors group cursor-pointer">
      <div className="h-32 bg-surface-muted rounded-t-2xl relative overflow-hidden">
        {trip.cover_photo_url ? (
          <img src={trip.cover_photo_url} alt={trip.name} className="w-full h-full object-cover" />
        ) : (
          <div className="w-full h-full bg-linear-to-br from-primary-soft to-surface-hover mix-blend-multiply flex items-center justify-center">
            <MapPin className="text-primary opacity-50" size={32} />
          </div>
        )}
        <div className="absolute top-3 right-3">
          <Badge variant={trip.status === 'ongoing' ? 'warning' : trip.status === 'upcoming' ? 'primary' : 'success'}>
            {trip.status.charAt(0).toUpperCase() + trip.status.slice(1)}
          </Badge>
        </div>
      </div>
      <CardContent className="pt-4">
        <h3 className="font-manrope text-lg font-semibold text-text-primary truncate">{trip.name}</h3>
        <div className="flex items-center gap-2 mt-2 text-sm text-text-secondary">
          <Calendar size={14} />
          <span>{new Date(trip.start_date).toLocaleDateString()} - {new Date(trip.end_date).toLocaleDateString()}</span>
        </div>
      </CardContent>
    </Card>
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
        <Card className="flex flex-col items-center justify-center py-20 text-center border-dashed border-2">
          <div className="w-16 h-16 bg-primary-soft rounded-full flex items-center justify-center mb-4 text-primary">
            <MapPin size={32} />
          </div>
          <h3 className="text-xl font-semibold text-text-primary font-manrope">No trips planned yet</h3>
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
              <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6 opacity-75">
                {groupedTrips.completed.map(trip => <TripCard key={trip.id} trip={trip} />)}
              </div>
            </section>
          )}
        </div>
      )}
    </div>
  );
};